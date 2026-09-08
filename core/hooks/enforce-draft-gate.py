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
"""
from __future__ import print_function

import json
import os
import subprocess
import sys

COVERED_TOOLS = ("Write", "Edit", "MultiEdit")


def log(msg):
    try:
        sys.stderr.write("[enforce-draft-gate] %s\n" % msg)
    except Exception:
        pass


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


def block(msg):
    sys.stderr.write(
        "BLOCKED (DRAFT/GATED convention): %s\n"
        "Write the asset as '<name>.DRAFT.md'; it becomes '<name>.md' only once an isolated "
        "claims-gate dispatch writes a validating '<name>.verdict.md' (PASS or CONCERNS, no "
        "BLOCK-graded claim). See the compliance-claims-gate skill.\n"
        "(Set BR_CLAIMS_HOOK=off to disable this check for the session.)\n" % msg
    )
    return 2


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
    if tool not in COVERED_TOOLS:
        return 0

    tool_input = payload.get("tool_input") or {}
    raw_path = tool_input.get("file_path") or ""
    if not raw_path or not raw_path.endswith(".md"):
        return 0

    project_dir = os.path.realpath(
        os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())
    abs_path = raw_path if os.path.isabs(raw_path) else os.path.join(
        payload.get("cwd") or project_dir, raw_path)
    abs_path = os.path.realpath(abs_path)
    target_dir = os.path.dirname(abs_path)
    basename = os.path.basename(abs_path)

    marked = find_marker_dir(target_dir, project_dir)
    if not marked:
        return 0  # inert outside every marked directory

    if basename.endswith(".DRAFT.md") or basename.endswith(".verdict.md"):
        return 0  # the draft itself, and the gate's own verdict file, are always writable

    # Plain "<name>.md" under a marked directory: require a validating sibling verdict.
    stem = basename[: -len(".md")]
    verdict_path = os.path.join(target_dir, stem + ".verdict.md")
    if not os.path.isfile(verdict_path):
        return block(
            "'%s' has no sibling '%s'." % (os.path.relpath(abs_path, project_dir),
                                            os.path.basename(verdict_path)))

    if not (os.path.isfile(validator) and os.access(validator, os.R_OK)):
        log("validator not found at %s, allowing (fail-open)" % validator)
        return 0

    try:
        p = subprocess.run([sys.executable, validator, verdict_path, "--require", "--json"],
                           capture_output=True, text=True, timeout=30)
        report = json.loads(p.stdout or "{}")
    except Exception as e:
        log("validator invocation failed, allowing (fail-open): %s" % e)
        return 0

    verdicts = report.get("verdicts") or []
    ok = bool(report.get("ok")) and len(verdicts) >= 1 and all(
        v in ("PASS", "CONCERNS") for v in verdicts)
    if not ok:
        return block(
            "'%s' exists but does not validate as a cleared verdict (errors: %s; verdicts: %s)."
            % (os.path.basename(verdict_path), "; ".join(report.get("errors") or [])[:300],
               verdicts or "none"))

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # never crash the hook — an uncaught exception must fail OPEN
        log("unexpected error, allowing (fail-open): %s" % e)
        sys.exit(0)
