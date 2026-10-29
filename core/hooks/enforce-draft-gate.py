#!/usr/bin/env python3
"""PreToolUse-hook helper: enforce the DRAFT/GATED file convention (the 2.1.0 claims-gate change).

Invoked by enforce-draft-gate.sh with the path to validate_verdict.py as argv[1] and the
PreToolUse-hook payload on stdin. Exits 2 (block) with a one-line reason on stderr when a
Write/Edit targets an ungated `.md` file inside a marketing-asset directory, when a Bash command writes one there or names a
`.verdict.md` it writes in a form it parses (listed below), anywhere, and after its deadline as described below; exits 0 (allow) otherwise.

FAIL CLOSED on a gated write (D-267, D-269). An error the hook catches while judging a write under a marked asset directory
(the validator missing or failing to start, a verdict file or a turn-start snapshot it cannot read, a `cd` it cannot resolve
before a relative `.md` write in a form it parses or an archive extract, in any project: D-314) denies the write (exit 2)
with "the claims-gate check could not run (<reason>): this write is not allowed; report it". Any other error (a lookup that
raises, a crash) goes to the name-only rule below, so a write it cannot see by name, such as a Write to a link with another
name, passes; the hooks README lists this limit. A call the hook does not cover (a tool it does
not list, a target that is not a `.md`, a target outside every marked directory) passes. When an error nothing handled stops
the check, or the deadline below fires, the hook does not guess where the marked directories are (D-305): it denies a Write,
Edit or MultiEdit whose target is named `.md`, a Bash command that names a `.md`, copies a folder, unpacks an archive or copies
with a wildcard (the shapes in BULK_WRITE) or is over 2048 bytes long as sent (D-329, D-333), and a call it cannot read; it allows every other call, saying so on stderr. An empty
stdin is not a hook call.
The owner's way out is the announced kill switch (BR_CLAIMS_HOOK=off or BR_HOOKS=off), never a silent error.
DEADLINE (D-278): hooks.json gives this hook 10 s, and Claude Code (measured on client 2.1.296; audit 10V X1: _eval/proofs/2026-10-patch283/amendment11/z6/audit10v-timeout/AUDIT-10V-REPORT.md) lets the write through when a hook outlives its
timeout. It arms an
alarm at HOOK_BUDGET_S (5 s; the validator call gets 3 s) and, at the deadline, denies the calls listed above by the same rule
(D-305): "the claims-gate check ran out of time: this write is not allowed; report it". The shell wrapper's watchdog (7 s) answers
by the same rule if the helper cannot answer at all (D-290).
It blocks when the target resolves inside a directory the session has marked with a
`.br-assets` file AND the target is a bare `.md` write/edit with no sibling `.verdict.md`
holding a claims-gate PASS that validates, or with one the Stop hook's turn-start snapshot shows unchanged since this turn began,
not written in this turn's transcript and last modified before the turn began (audit 13 R3, D-324, D-332: an approval from an
earlier turn does not clear new copy), or when it cannot judge such a write (by the rules above).

MARKING RULE. A directory D is "marked" if `.br-assets` exists in D or in any ancestor of D, up
to (and including) the project root, looking at most 25 folders up; a folder the hook cannot look into counts as marked. Written by the `marketing-campaign` skill at campaign start (see
`compliance-claims-gate` SKILL.md). Outside every marked directory this hook allows every write except a Bash
command that names a `.verdict.md` it writes in a form it parses, a `cd` it cannot resolve before a relative `.md` write in a form it parses or an
archive extract (D-314), and, when its check cannot finish, the calls the paragraph above lists — this is the
scoping the August unscoped Stop hook lacked.

VERDICT FILES ARE WRITTEN WITH THE WRITE TOOL (D-175, 2.8.2). The Stop hook reads a verdict file's
content from the Write or Edit call that made it. A Bash command whose text names the `*.verdict.md` it writes in one of these forms (a `>` or
`>>` redirect, `tee`, `cp`/`mv` onto it, `sed -i`/`perl -i`, `dd of=`, or a `python -c`/`node -e`
text that writes and names it) hides that content, so this hook BLOCKS it, everywhere, not only in marked
directories. A name built at run time, a variable target, a script, or a writer not listed here (curl -o, wget -O, touch,
awk) is not seen here (_eval/proofs/2026-10-patch284/amend1/q6/c16-probe.txt, _eval/proofs/2026-10-patch284/amend1/q6/r4-probe.txt); the Stop hook treats
any verdict file a Bash command names as unverified, and its disk check catches the rest where it runs. A Bash command that only reads a verdict file (`cat`, `grep`) passes here; the Stop hook
still treats any verdict file a Bash command names as unverified (see validate-verdicts.py, check 1c).

BASH WRITES UNDER A MARKED FOLDER (D-190, 2.8.2, audit 3 G10). A Bash command that writes a plain `.md`
under a `.br-assets`-marked folder (cp, mv, install, ln, rsync, tee, `>`/`>>`, sed -i, dd, a python,
node, perl, ruby, deno, bun or shell -c/-e text that writes and names the file) is judged by the same rule as a Write: it needs a sibling `.verdict.md`
holding a claims-gate PASS that validates. A copy into a folder is judged by the name it lands on; `cp a.DRAFT.md
b.DRAFT.md` is a draft and passes; an archive extracted (tar -x, unzip) or a folder copied into a marked
folder is blocked, since the hook cannot see which files it writes.
"""
from __future__ import print_function

