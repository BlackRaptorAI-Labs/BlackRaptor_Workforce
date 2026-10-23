#!/usr/bin/env python3
"""PreToolUse hook: block modifications to Tier-3 protected paths.

Fail-closed enforcement of the Tier-3 boundary for ALL Claude Code sessions
and subagents in this repo. Prompts instruct agents not to touch these paths;
this hook stops the common ways of touching them, with a clear message.

EARLY WARNING, NOT THE LOCK (D-223, 2.8.3). The Bash checks below read command
text, and a command can always be written in a form they miss (`python3 -c`,
`node -e`, `install`, `ln -sf`; audit 5 K2). What keeps every agent's shell off
the enforcement files is Claude Code's sandbox: /workforce-init turns it on with
failIfUnavailable, no unsandboxed commands, and a denyWrite entry for each
enforcement file outside the .claude folders the sandbox already protects. This
hook stays to catch honest mistakes early; without the sandbox, an agent with a
shell can edit these files.

Coverage:
  - Edit/Write/MultiEdit/NotebookEdit: blocked on protected paths. Paths are
    matched case-insensitively (macOS/Windows default filesystems are
    case-insensitive) and with symlinks resolved (realpath).
  - Bash: heuristic — blocked when the command references a protected path AND
    contains a write-shaped operation (redirect, sed -i, tee, mv, cp, rm, git
    checkout/restore/apply, patch, chmod, dd, truncate). Reads (cat/grep/ls)
    pass, including reads with 2>&1 or a redirect to /dev/null. This catches
    accidents, not determined adversaries.
  - Malformed input or a missing file path on an edit tool: BLOCKED (fail
    closed). If a Claude Code update changes the hook payload shape, edits to
    anything will be blocked until this hook is updated — that is deliberate.
  - The guard guards itself: .claude/settings.json and .claude/hooks/ are on
    the protected list.
  - Bash, live systems (2.8.2): blocked when a program position in the command
    holds a cloud, infrastructure, deploy, remote-access or remote-database tool
    (LIVE_TOOLS below), after splitting on ; && || | & ( ) newlines, $(...) and
    backticks, and looking through env, sudo, sh -c / bash -c, eval, xargs,
    npx and absolute paths. A read of a path (ls ~/.aws) is not the tool and
    passes. The human runs such commands, or starts the session with
    BR_ALLOW_LIVE=1 (logged). Read-only exceptions for a repo go in
    .claude/live-commands-allow.txt, one Python regular expression per line,
    each matched against one whole simple command; that file is Tier-3.
  - Bash, publish and data out (2.8.2 amendment): the same check blocks gh
    pr merge / release / repo delete|edit / secret / variable and non-GET gh
    api, a forcing or deleting git push, npm/yarn/pnpm publish, twine upload,
    cargo publish, gem push, docker push/login, nc/ncat to a remote host, and
    curl/wget/httpie sending data or a POST/PUT/PATCH/DELETE to a host that
    is not local. A database URL naming localhost (or no host) is local.
  - Bash, forms that hide the program (2.8.2, audit 2 F4, D-178): an alias
    defined on the same line (`alias k=kubectl; k get pods`) is expanded
    before the check; a function body defined on the line is checked as
    commands; any pipe into sh, bash, zsh, dash or ksh (`| sh`, `| bash -s`,
    `base64 -d | sh`) and a shell or `source` reading `<(...)` are blocked,
    since the hook cannot read the text the shell runs; a heredoc whose
    consuming command is a shell has its body checked as commands; `curl -K`
    or `--config` is blocked (the config file can hold the URL and upload);
    `python -c` / `node -e` text is checked, BEST EFFORT, for a live tool run
    through subprocess / child_process, or a network call (urllib,
    http.client, requests, httpx, socket, fetch, http(s).request, axios) to a
    host literal that is not local.

Known gaps (the hook reads one command line's text, nothing more). It does
NOT see, and so permits:
  - repo scripts: `sh deploy.sh`, `./deploy.sh`, `bash deploy.sh` run what
    the file says;
  - Makefile targets: `make rollout` runs what the Makefile says;
  - copied or renamed binaries: `cp $(command -v aws) ./a && ./a s3 ls`, or a
    symlink to a new name;
  - PATH shadowing: a local directory put first on PATH with a wrapper named
    like a harmless program;
  - flags held in variables: `F=-T; curl $F file https://...`, or
    `D='-d @.env'; curl $D https://...`;
  - hosts from environment variables: `psql "$DATABASE_URL"`, a URL in `$X`
    (a send to a host the hook cannot see is blocked; a read is not);
  - interpreters running files: `python3 dbq.py`, `node tool.js`, `sh < x`,
    and interpreter one-liners that build the command or host at run time;
  - an alias defined inside `sh -c` (`sh -c 'alias k=kubectl; k get pods'`):
    aliases are expanded on the outer line only.
  Not live by design, and permitted: reads of credential files (`cat
  ~/.aws/credentials`), package installs (`pip install <url>`, `npx <pkg>`),
  and a curl or wget GET.
The boundary for these is a sandbox network allowlist, not this hook.

Boundary of record: this hook is IN-SESSION accident-prevention and is
bypassable by construction (especially the Bash heuristic). The enforcement of
record for Tier 3 is SERVER-SIDE — branch protection (the owner's approval) + the
change-record-required CI check. Do not rely on this hook as the only control.

Contract (Claude Code hooks):
  stdin  = JSON: { tool_name, tool_input: {...}, cwd, ... }
  exit 0 = allow · exit 2 = block; stderr is fed back to Claude as the reason

Intentional Tier-3 work: run with  BR_ALLOW_TIER3=1 claude
(The old ALLOW_TIER3=1 alias was removed in 2.8.0.)
A live-system command the human wants an agent to run: BR_ALLOW_LIVE=1 claude
(BR_ALLOW_TIER3 does not open live commands, and BR_ALLOW_LIVE does not open Tier-3 paths.)
Blocked attempts and overrides are logged to .claude/hooks/tier3-attempts.log.
"""
import json
import os
import re
import shlex
import sys
from urllib.parse import urlsplit
from datetime import datetime, timezone

