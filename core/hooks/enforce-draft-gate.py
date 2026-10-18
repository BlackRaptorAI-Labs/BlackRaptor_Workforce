#!/usr/bin/env python3
"""PreToolUse-hook helper: enforce the DRAFT/GATED file convention (the 2.1.0 claims-gate change).

Invoked by enforce-draft-gate.sh with the path to validate_verdict.py as argv[1] and the
PreToolUse-hook payload on stdin. Exits 2 (block) with a one-line reason on stderr when a
Write/Edit targets an ungated `.md` file inside a marketing-asset directory; exits 0 (allow)
otherwise.

FAIL-OPEN everywhere except the one judgement it exists to make. Unreadable payload, a tool
this hook does not cover, a target outside any marked directory, or an internal error -> exit 0.
It blocks ONLY when the target resolves inside a directory the session has marked with a
`.br-assets` file AND the target is a bare `.md` write/edit with no validating sibling
`.verdict.md`.

MARKING RULE. A directory D is "marked" if `.br-assets` exists in D or in any ancestor of D, up
to (and including) the project root. Written by the `marketing-core` skill at onboarding and by
`marketing-campaign` at campaign start (see `compliance-claims-gate` SKILL.md). Outside every
marked directory this hook is completely inert — this is the scoping the August unscoped Stop
hook lacked.

VERDICT FILES ARE WRITTEN WITH THE WRITE TOOL (D-175, 2.8.2). The Stop hook reads a verdict file's
content from the Write or Edit call that made it. A Bash command that writes a `*.verdict.md` (a `>` or
`>>` redirect, `tee`, `cp`/`mv` onto it, `sed -i`/`perl -i`, `dd of=`, or a `python -c`/`node -e`
text that writes it) hides that content, so this hook BLOCKS it, everywhere, not only in marked
directories. A Bash command that only reads a verdict file (`cat`, `grep`) passes here; the Stop hook
still treats any verdict file a Bash command names as unverified (see validate-verdicts.py, check 1c).

BASH WRITES UNDER A MARKED FOLDER (D-190, 2.8.2, audit 3 G10). A Bash command that writes a plain `.md`
under a `.br-assets`-marked folder (cp, mv, install, ln, rsync, tee, `>`/`>>`, sed -i, dd, an
interpreter -c/-e that writes) is judged by the same rule as a Write: it needs a sibling `.verdict.md`
that validates as PASS. A copy into a folder is judged by the name it lands on; `cp a.DRAFT.md
b.DRAFT.md` is a draft and passes; an archive extracted (tar -x, unzip) or a folder copied into a marked
folder is blocked, since the hook cannot see which files it writes.
"""
from __future__ import print_function

import json
import os
import re
import shlex
import subprocess
import sys

COVERED_TOOLS = ("Write", "Edit", "MultiEdit")
VERDICT_BASH_MESSAGE = "Verdict files are written with the Write tool so the gate check can read them."
HEREDOC = re.compile(r"(?<!<)<<(?!<)-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
SEPARATORS = {";", "&&", "||", "|", "&", "|&", "(", ")"}
INTERPRETER = re.compile(r"^(python[0-9.]*|node|nodejs|perl|ruby|deno|bun)$")
WRITE_HINT = re.compile(r"write|copy|rename|move|replace\(|appendFile|['\"][wa]b?\+?['\"]|>>?")


def log(msg):
    try:
        sys.stderr.write("[enforce-draft-gate] %s\n" % msg)
    except Exception:
        pass


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
    return isinstance(tok, str) and tok.strip("'\"").endswith(".verdict.md")


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
    for m in re.finditer(r"\b(python[0-9.]*|node|nodejs|perl|ruby)\s+(?:-[A-Za-z]*\s+)*-[ce]\s+(\"[^\"]*\"|'[^']*')", cmd):
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
        if os.path.isfile(os.path.join(d, ".br-assets")):
            return d
        if root and d == root:
            return None
        parent = os.path.dirname(d)
        if parent == d or hops >= 25:
            return None
        d = parent
        hops += 1


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
    # Plain "<name>.md" under a marked directory: require a validating sibling verdict.
    stem = basename[: -len(".md")]
    verdict_path = os.path.join(target_dir, stem + ".verdict.md")
    if not os.path.isfile(verdict_path):
        return "'%s' has no sibling '%s'." % (os.path.relpath(abs_path, project_dir), os.path.basename(verdict_path))
    if not (os.path.isfile(validator) and os.access(validator, os.R_OK)):
        log("validator not found at %s, allowing (fail-open)" % validator)
        return None
    try:
        p = subprocess.run([sys.executable, validator, verdict_path, "--require", "--json"],
                           capture_output=True, text=True, timeout=30)
        report = json.loads(p.stdout or "{}")
    except Exception as e:
        log("validator invocation failed, allowing (fail-open): %s" % e)
        return None
    verdicts = report.get("verdicts") or []
    # PASS only (D-119, R5, audit F9): claims-gate SHIPs only when every claim is PASS, so a CONCERNS
    # verdict is a HOLD and never promotes the asset.
    ok = bool(report.get("ok")) and len(verdicts) >= 1 and all(v == "PASS" for v in verdicts)
    if not ok:
        return ("'%s' exists but does not validate as a cleared verdict (errors: %s; verdicts: %s)."
                % (os.path.basename(verdict_path), "; ".join(report.get("errors") or [])[:300], verdicts or "none"))
    return None


def bash_marked_decision(cmd, cwd, project_dir, validator):
    """D-190 (audit 3 G10): a Bash write under a marked folder follows the same DRAFT/GATED rule as Write.
    A copy or move into a folder is judged by the name it lands on; an archive extracted into a marked
    folder is blocked, since the hook cannot see which files it writes."""
    files, dirs = bash_write_targets(cmd)
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
    if len(sys.argv) < 2:
        return 0
    validator = sys.argv[1]

    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        log("malformed hook payload, allowing (%s)" % e)
        return 0

    tool = payload.get("tool_name") or ""
    project_dir = os.path.realpath(
        os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())
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
    if not raw_path or not raw_path.endswith(".md"):
        return 0
    abs_path = raw_path if os.path.isabs(raw_path) else os.path.join(
        payload.get("cwd") or project_dir, raw_path)
    why = draft_decision(os.path.realpath(abs_path), project_dir, validator)
    return block(why) if why else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # never crash the hook — an uncaught exception must fail OPEN
        log("unexpected error, allowing (fail-open): %s" % e)
        sys.exit(0)