import json
import os
import re
import shlex
import signal
import stat
import subprocess
import sys
import time

COVERED_TOOLS = ("Write", "Edit", "MultiEdit")
VERDICT_BASH_MESSAGE = "Verdict files are written with the Write tool so the gate check can read them."
HEREDOC = re.compile(r"(?<!<)<<(?!<)-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
SEPARATORS = {";", "&&", "||", "|", "&", "|&", "(", ")"}
INTERPRETER = re.compile(r"^(python[0-9.]*|node|nodejs|perl|ruby|deno|bun)$")
WRITE_HINT = re.compile(r"write|copy|rename|move|replace\(|appendFile|['\"][wa]b?\+?['\"]|>>?")
VERDICT_FENCE = re.compile(r"^[ \t]*```verdict[ \t]*\n(.*?)\n[ \t]*```", re.S | re.M)
# D-305 (Rule F review): after a failure the hook cannot see which files a folder copy, an archive or a wildcard writes, so a shell command
# with one of these shapes is denied with the commands that name a .md. The same list is in enforce-draft-gate.sh.
BULK_WRITE = re.compile(r"(^|[;&|(`\s])(cp|gcp|mv|install|ln)\b[^;&|]*(\s-[A-Za-z]*[rRa][A-Za-z]*\b|\s--(recursive|archive)\b|[*?\[])"
                        r"|(^|[;&|(`\s])(rsync|ditto|cpio|pax|unzip|7z|7za)\b"
                        r"|(^|[;&|(`\s])(tar|bsdtar|gtar)\s+(-?[A-Za-z]*x|--extract\b|--get\b|[^;&|]*\s(-[A-Za-z]*x|--extract|--get)\b)")


def names_markdown(cmd):
    """D-305: True when a shell command may write a .md: it names one once quotes and backslashes are taken out (`page.m"d"`), or it
    copies a folder, unpacks an archive or copies with a wildcard. Used only when the hook's own check cannot run."""
    flat = re.sub(r"[\"'\\]", "", (cmd or "").replace("\\\n", ""))   # a backslash-newline joins two lines into one word
    return ".md" in flat.lower() or bool(BULK_WRITE.search(flat))


def log(msg):
    try:
        sys.stderr.write("[enforce-draft-gate] %s\n" % msg)
    except Exception:
        pass


# D-278 (Amendment 11, Z1): THIS HOOK DECIDES BEFORE THE CLIENT'S TIMEOUT. hooks.json gives it 10 s, and Claude Code cancels a hook that
# outlives its timeout and lets the write through, silently (audit 10V, measured on client 2.1.296). So it arms its own alarm at
# HOOK_BUDGET_S (5 s) and, when it fires, denies by the D-305 rule; the shell wrapper's watchdog (7 s, then 1 s for the kill) is the backup if
# this process cannot answer at all, so the worst case ends at least 1 s before the client's 10 s (D-290; at worst 8.14 s measured,
# _eval/proofs/2026-10-patch284/amend1/q6/claims-timing-r2.txt). BR_HOOK_BUDGET_S can only
# LOWER the budget.
HOOK_BUDGET_S = 5
VALIDATOR_TIMEOUT_S = 3
_BUDGET = {"deadline": None}


class BudgetExceeded(BaseException):
    """The hook's own deadline. A BaseException, so no `except Exception` below can swallow it."""


def time_left():
    d = _BUDGET["deadline"]
    return 1e9 if d is None else d - time.time()


def _on_alarm(_signum, _frame):
    raise BudgetExceeded("the claims-gate check")


def _arm_budget():
    try:
        env = float(os.environ.get("BR_HOOK_BUDGET_S") or 0)
    except ValueError:
        env = 0
    b = min(HOOK_BUDGET_S, env) if env > 0 else HOOK_BUDGET_S
    _BUDGET["deadline"] = time.time() + b
    try:
        signal.signal(signal.SIGALRM, _on_alarm)
        signal.setitimer(signal.ITIMER_REAL, b)
    except (AttributeError, ValueError, OSError):   # D-278: no SIGALRM here: the wrapper's watchdog is the only deadline
        pass


def _disarm_budget():
    _BUDGET["deadline"] = None
    try:
        signal.setitimer(signal.ITIMER_REAL, 0)
    except (AttributeError, ValueError, OSError):   # D-278: nothing was armed
        pass


class Cannot(Exception):
    """The judgement could not be made (D-269): the write is denied, naming why."""


def time_block():
    sys.stderr.write(
        "BLOCKED (DRAFT/GATED convention): the claims-gate check ran out of time: this write is not allowed; report it\n"
        "If you believe this block is wrong, stop and report it to the human with the reason above; "
        "do not disable the check.\n")
    return 2


def cannot_block(reason):
    sys.stderr.write(
        "BLOCKED (DRAFT/GATED convention): the claims-gate check could not run (%s): this write is not allowed; report it\n"
        "If you believe this block is wrong, stop and report it to the human with the reason above; "
        "do not disable the check.\n" % reason)
    return 2


_STATE = {"payload": None, "raw": None}
_JSON_WS = re.compile(r"[ \t\n\r]*")


def _members(raw, i, dec):
    """(key, value start, value end) of each member of the JSON object whose `{` is at raw[i]."""
    i = _JSON_WS.match(raw, i + 1).end()
    if raw[i] == "}":
        return
    while True:
        key, j = dec.raw_decode(raw, i)
        j = _JSON_WS.match(raw, j).end()
        if raw[j] != ":":
            raise ValueError("no colon after a key")
        v = _JSON_WS.match(raw, j + 1).end()
        _val, e = dec.raw_decode(raw, v)
        yield key, v, e
        e = _JSON_WS.match(raw, e).end()
        if raw[e] == "}":
            return
        if raw[e] != ",":
            raise ValueError("no comma between members")
        i = _JSON_WS.match(raw, e + 1).end()


def sent_command_text(raw):
    """D-336 (audit 13V V3): the text of tool_input.command exactly as the client sent it (escapes kept), found by the call's own
    structure: the member `command` of the top-level member `tool_input`, the last of each when a key repeats (as json.loads
    keeps the last). None when the call has no such string or cannot be walked."""
    try:
        dec = json.JSONDecoder()
        start = _JSON_WS.match(raw, 0).end()
        if raw[start] != "{":
            return None
        found = None
        for key, v, e in _members(raw, start, dec):
            if key == "tool_input":
                found = None
                if raw[v] == "{":
                    for k2, v2, e2 in _members(raw, v, dec):
                        if k2 == "command":
                            found = raw[v2 + 1:e2 - 1] if raw[v2] == '"' else None
        return found
    except Exception:          # D-270 (closed; D-336): not walked; the caller counts the parsed command instead
        return None


def guard_failure(exc, timed=False):
    """D-269, D-305: an error nothing handled, or the deadline. The hook does not guess where the marked folders are (a search could
    miss one behind a link, an unreadable folder or a depth bound, and could run past the client's timeout): it denies every Write,
    Edit or MultiEdit of a `.md` file, every Bash command that names a `.md` or is over 2048 bytes long as sent (D-329, D-333) and every call it
    cannot read, and allows every other call,
    said on stderr."""
    reason = "%s" % type(exc).__name__
    try:
        payload = _STATE["payload"]
        if not isinstance(payload, dict):
            deny = True        # the call could not be read, so nothing can be ruled out
        else:
            tool = payload.get("tool_name") or ""
            ti = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
            if tool == "Bash":
                cmd = str(ti.get("command") or "")      # D-329: over 2048 bytes of its JSON text, denied as the shell wrapper denies it
                # D-333 (audit 13T T4): the text as sent; D-336 (audits 13U U3, 13V V3): of the field that holds this call's
                # command, found by the call's structure, never by a field's name or value alone
                text = sent_command_text(_STATE["raw"] or "")
                sent = text if text is not None else json.dumps(cmd, ensure_ascii=False)[1:-1]
                deny = len(sent.encode("utf-8", "surrogateescape" if text is not None else "surrogatepass")) > 2048 or names_markdown(cmd)
            elif tool in COVERED_TOOLS:
                fp = str(ti.get("file_path") or "")
                deny = fp.lower().endswith(".md") if fp else ".md" in json.dumps(ti).lower()
            else:
                deny = False
    except Exception:
        deny = True
    if deny:
        return time_block() if timed else cannot_block(reason)
    log("%s stopped the check; the target or command of this call names no .md file, or the hook does not cover its tool, so it is allowed" % ("running out of time" if timed else "an error (%s)" % reason))
    return 0


def time_failure(exc=None):
    """D-278: the hook's own deadline fired. The same rule as an error (D-305)."""
    return guard_failure(exc if exc is not None else BudgetExceeded("the claims-gate check"), timed=True)


def _strip_heredoc_bodies(cmd):
    """Drop heredoc bodies: their text is data fed to a command, not the command line itself."""
    out, pending = [], []
    for line in cmd.split("\n"):
        if pending:
            if line.strip() == pending[0]:
                pending.pop(0)
            continue
        out.append(line)
        pending.extend(m.group(2) for m in HEREDOC.finditer(line))
    return "\n".join(out)


def _tokens(cmd):
    try:
        lex = shlex.shlex(cmd.replace("\n", " ; "), posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        return list(lex)
    except ValueError:
        return cmd.replace("\n", " ; ").split()


def _is_verdict(tok):
    return isinstance(tok, str) and tok.strip("'\"").lower().endswith(".verdict.md")   # string gate r1: a case-blind disk writes .VERDICT.md as .verdict.md


def bash_write_targets(cmd):
    """Every target a Bash command writes (D-175, D-190): [(path, sources)] for a > or >> redirect, tee,
    cp/mv/install/ln/rsync onto it (sources kept so a copy into a folder can be named), sed -i / perl -i,
    dd of=, truncate, and an interpreter's -c/-e text that names a path and writes; plus [dir] for an
    archive extracted into a folder (tar -x, unzip). A read is not a write."""
    files, dirs = [], []
    toks = _tokens(_strip_heredoc_bodies(cmd))
    seg = []
    for tok in toks + [";"]:
        if tok in SEPARATORS:
            f, d = _segment_targets(seg)
            files += f; dirs += d
            seg = []
        else:
            seg.append(tok)
    # an interpreter text keeps its own quoting; read it from the raw command too
    for m in re.finditer(r"\b(python[0-9.]*|node|nodejs|perl|ruby|deno|bun|sh|bash|zsh|dash)\s+(?:-[A-Za-z]*\s+)*-[ce]\s+(\"[^\"]*\"|'[^']*')", cmd):
        body = m.group(2)
        if WRITE_HINT.search(body):
            files += [(x, []) for x in re.findall(r"[^\s'\"(),]*\.md\b", body, re.I)]
    return files, dirs


def bash_verdict_writes(cmd):
    """The `*.verdict.md` targets a Bash command writes (D-175)."""
    return sorted(set(p for p, _s in bash_write_targets(cmd)[0] if _is_verdict(p)))


def _segment_targets(seg):
    files, dirs = [], []
    for i, tok in enumerate(seg):
        if set(tok) <= set("<>&|0123456789") and ">" in tok and not tok.endswith(">&") and i + 1 < len(seg):
            files.append((seg[i + 1].strip("'\""), []))
    words = [t for t in seg if not (set(t) <= set("<>&|0123456789") and (">" in t or "<" in t))]
    while words and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]):
        words = words[1:]
    while words and os.path.basename(words[0]) in ("sudo", "env", "command", "nohup", "exec", "builtin"):
        words = words[1:]
    if not words:
        return files, dirs
    prog, args = os.path.basename(words[0]), words[1:]
    plain = [a for a in args if not a.startswith("-")]
    if prog == "tee":
        files += [(a, []) for a in plain]
    elif prog in ("cp", "mv", "install", "ln", "rsync"):
        for j, a in enumerate(args):
            if a in ("-t", "--target-directory") and j + 1 < len(args):
                files.append((args[j + 1], [x for x in plain if x != args[j + 1]]))
        if len(plain) >= 2:
            files.append((plain[-1], plain[:-1]))
    elif prog in ("sed", "perl") and any(a == "-i" or a.startswith("-i") or (prog == "perl" and "i" in a[1:] and a.startswith("-") and not a.startswith("--")) for a in args):
        files += [(a, []) for a in plain[1:]] if prog == "sed" else [(a, []) for a in plain]
    elif prog == "dd":
        files += [(a[3:], []) for a in args if a.startswith("of=")]
    elif prog == "truncate":
        files += [(a, []) for a in plain]
    elif prog in ("tar", "bsdtar", "gtar") and any(a.startswith("-") and "x" in a or a == "x" or a.startswith("x") for a in args[:1] + [x for x in args if x.startswith("-")]):
        dest = "."
        for j, a in enumerate(args):
            if a in ("-C", "--directory") and j + 1 < len(args):
                dest = args[j + 1]
            elif a.startswith("--directory="):
                dest = a.split("=", 1)[1]
        dirs.append(dest)
    elif prog == "unzip":
        dest = "."
        for j, a in enumerate(args):
            if a == "-d" and j + 1 < len(args):
                dest = args[j + 1]
        dirs.append(dest)
    return files, dirs