# CUSTOMIZE: your Tier-3 paths. Keep this list in sync with the GATED list in
# .github/workflows/change-record-required.yml.
# The first three entries protect the enforcement mechanism itself — keep them.
TIER3_PREFIXES = [
    ".github/",
    ".claude/hooks/",
    ".claude/agents/",
    ".claude/commands/",
    ".claude/skills/",
    # "src/auth/",                # e.g. authentication / authorization
    # "db/migrations/",           # e.g. schema & migrations
    # "src/remote-exec/",         # e.g. anything that runs commands remotely
]
TIER3_FILES = [
    ".claude/settings.json",
    ".claude/live-commands-allow.txt",   # the human's live-command exceptions; agents never edit it
    ".claude/gates-allow.txt",           # the project's own gate slugs (D-192); an agent listing itself would sign verdicts
    ".claude/test-summary-patterns.txt", # the project's test-summary readers (D-216); an agent adding one could fake a green run
    # "src/lib/audit.ts",         # e.g. your audit-trail writer
]
REPO_MARKER = ""  # set at runtime from the project directory name (see main)
WRITE_CMD = re.compile(
    r"(>>?|\bsed\b[^|;&]*\s-i|\btee\b|\bmv\b|\bcp\b|\brm\b|\btouch\b"
    r"|\bgit\s+(apply|checkout|restore)\b|\bpatch\b|\bchmod\b|\bdd\b|\btruncate\b)"
)
# Redirects that write no file (D-161): fd duplications such as 2>&1, >&2, 1>&- and redirects to
# /dev/null. They are removed from a copy of the command before WRITE_CMD is tested; the Tier-3 path
# match still runs on the full command. The lookahead keeps `>&2x` (a write to file "2x") a write.
NO_WRITE_REDIRECT = re.compile(r"[0-9]*(>&[0-9-]+|>>?\s*/dev/null)(?=$|[\s;|&)<>])")

# ---- live systems (2.8.2, D-169) -------------------------------------------------------------
# A program here reaches a cloud account, a cluster, a deploy target, a remote host or a remote
# database. None means "always"; a set means "only with one of these subcommands" (the first
# argument that is not an option); a function decides from the arguments.
LIVE_ALLOW_FILE = ".claude/live-commands-allow.txt"
LIVE_MESSAGE = ("This command reaches a live system. Agents do not run it. If the human wants it run, "
                "they run it themselves, or allow it for this session with BR_ALLOW_LIVE=1 (logged).")
PUBLISH_MESSAGE = "This command publishes or sends data out. Agents do not run it."
OVERRIDE_SENTENCE = ("If the human wants it run, they run it themselves, or allow it for this session with "
                     "BR_ALLOW_LIVE=1 (logged).")
PIPED_MESSAGE = ("This command feeds text to a shell through a pipe or a substitution, so the hook cannot read "
                 "what it runs. Agents do not run it.")
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0", ""}
URL = re.compile(r"^[a-z][a-z0-9+.-]*://", re.I)
REMOTE_PATH = re.compile(r"^(rsync://|([^/\s:@]+@)?[A-Za-z0-9][A-Za-z0-9.-]*::?[^:]*$)")


def _subcommand_in(args, names):
    """True when one of the first two non-option arguments is in names (an option such as
    `-C dir` can push the subcommand to second place)."""
    return any(a in names for a in [x for x in args if not x.startswith("-")][:2])


def _url_host(url):
    """The host a URL names, lowercased; "" when it names none. An unparseable URL counts as remote."""
    try:
        return (urlsplit(url).hostname or "").lower()
    except ValueError:
        return "unparseable"


def _git_push_destructive(args):
    """`git push` that forces or deletes: --force, -f, --force-with-lease, --delete/-d, --mirror,
    a `+refspec` (a forced update) or a `:refspec` (a deletion). Other git commands are not live."""
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in ("-C", "-c") else 1
    if i >= len(args) or args[i] != "push":
        return False
    for a in args[i + 1:]:
        if a in ("--force", "--delete", "--mirror") or a.startswith("--force-with-lease") or a.startswith("--force-if-includes"):
            return True
        if a.startswith("-") and not a.startswith("--") and ("f" in a[1:] or "d" in a[1:]):
            return True
        if not a.startswith("-") and (a.startswith(":") or a.startswith("+")):
            return True
    return False


GH_VALUE_OPTS = {"-R", "--repo", "-X", "--method", "-f", "-F", "--field", "--raw-field", "-H", "--header",
                 "--input", "-q", "--jq", "-t", "--template", "--hostname"}


def _gh_writes(args):
    """gh subcommands that change or publish: pr merge, release, repo delete/edit, secret, variable, and
    `gh api` with a method other than GET (or with fields or --input, which make gh send a POST)."""
    pos, i = [], 0
    while i < len(args):
        a = args[i]
        if a in GH_VALUE_OPTS:
            i += 2
            continue
        if not a.startswith("-"):
            pos.append(a)
        i += 1
    if not pos:
        return False
    if pos[0] in ("release", "secret", "variable"):
        return True
    if pos[0] == "pr" and pos[1:2] == ["merge"]:
        return True
    if pos[0] == "repo" and pos[1:2] and pos[1] in ("delete", "edit"):
        return True
    if pos[0] == "api":
        for j, a in enumerate(args):
            m = None
            if a in ("-X", "--method") and j + 1 < len(args):
                m = args[j + 1]
            elif a.startswith("--method="):
                m = a.split("=", 1)[1]
            elif a.startswith("-X") and len(a) > 2:
                m = a[2:]
            if m is not None and m.upper() != "GET":
                return True
            if a in ("-f", "-F", "--field", "--raw-field", "--input") or a.startswith(("--field=", "--raw-field=", "--input=")):
                return True
    return False


SEND_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
HTTP_VALUE_OPTS = {"-d", "-F", "-T", "-X", "-H", "-o", "-u", "-A", "-e", "-b", "-c", "-K", "-w", "-x", "-m", "-r",
                   "-E", "-U", "-O", "--data", "--data-raw", "--data-binary", "--data-urlencode", "--data-ascii",
                   "--form", "--form-string", "--upload-file", "--request", "--header", "--output", "--user",
                   "--user-agent", "--referer", "--cookie", "--cookie-jar", "--config", "--write-out", "--proxy",
                   "--max-time", "--connect-timeout", "--retry", "--cert", "--key", "--post-data", "--post-file",
                   "--method", "--body-data", "--body-file", "--output-document", "-P", "--directory-prefix"}
HOSTISH = re.compile(r"^(\[[0-9a-fA-F:]+\]|[A-Za-z0-9.-]+)(:\d+)?(/.*)?$")


def _http_sends(prog, args):
    """True when the command carries an upload or method flag (or, for httpie, a POST/PUT/PATCH/DELETE
    method word) and a target that is not local; a send whose target the hook cannot see is not local."""
    sends, targets, i = False, [], 0
    while i < len(args):
        a = args[i]
        nxt = args[i + 1] if i + 1 < len(args) else ""
        if a in ("-d", "-F", "-T") or (a[:2] in ("-d", "-F", "-T") and not a.startswith("--") and len(a) > 2) \
                or a.startswith(("--data", "--form", "--upload-file", "--post-data", "--post-file", "--method",
                                 "--body-data", "--body-file")):
            sends = True
        if a in ("-X", "--request") and nxt.upper() in SEND_METHODS:
            sends = True
        if (a.startswith("-X") and len(a) > 2 and a[2:].upper() in SEND_METHODS) or \
                (a.startswith("--request=") and a.split("=", 1)[1].upper() in SEND_METHODS):
            sends = True
        if a in HTTP_VALUE_OPTS:
            i += 2
            continue
        if not a.startswith("-"):
            if prog in ("http", "https", "httpie") and a.upper() in SEND_METHODS:
                sends = True
            elif URL.match(a):
                targets.append(_url_host(a))
            elif HOSTISH.match(a) and ("." in a.split("/")[0] or a.split("/")[0].split(":")[0] in LOCAL_HOSTS):
                targets.append(a.split("/")[0].rsplit(":", 1)[0].strip("[]").lower())
        i += 1
    if not sends:
        return False
    return not targets or any(t not in LOCAL_HOSTS for t in targets)