def find_marker_dir(start_dir, project_dir):
    """Return the marked directory (nearest first) or None. Bounded walk: stops at
    project_dir (inclusive) or after 25 hops, whichever comes first — never wanders the
    filesystem indefinitely on a session rooted somewhere unexpected."""
    d = os.path.realpath(start_dir)
    root = os.path.realpath(project_dir) if project_dir else None
    hops = 0
    while True:
        if _marker_in(d):
            return d
        if root and d == root:
            return None
        parent = os.path.dirname(d)
        if parent == d or hops >= 25:
            return None
        d = parent
        hops += 1


def _marker_in(d):
    """True when folder d holds a .br-assets file, or when the hook is refused a look into d (D-305, Rule F review: a folder it cannot
    read may be marked, so it is treated as marked; os.path.isfile would answer False)."""
    try:
        return stat.S_ISREG(os.stat(os.path.join(d, ".br-assets")).st_mode)
    except (FileNotFoundError, NotADirectoryError):
        return False
    except OSError:
        return True


def block_verdict_bash(targets):
    sys.stderr.write(
        "BLOCKED (verdict file written by Bash: %s). %s Return the gate's verdict block in its reply, and "
        "copy it unchanged into the file with the Write tool if a file is needed.\n"
        "If you believe this block is wrong, stop and report it to the human with the reason above; "
        "do not disable the check.\n" % (", ".join(targets), VERDICT_BASH_MESSAGE))
    return 2


def block(msg):
    sys.stderr.write(
        "BLOCKED (DRAFT/GATED convention): %s\n"
        "Write the asset as '<name>.DRAFT.md'; it becomes '<name>.md' only once an isolated "
        "claims-gate dispatch writes a validating '<name>.verdict.md' whose verdict is PASS. "
        "See the compliance-claims-gate skill.\n"
        "If you believe this block is wrong, stop and report it to the human with the reason above; "
        "do not disable the check.\n" % msg
    )
    return 2


def draft_decision(abs_path, project_dir, validator, fold_case=False):
    """None to allow, or the reason to block, for a write of abs_path (the Write rule, D-119). fold_case
    (the Bash path, D-199): a name is a draft or a verdict file in any case, as the Stop snapshot reads it."""
    target_dir = os.path.dirname(abs_path)
    basename = os.path.basename(abs_path)
    if not basename.lower().endswith(".md") or not find_marker_dir(target_dir, project_dir):
        return None  # inert outside every marked directory
    name = basename.lower() if fold_case else basename
    if name.endswith(".DRAFT.md".lower() if fold_case else ".DRAFT.md") or name.endswith(".verdict.md"):
        return None  # the draft itself, and the gate's own verdict file, are always writable
    # Plain "<name>.md" under a marked directory: require a sibling verdict holding a validating claims-gate PASS.
    stem = basename[: -len(".md")]
    verdict_path = os.path.join(target_dir, stem + ".verdict.md")
    if not os.path.isfile(verdict_path):
        return "'%s' has no sibling '%s'." % (os.path.relpath(abs_path, project_dir), os.path.basename(verdict_path))
    if not (os.path.isfile(validator) and os.access(validator, os.R_OK)):
        raise Cannot("the validator is missing at %s" % validator)
    try:
        p = subprocess.run([sys.executable, "-I", validator, verdict_path, "--require", "--json"],
                           capture_output=True, text=True, timeout=max(1, min(VALIDATOR_TIMEOUT_S, time_left())))
        report = json.loads(p.stdout or "{}")
    except Exception as e:
        raise Cannot("the validator could not be run: %s" % type(e).__name__)
    verdicts = report.get("verdicts") or []
    # PASS only (D-119, R5, audit F9): claims-gate SHIPs only when every claim is PASS, so a CONCERNS
    # verdict is a HOLD and never promotes the asset.
    ok = bool(report.get("ok")) and len(verdicts) >= 1 and all(v == "PASS" for v in verdicts)
    if not ok:
        return ("'%s' exists but does not validate as a cleared verdict (errors: %s; verdicts: %s)."
                % (os.path.basename(verdict_path), "; ".join(report.get("errors") or [])[:300], verdicts or "none"))
    # D-304 (Rule F review): only the claims gate clears an asset; another gate's PASS copied beside it does not
    try:
        text = open(verdict_path, encoding="utf-8", errors="replace").read()
    except Exception as e:
        raise Cannot("the verdict file could not be read: %s" % type(e).__name__)
    others = []
    for raw in VERDICT_FENCE.findall(text):
        try:
            agent = json.loads(raw).get("agent")
        except Exception:
            agent = None
        if str(agent or "").split(":")[-1].strip() != "claims-gate":
            others.append(str(agent))
    if others:
        return "'%s' is not a claims-gate verdict (a block names the agent %s); only the claims gate clears an asset." % (
            os.path.basename(verdict_path), ", ".join(sorted(set(others))))
    if turn_start_unchanged(verdict_path, project_dir):
        return ("'%s' was not written this turn: an approval from an earlier turn does not clear new copy. Gate this copy with the "
                "claims gate and write its PASS beside it." % os.path.basename(verdict_path))
    return None