def _curl_config(args):
    """`curl -K FILE` / `--config FILE`: the config can hold the URL and an upload the hook cannot read."""
    return any(a in ("-K", "--config") or a.startswith("--config=")
               or (a.startswith("-") and not a.startswith("--") and "K" in a[1:]) for a in args)


INTERPRETER = re.compile(r"^(python[0-9.]*|node|nodejs)$")
NET_CALL = re.compile(r"urllib|http\.client|\brequests\b|\bhttpx\b|\baiohttp\b|\bsocket\b|\bfetch\s*\("
                      r"|\bhttps?\.request\b|\baxios\b|require\(\s*['\"]https?['\"]\s*\)|\bnet\.connect\b")
SUB_CALL = re.compile(r"\bsubprocess\b|\bos\.(system|popen|exec\w*|spawn\w*)\b|\bpty\.spawn\b|child_process"
                      r"|\bexecSync\b|\bspawnSync\b|\bexecFileSync\b")
HOST_LITERAL = re.compile(r"[a-z][a-z0-9+.-]*://\[?([^/'\"\s:\]]+)", re.I)
STRING_LIT = re.compile(r"(['\"])((?:\\.|(?!\1).)*)\1")


def _interp_text(prog, args):
    """The code text of `python -c CODE` or `node -e|--eval|-p|--print CODE`, or None."""
    flags = ("-c",) if prog.startswith("python") else ("-e", "--eval", "-p", "--print")
    for i, a in enumerate(args):
        if a in flags and i + 1 < len(args):
            return args[i + 1]
        if prog.startswith("python") and a.startswith("-") and not a.startswith("--") and a.endswith("c") and i + 1 < len(args):
            return args[i + 1]
        if a.startswith(("--eval=", "--print=")):
            return a.split("=", 1)[1]
    return None


def interpreter_hit(prog, text, depth=0):
    """BEST EFFORT (D-178): what an interpreter one-liner reaches, as a label: '<tool> via <prog>' when
    subprocess / child_process text carries a live command in its string literals; '<prog> to <host>'
    when a network call or a subprocess names a host literal that is not local; None otherwise."""
    if not text:
        return None
    remote = [h.lower() for h in HOST_LITERAL.findall(text) if h.lower() not in LOCAL_HOSTS]
    if SUB_CALL.search(text):
        lits = [m.group(2) for m in STRING_LIT.finditer(text)]
        cands = list(lits)
        for lst in re.findall(r"\[([^\]]*)\]", text):
            words = [m.group(2) for m in STRING_LIT.finditer(lst)]
            if words:
                cands.append(" ".join(shlex.quote(w) for w in words))
        for c in cands:
            for seg in _split_commands(c):
                hit = live_program(seg, depth + 1)
                if hit:
                    return "%s via %s" % (hit, prog)
        if remote:
            return "%s to %s" % (prog, remote[0])
    if NET_CALL.search(text) and remote:
        return "%s to %s" % (prog, remote[0])
    return None


def _nc_remote(args):
    """nc/ncat to a host that is not local (a raw socket can send anything); listening (-l) is local."""
    if any(a == "-l" or (a.startswith("-") and not a.startswith("--") and "l" in a[1:]) or a == "--listen" for a in args):
        return False
    hosts = [a for a in args if not a.startswith("-") and not a.isdigit()]
    return bool(hosts) and any(h.lower() not in LOCAL_HOSTS for h in hosts[:1])


def _db_remote(args, host_flags, url_flags=()):
    """True when a database client is given a non-local host, or a connection URL whose host is not
    local (2.8.2 amendment: a URL naming localhost, 127.0.0.1, ::1 or no host is local). A URL held in a
    variable (`psql "$DATABASE_URL"`) is not seen: the hook gets the text before the shell expands it."""
    for i, a in enumerate(args):
        v = a.split("=", 1)[1] if a.startswith("--") and "=" in a else a
        if URL.match(v):
            if _url_host(v) not in LOCAL_HOSTS:
                return True
            continue
        m = re.search(r"(?:^|\s)host=(\S+)", a)   # libpq conninfo string
        if m and m.group(1).strip("'\"") not in LOCAL_HOSTS:
            return True
        for f in list(host_flags) + list(url_flags):
            val = None
            if a == f and i + 1 < len(args):
                val = args[i + 1]
            elif f.startswith("--") and a.startswith(f + "="):
                val = a[len(f) + 1:]
            elif not f.startswith("--") and not a.startswith("--") and a.startswith(f) and len(a) > len(f):
                val = a[len(f):]
            if val is None:
                continue
            if f in url_flags or URL.match(val):
                if not URL.match(val) or _url_host(val) not in LOCAL_HOSTS:
                    return True
                continue
            host = val if val.count(":") > 1 else val.split(":")[0]   # drop a port, keep ::1
            if host not in LOCAL_HOSTS and not host.startswith("/"):  # a socket directory is local
                return True
    return False