def bash_marked_decision(cmd, cwd, project_dir, validator):
    """D-190 (audit 3 G10): a Bash write under a marked folder follows the same DRAFT/GATED rule as Write.
    A copy or move into a folder is judged by the name it lands on; an archive extracted into a marked
    folder is blocked, since the hook cannot see which files it writes."""
    files, dirs = bash_write_targets(cmd)
    bases = [cwd]
    for c in cd_targets(cmd):      # D-305 (Rule F review): `cd assets && cp ../a page.md` writes in assets/
        if re.search(r"[$`*?]", c) or c == "-":
            if any(p.lower().endswith(".md") and not os.path.isabs(p) for p, _s in files) or dirs:   # D-314: in every project
                raise Cannot("the command changes to a folder the hook cannot resolve (%s)" % c)
            continue
        bases.append(os.path.realpath(os.path.join(bases[-1], os.path.expanduser(c))))
    for base in bases:
        why = _marked_decision_from(files, dirs, base, project_dir, validator)
        if why:
            return why
    return None


def turn_start_unchanged(verdict_path, project_dir):
    """Audit 13 R3: True when the Stop hook's turn-start snapshot for this session and project holds verdict_path with the same bytes
    it has now, no Write or Edit of it in this turn's transcript, and a file time before the snapshot's start (D-332): the approval
    beside the asset was written before this turn, so it does not clear copy written in this one. False when there is no such
    snapshot or the file changed; the Stop hook then judges the write against this turn's claims-gate returns."""
    import hashlib
    base = _session_base()
    if not base or not os.path.exists(base + ".br-snapshot.json") or os.path.getsize(base + ".br-snapshot.json") == 0:
        return False       # no snapshot (or one the Stop hook dropped, D-323): the Stop hook's own rule (a verdict file written this turn) decides
    try:
        state = json.load(open(base + ".br-snapshot.json"))
        if not isinstance(state, dict):
            raise ValueError("the snapshot is not a JSON object")
    except Exception as e:   # string gate r12: a snapshot that exists but cannot be read is an error on a marked write: denied
        raise Cannot("the turn snapshot could not be read: %s" % type(e).__name__)
    root = os.path.realpath(project_dir)
    if state.get("root") != root or state.get("session") != (_STATE.get("payload") or {}).get("session_id"):
        return False       # another project or session (or an older hook's file): not this turn's start; the Stop decides
    rel = os.path.relpath(os.path.realpath(verdict_path), root)
    old = (state.get("turn_start") or {}).get(rel) if isinstance(state.get("turn_start"), dict) else None
    if not old:
        return False
    try:
        same = old == hashlib.sha256(open(verdict_path, "rb").read()).hexdigest()
    except Exception as e:
        raise Cannot("the verdict file could not be read: %s" % type(e).__name__)
    # D-324 (audit 13R F1): the same bytes do not prove the file was left alone; a fresh review can return the same block. It is
    # this turn's when this turn wrote it (a Write, Edit or MultiEdit of it in the session's transcript, or a subagent's, since the
    # turn began).
    if not same or written_this_turn(verdict_path, project_dir):
        return False
    # D-332 (live f1-same-bytes, 1 of 4 runs): the client can call this hook before it has saved the approval's Write to the
    # transcript, so a file modified after the snapshot's start time is this turn's too. The Stop still requires a Write or Edit of
    # the approval in the turn, so a file whose time alone was moved (touch) is blocked there.
    started = state.get("started")
    if type(started) in (int, float) and not isinstance(started, bool):
        try:
            if os.stat(verdict_path).st_mtime >= started:
                return False
        except OSError as e:
            raise Cannot("the verdict file could not be read: %s" % type(e).__name__)
    return True


def _real_user(ev):
    """The Stop hook's rule (turn_identity) for a message that starts a turn: a `user` event that is not synthetic or meta, carries no
    tool result and is not a task notice."""
    if not isinstance(ev, dict) or ev.get("type") != "user" or ev.get("isSynthetic") or ev.get("isMeta"):
        return False
    c = (ev.get("message") or {}).get("content") if isinstance(ev.get("message"), dict) else None
    if isinstance(c, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
            return False
        c = "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    if (ev.get("origin") or {}).get("kind") == "task-notification" or (isinstance(c, str) and c.lstrip().startswith("<task-notification>")):
        return False
    return True


def written_this_turn(verdict_path, project_dir):
    """D-324 (audit 13R F1): True when a Write, Edit or MultiEdit of verdict_path appears in the session transcript after the turn's
    real user message, or in a subagent transcript of the session at or after that message's time. A transcript that cannot be read
    is an error on a marked write (denied)."""
    tp = (_STATE.get("payload") or {}).get("transcript_path")
    cwd = (_STATE.get("payload") or {}).get("cwd") or project_dir
    target = os.path.realpath(verdict_path)
    name = os.path.basename(verdict_path)

    def writes(lines, since_idx=0, since_ts=None):
        denied = set()     # D-326 (audit 13S S1): the Stop hook's rule (D-284): a Write or Edit whose tool result is an error did not happen
        for line in lines[since_idx:]:
            if '"is_error"' not in line:
                continue
            try:
                ev = json.loads(line)
            except Exception:   # D-270 (normal; D-326): a line that is not JSON is not a tool result
                continue
            c = (ev.get("message") or {}).get("content") if isinstance(ev, dict) and isinstance(ev.get("message"), dict) else None
            for b in c if isinstance(c, list) else []:
                if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("is_error") is True and b.get("tool_use_id"):
                    denied.add(b["tool_use_id"])
        for line in lines[since_idx:]:
            if name not in line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            if since_ts and isinstance(ev, dict) and str(ev.get("timestamp") or "") < since_ts:
                continue
            for b in ((ev.get("message") or {}).get("content") or []) if isinstance(ev, dict) and isinstance(ev.get("message"), dict) else []:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in ("Write", "Edit", "MultiEdit") \
                        and b.get("id") not in denied:
                    fp = str((b.get("input") or {}).get("file_path") or "")
                    if fp and os.path.realpath(fp if os.path.isabs(fp) else os.path.join(cwd, fp)) == target:
                        return True
        return False

    if not isinstance(tp, str) or not tp:
        return False
    try:
        lines = open(tp, encoding="utf-8", errors="replace").read().splitlines()
    except Exception as e:
        raise Cannot("the session transcript could not be read: %s" % type(e).__name__)
    start, start_ts = 0, None
    for i, line in enumerate(lines):
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if _real_user(ev):
            start, start_ts = i, ev.get("timestamp")
    if writes(lines, start):
        return True
    sub = os.path.join(tp[:-len(".jsonl")] if tp.endswith(".jsonl") else tp, "subagents")
    if start_ts and os.path.isdir(sub):
        for f in sorted(os.listdir(sub)):
            if f.startswith("agent-") and f.endswith(".jsonl"):
                try:
                    if writes(open(os.path.join(sub, f), encoding="utf-8", errors="replace").read().splitlines(), 0, start_ts):
                        return True
                except OSError as e:
                    raise Cannot("a subagent transcript could not be read: %s" % type(e).__name__)
    return False


def _session_base():
    """The transcript path without `.jsonl`: the Stop hook keeps its snapshot beside it (`<base>.br-snapshot.json`)."""
    tp = (_STATE.get("payload") or {}).get("transcript_path")
    if not isinstance(tp, str) or not tp:
        return None
    return tp[:-len(".jsonl")] if tp.endswith(".jsonl") else tp


def cd_targets(cmd):
    """The folder of each `cd` or `pushd` in a shell command, in order (`~` for a bare cd)."""
    out, seg = [], []
    for tok in _tokens(_strip_heredoc_bodies(cmd)) + [";"]:
        if tok in SEPARATORS:
            if seg and os.path.basename(seg[0]) in ("cd", "pushd"):
                args = [a for a in seg[1:] if not (a.startswith("-") and a != "-")]
                out.append(args[0] if args else "~")
            seg = []
        else:
            seg.append(tok)
    return out


def _marked_decision_from(files, dirs, cwd, project_dir, validator):
    absp = lambda x: os.path.realpath(x if os.path.isabs(x) else os.path.join(cwd, x))
    for d in dirs:
        if find_marker_dir(absp(d), project_dir):
            return "an archive is extracted into the marketing-asset folder '%s'; the hook cannot see which files it writes." % (
                os.path.relpath(absp(d), project_dir))
    for path, srcs in files:
        ap = absp(path)
        dests = [ap]
        if os.path.isdir(ap) or path.endswith("/"):
            dests = [os.path.join(ap, os.path.basename(src.rstrip("/"))) for src in srcs] or [ap]
        for src in srcs:
            if os.path.isdir(absp(src)) and find_marker_dir(ap if os.path.isdir(ap) else os.path.dirname(ap), project_dir):
                return "a folder is copied into the marketing-asset folder '%s'; the hook cannot see which files it writes." % (
                    os.path.relpath(ap, project_dir))
        for dest in dests:
            if os.path.isdir(dest) and find_marker_dir(dest, project_dir):
                return "a folder is copied into the marketing-asset folder '%s'; the hook cannot see which files it writes." % (
                    os.path.relpath(dest, project_dir))
            why = draft_decision(dest, project_dir, validator, fold_case=True)
            if why:
                return why
    return None


def main():
    """D-278: arm the hook's own deadline, then judge; reaching the deadline is a denial of a marked write, never a silent pass."""
    _arm_budget()
    try:
        return _main()
    except BudgetExceeded as late:
        _disarm_budget()
        return time_failure(late)
    finally:
        _disarm_budget()


def _main():
    if len(sys.argv) < 2:
        return 0
    validator = sys.argv[1]

    raw = sys.stdin.read()
    _STATE["raw"] = raw
    if not raw.strip():
        return 0               # nothing was sent: not a hook call
    try:
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("the payload is not a JSON object")
    except Exception as e:
        return guard_failure(e)   # D-269, D-305: cannot tell the tool or the target, so the call is denied
    _STATE["payload"] = payload

    tool = payload.get("tool_name") or ""
    project_dir = os.path.realpath(
        os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())
    try:
        if tool == "Bash":
            cmd = str((payload.get("tool_input") or {}).get("command") or "")
            targets = bash_verdict_writes(cmd)
            if targets:
                return block_verdict_bash(targets)
            why = bash_marked_decision(cmd, payload.get("cwd") or project_dir, project_dir, validator)
            return block(why) if why else 0
        if tool not in COVERED_TOOLS:
            return 0

        tool_input = payload.get("tool_input") or {}
        raw_path = tool_input.get("file_path") or ""
        if not raw_path:
            return 0
        abs_path = os.path.realpath(raw_path if os.path.isabs(raw_path) else os.path.join(
            payload.get("cwd") or project_dir, raw_path))
        # D-305 (Rule F review): `.MD` is a Markdown file too, and a link named `notes.txt` that points at `page.md` writes page.md
        if not (raw_path.lower().endswith(".md") or abs_path.lower().endswith(".md")):
            return 0
        why = draft_decision(abs_path, project_dir, validator, fold_case=True)
        return block(why) if why else 0
    except Cannot as c:
        return cannot_block(str(c))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # D-269, D-305: an uncaught error is decided by the no-guess rule
        sys.exit(guard_failure(e))