LIVE_TOOLS = {
    "aws": None, "gcloud": None, "gsutil": None, "bq": None, "az": None, "kubectl": None,
    "helm": None, "flyctl": None, "fly": None, "heroku": None, "ssh": None, "scp": None, "sftp": None,
    "terraform": {"apply", "destroy", "import", "state"},
    "tofu": {"apply", "destroy", "import", "state"},
    "pulumi": {"up", "destroy"},
    "cdk": {"deploy", "destroy"},
    "serverless": {"deploy"}, "sls": {"deploy"},
    "vercel": lambda args: any(a == "--prod" or a.startswith("--prod=") for a in args),
    "rsync": lambda args: any(not a.startswith("-") and REMOTE_PATH.match(a) for a in args),
    "psql": lambda args: _db_remote(args, ["-h", "--host"]),
    "mysql": lambda args: _db_remote(args, ["-h", "--host"]),
    "mongosh": lambda args: _db_remote(args, ["--host"]),
    "redis-cli": lambda args: _db_remote(args, ["-h"], ["-u"]),
    # publish and data out (2.8.2 amendment, D-169): the PUBLISH_MESSAGE group
    "gh": _gh_writes,
    "git": _git_push_destructive,
    "npm": {"publish"}, "yarn": {"publish"}, "pnpm": {"publish"},
    "twine": {"upload"}, "cargo": {"publish"}, "gem": {"push"}, "docker": {"push", "login"},
    "curl": lambda args: _curl_config(args) or _http_sends("curl", args), "wget": lambda args: _http_sends("wget", args),
    "http": lambda args: _http_sends("http", args), "https": lambda args: _http_sends("http", args),
    "httpie": lambda args: _http_sends("http", args),
    "nc": _nc_remote, "ncat": _nc_remote,
}
PUBLISH_TOOLS = {"gh", "git", "npm", "yarn", "pnpm", "twine", "cargo", "gem", "docker", "curl", "wget", "http",
                 "https", "httpie", "nc", "ncat"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
RESERVED = {"{", "}", "!", "if", "then", "do", "else", "elif", "while", "until", "time", "fi", "done"}
# wrappers that run the rest of the line: name -> options that take a value
WRAPPERS = {"sudo": {"-u", "-g", "-C", "-p", "-r", "-t", "-U", "-D", "-h"}, "nohup": set(), "exec": {"-a"},
            "nice": {"-n"}, "timeout": {"-s", "-k"}, "stdbuf": {"-i", "-o", "-e"}, "builtin": set(),
            "xargs": {"-I", "-n", "-P", "-L", "-d", "-E", "-s", "-a"}, "npx": {"-p", "--package"},
            "bunx": {"-p", "--package"}, "caffeinate": set(), "doas": {"-u"}}


HEREDOC = re.compile(r"(?<!<)<<(?!<)-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
SUBST = re.compile(r"\$\([^)]*\)|`[^`]*`")


def head_program(segment):
    """(program, rest) of a simple command after assignments, env, `command` and wrappers; (None, [])."""
    args = _argv(segment)
    while args:
        a = args[0]
        if a in RESERVED or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", a):
            args = args[1:]
            continue
        prog = os.path.basename(a.lstrip("\\")).lower()
        rest = args[1:]
        if prog == "env":
            while rest and (rest[0].startswith("-") or "=" in rest[0]):
                rest = rest[2:] if rest[0] in ("-u", "--unset", "-C", "--chdir") else rest[1:]
            args = rest
            continue
        if prog == "command" and rest[:1] not in (["-v"], ["-V"]):
            args = rest[1:] if rest[:1] == ["-p"] else rest
            continue
        if prog in WRAPPERS:
            takes = WRAPPERS[prog]
            while rest and rest[0].startswith("-"):
                rest = rest[2:] if rest[0] in takes else rest[1:]
            if prog == "timeout" and rest:
                rest = rest[1:]
            args = rest
            continue
        return prog, rest
    return None, []


def _shell_reads_stdin(prog, rest):
    """A shell that runs the text on its standard input: no -c, and no script file argument."""
    if prog not in SHELLS:
        return False
    i = 0
    while i < len(rest) and rest[i][:1] in ("-", "+"):
        if rest[i][:1] == "-" and not rest[i].startswith("--") and "c" in rest[i][1:]:
            return False
        i += 2 if rest[i] in ("-o", "+o", "-O", "+O", "--rcfile", "--init-file") else 1
    return i >= len(rest) or any(r == "-s" or (r.startswith("-") and "s" in r[1:]) for r in rest[:i])


def _consumer(line, start):
    """The program of the simple command a heredoc opened at `start` of `line` feeds."""
    return head_program(re.split(r"[;&|(]", line[:start])[-1])


def _strip_heredocs(cmd):
    """Drop heredoc bodies (they are data), keeping any $(...) or backtick in an unquoted one. A body
    whose consuming command is a shell (`sh <<EOF`, `bash -s <<EOF`) is commands, not data: it is kept
    (D-178)."""
    out, pending = [], []
    for line in cmd.split("\n"):
        if pending:
            delim, quoted, keep = pending[0]
            if line.strip() == delim:
                pending.pop(0)
            elif keep:
                out.append(line)
            elif not quoted:
                out.extend(SUBST.findall(line))
            continue
        out.append(line)
        for m in HEREDOC.finditer(line):
            prog, rest = _consumer(line, m.start())
            pending.append((m.group(2), bool(m.group(1)), bool(prog) and _shell_reads_stdin(prog, rest)))
    return "\n".join(out)


def heredoc_interpreter_bodies(cmd):
    """[(program, body)] for each heredoc fed to python or node (`python3 - <<EOF`), BEST EFFORT."""
    out, pending = [], []
    for line in cmd.split("\n"):
        if pending:
            if line.strip() == pending[0][0]:
                delim, prog, body = pending.pop(0)
                if prog:
                    out.append((prog, "\n".join(body)))
            else:
                pending[0][2].append(line)
            continue
        for m in HEREDOC.finditer(line):
            prog, _rest = _consumer(line, m.start())
            pending.append((m.group(2), prog if prog and INTERPRETER.match(prog) else None, []))
    return out


def pipeline_parts(cmd):
    """[(simple command, operator before it)] at the top level of a line; quotes respected."""
    parts, buf, op, i, q, n = [], [], "", 0, None, len(cmd)
    while i < n:
        c = cmd[i]
        if q:
            buf.append(c)
            if c == q:
                q = None
            elif c == "\\" and q == '"' and i + 1 < n:
                buf.append(cmd[i + 1]); i += 1
            i += 1
            continue
        if c in "'\"":
            q = c; buf.append(c); i += 1; continue
        if c == "\\" and i + 1 < n:
            buf.append(cmd[i:i + 2]); i += 2; continue
        if c in ";|&\n":
            two = cmd[i:i + 2]
            nxt = two if two in ("||", "&&", "|&", ";;") else c
            parts.append(("".join(buf).strip(), op)); buf = []
            op = nxt; i += len(nxt); continue
        buf.append(c); i += 1
    parts.append(("".join(buf).strip(), op))
    return [(s, o) for s, o in parts if s]


def piped_shell_hits(cmd):
    """Shells fed text the hook cannot read (D-178): a pipe into sh/bash/zsh/dash/ksh, or a shell or
    `source` reading a process substitution."""
    hits = []
    for seg, op in pipeline_parts(_strip_heredocs(cmd)):
        prog, rest = head_program(seg)
        if op in ("|", "|&") and prog and _shell_reads_stdin(prog, rest):
            hits.append((seg, "%s (piped)" % prog))
    for m in re.finditer(r"(?:^|[\s;&|(])((?:sh|bash|zsh|dash|ksh|source|\.))\s+(?:-\S+\s+)*<\(", cmd):
        hits.append((m.group(0).strip(), "%s (piped)" % m.group(1)))
    return hits


def alias_expanded(segments):
    """Segments with every alias defined earlier on the same line expanded (D-178)."""
    aliases, out = {}, []
    for seg in segments:
        args = _argv(seg)
        if args[:1] == ["alias"]:
            for a in args[1:]:
                if "=" in a:
                    k, v = a.split("=", 1)
                    aliases[k] = v
            continue
        if args and args[0] in aliases:
            out.append(aliases[args[0]] + " " + " ".join(shlex.quote(x) for x in args[1:]))
        out.append(seg)
    return out


def _split_commands(cmd):
    """The simple commands in a shell line, plus the text of every $(...) and backtick inside it
    (those run too, even inside double quotes). Single quotes hide everything."""
    out, buf, i, q, n = [], [], 0, None, len(cmd)

    def flush():
        s = "".join(buf).strip()
        if s:
            out.append(s)
        del buf[:]

    while i < n:
        c = cmd[i]
        if q == "'":
            buf.append(c)
            q = None if c == "'" else q
            i += 1
            continue
        if c == "\\" and i + 1 < n:
            buf.append(cmd[i:i + 2]); i += 2; continue
        if c == "$" and cmd[i + 1:i + 2] == "(":
            depth, j = 1, i + 2
            while j < n and depth:
                depth += {"(": 1, ")": -1}.get(cmd[j], 0)
                j += 1
            out.extend(_split_commands(cmd[i + 2:j - 1]))
            buf.append("SUBST"); i = j; continue
        if c == "`":
            j = cmd.find("`", i + 1)
            j = n if j < 0 else j
            out.extend(_split_commands(cmd[i + 1:j]))
            buf.append("SUBST"); i = j + 1; continue
        if c == '"':
            q = None if q == '"' else '"'
            buf.append(c); i += 1; continue
        if q is None and c == "'":
            q = "'"; buf.append(c); i += 1; continue
        if q is None and c in ";|&()\n":
            flush(); i += 1; continue
        buf.append(c); i += 1
    flush()
    return out


def _argv(segment):
    try:
        return shlex.split(segment, comments=False, posix=True)
    except ValueError:
        return segment.split()


def live_program(segment, depth=0):
    """The live tool a simple command runs, or None. Looks through assignments, env, sudo and other
    wrappers, `sh -c`, `eval` and absolute paths."""
    if depth > 5:
        return None
    args = _argv(segment)
    while args:
        a = args[0]
        if a in RESERVED or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", a):
            args = args[1:]
            continue
        prog = os.path.basename(a.lstrip("\\")).lower()
        rest = args[1:]
        if prog == "env":
            while rest and (rest[0].startswith("-") or "=" in rest[0]):
                if rest[0] in ("-u", "--unset", "-C", "--chdir"):
                    rest = rest[1:]
                elif rest[0] in ("-S", "--split-string") and len(rest) > 1:
                    return live_program(rest[1], depth + 1)
                rest = rest[1:]
            args = rest
            continue
        if prog == "command":
            if rest[:1] in (["-v"], ["-V"]):
                return None   # a lookup, not a run
            args = rest[1:] if rest[:1] == ["-p"] else rest
            continue
        if prog in ("pnpm", "yarn", "npm") and rest[:1] and rest[0] in ("dlx", "exec", "x"):
            rest = rest[1:]
            while rest and rest[0].startswith("-"):
                rest = rest[1:]
            args = rest
            continue
        if prog in WRAPPERS:
            takes = WRAPPERS[prog]
            while rest and rest[0].startswith("-"):
                rest = rest[2:] if rest[0] in takes else rest[1:]
            if prog == "timeout" and rest:
                rest = rest[1:]   # the duration
            args = rest
            continue
        if prog in SHELLS:
            i = 0
            while i < len(rest) and rest[i][:1] in ("-", "+"):
                if rest[i] in ("-o", "+o", "-O", "+O", "--rcfile", "--init-file"):
                    i += 2
                    continue
                if rest[i][:1] == "-" and not rest[i].startswith("--") and "c" in rest[i][1:]:
                    if i + 1 < len(rest):
                        for inner in _split_commands(rest[i + 1]):
                            hit = live_program(inner, depth + 1)
                            if hit:
                                return hit
                    return None
                i += 1
            return None
        if prog == "eval":
            for inner in _split_commands(" ".join(rest)):
                hit = live_program(inner, depth + 1)
                if hit:
                    return hit
            return None
        if INTERPRETER.match(prog):
            return interpreter_hit(prog, _interp_text(prog, rest), depth)
        rule = LIVE_TOOLS.get(prog, False)
        if rule is False:
            return None
        if rule is None:
            return prog
        if isinstance(rule, set):
            return prog if _subcommand_in(rest, rule) else None
        return prog if rule(rest) else None
    return None


def live_allow_patterns(project_dir):
    pats = []
    try:
        with open(os.path.join(project_dir, LIVE_ALLOW_FILE), encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    pats.append(re.compile(line))
                except re.error:
                    pass   # a broken line allows nothing
    except OSError:
        pass
    return pats


def live_hits(cmd, project_dir):
    """[(simple command, tool)] for every live command not covered by an allow-list line, and the
    list of simple commands an allow-list line permitted."""
    pats = live_allow_patterns(project_dir)
    hits, allowed = [], []
    found = [(seg, live_program(seg)) for seg in alias_expanded(_split_commands(_strip_heredocs(cmd)))]
    found += piped_shell_hits(cmd)
    for prog, body in heredoc_interpreter_bodies(cmd):
        hit = interpreter_hit(prog, body)
        if hit:
            found.append(("%s <<heredoc" % prog, hit))
    for seg, tool in found:
        if not tool:
            continue
        if any(p.fullmatch(seg) for p in pats):
            allowed.append(seg)
        else:
            hits.append((seg, tool))
    return hits, allowed

# Lowercased views for case-insensitive matching. macOS and Windows default
# filesystems are case-insensitive, so a case variant (e.g. .GitHub/) must not
# slip past the guard. Recomputed from the lists above.
_TIER3_FILES_LC = {f.lower() for f in TIER3_FILES}
_TIER3_PREFIXES_LC = tuple(p.lower() for p in TIER3_PREFIXES)


def match(rel: str) -> bool:
    r = rel.lower()  # case-insensitive; see _TIER3_*_LC above
    if r in _TIER3_FILES_LC or r.startswith(_TIER3_PREFIXES_LC):
        return True
    marker = REPO_MARKER.lower()
    if marker and marker in r:  # session rooted above the repo
        sub = r.split(marker, 1)[1]
        return sub in _TIER3_FILES_LC or sub.startswith(_TIER3_PREFIXES_LC)
    return False


def log(project_dir: str, entry: dict) -> None:
    try:
        entry["ts"] = datetime.now(timezone.utc).isoformat()
        path = os.path.join(project_dir, ".claude", "hooks", "tier3-attempts.log")
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def block(msg: str) -> int:
    sys.stderr.write(
        msg + "\n"
        "If this change is part of an approved Tier-3 slice: stop, tell the human to re-run "
        "the session with BR_ALLOW_TIER3=1 (the override is logged), and note that the "
        "change requires a Change Record and second-person approval on the PR.\n"
        "Otherwise: propose the change as a diff in your response instead of applying it.\n"
    )
    return 2


def main() -> int:
    allow = os.environ.get("BR_ALLOW_TIER3") == "1"
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0 if allow else block(
            "BLOCKED (fail-closed): hook received malformed input and cannot verify the "
            "target path. This may mean a Claude Code update changed the hook payload — "
            "the human should check .claude/hooks/protect-tier3.py against current docs."
        )

    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    session = payload.get("session_id", "")
    global REPO_MARKER
    REPO_MARKER = os.path.basename(os.path.realpath(project_dir)) + "/"

    if tool == "Bash":
        cmd = tool_input.get("command") or ""
        hits, allowed = live_hits(cmd, project_dir)
        for seg in ([] if hits else allowed):   # logged only when the command runs
            log(project_dir, {"check": "live-system", "tool": "Bash", "action": "ALLOWLIST-ALLOWED",
                              "session": session, "cmd": seg[:200]})
        if hits:
            allow_live = os.environ.get("BR_ALLOW_LIVE") == "1"
            log(project_dir, {"check": "live-system", "tool": "Bash",
                              "action": "OVERRIDE-ALLOWED" if allow_live else "BLOCKED",
                              "program": ";".join(sorted(set(t for _s, t in hits))),
                              "session": session, "cmd": cmd[:200]})
            if not allow_live:
                piped = sorted(set(t for _s, t in hits if t.endswith("(piped)")))
                out = sorted(set(t for _s, t in hits if t in PUBLISH_TOOLS or " to " in t))
                live = sorted(set(t for _s, t in hits) - set(piped) - set(out))
                if live:
                    sys.stderr.write("BLOCKED (live system: %s). %s\n" % (", ".join(live), LIVE_MESSAGE))
                if out:
                    sys.stderr.write("BLOCKED (publish or data out: %s). %s %s\n"
                                     % (", ".join(out), PUBLISH_MESSAGE, OVERRIDE_SENTENCE))
                if piped:
                    sys.stderr.write("BLOCKED (piped into a shell: %s). %s %s\n"
                                     % (", ".join(p.replace(" (piped)", "") for p in piped), PIPED_MESSAGE,
                                        OVERRIDE_SENTENCE))
                return 2
        # Case-insensitive: on a case-insensitive filesystem `sed -i` on packages/API/...
        # hits the same file as packages/api/... — mirror the Edit-path lowercasing.
        cmd_lc = cmd.lower()
        refs = [p for p in TIER3_FILES + TIER3_PREFIXES if p.lower() in cmd_lc]
        if refs and WRITE_CMD.search(NO_WRITE_REDIRECT.sub(" ", cmd)):
            action = "OVERRIDE-ALLOWED" if allow else "BLOCKED"
            log(project_dir, {"path": ";".join(refs), "tool": "Bash", "action": action,
                              "session": session, "cmd": cmd[:200]})
            if allow:
                return 0
            return block(
                f"BLOCKED: this shell command references Tier-3 protected path(s) "
                f"({', '.join(refs)}) and contains a write-shaped operation. Modifying "
                "Tier-3 files via Bash is not permitted (read-only commands are fine)."
            )
        return 0

    # Edit-shaped tools
    raw_path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not raw_path:
        return 0 if allow else block(
            f"BLOCKED (fail-closed): {tool} call carries no file path the hook can verify."
        )

    abs_path = os.path.realpath(
        raw_path if os.path.isabs(raw_path)
        else os.path.join(payload.get("cwd") or project_dir, raw_path)
    )
    try:
        rel = os.path.relpath(abs_path, os.path.realpath(project_dir))
    except ValueError:
        return 0
    rel = rel.replace(os.sep, "/")
    if rel.startswith("..") and (not REPO_MARKER or REPO_MARKER not in rel):
        return 0  # outside the repo: not our concern

    if not match(rel):
        return 0

    action = "OVERRIDE-ALLOWED" if allow else "BLOCKED"
    log(project_dir, {"path": rel, "tool": tool, "action": action, "session": session})
    if allow:
        return 0
    return block(
        f"BLOCKED: '{rel}' is a Tier-3 protected path (auth/RBAC, schema, remote-execution, "
        "CI, agent-guard config, or your regulated domain). Agents may not modify it directly."
    )


if __name__ == "__main__":
    sys.exit(main())
