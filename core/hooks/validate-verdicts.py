#!/usr/bin/env python3
"""Stop-hook helper: validate every gate verdict emitted this turn.

Invoked by validate-verdicts.sh with the path to validate_verdict.py as argv[1] and the Stop-hook
payload on stdin. Prints a `{"decision":"block", ...}` object when a gate's verdict block does not
validate, and nothing at all otherwise.

FAIL-OPEN everywhere except the one judgement it exists to make. Unreadable transcript, unparseable
event, missing tool_result, validator crash, any unexpected exception -> exit 0 quietly. It blocks
ONLY when it successfully read a gate's output and the validator rejected it.

LOOP GUARD: `stop_hook_active` is honoured. If the turn is already continuing because this hook
blocked, do not block again. Claude Code cuts a hook off after 8 consecutive blocks; that is a
backstop, not a design.
"""

from __future__ import print_function

import json
import os
import subprocess
import sys
import tempfile

# Keep in sync with verify.sh GATE_AGENTS (17 as of 2.0.0). A name here that is not a gate would
# block a turn for no reason; a gate missing here is simply not enforced.
GATES = {
    "code-reviewer", "security-architect", "red-team-reviewer", "compliance-officer",
    "domain-compliance", "privacy-counsel", "operational-readiness", "completion-auditor",
    "qa-test-engineer", "ux-designer", "ethics-governance", "evidence-auditor",
    "compliance-cert", "hw-design-reviewer", "claims-gate", "schema-reviewer", "test-auditor",
}


def main():
    if len(sys.argv) < 2:
        return 0
    validator = sys.argv[1]

    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("stop_hook_active"):
        return 0

    tpath = payload.get("transcript_path")
    if not tpath or not os.path.isfile(tpath):
        return 0
    try:
        lines = open(tpath, encoding="utf-8", errors="replace").read().splitlines()
    except Exception:
        return 0

    dispatched, results = {}, {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        for blk in ((ev.get("message") or {}).get("content") or []):
            if not isinstance(blk, dict):
                continue
            if blk.get("type") == "tool_use" and blk.get("name") in ("Task", "Agent"):
                # subagent_type is "<plugin>:<slug>" for a plugin agent, or a bare slug
                slug = str((blk.get("input") or {}).get("subagent_type") or "").split(":")[-1].strip()
                if slug in GATES:
                    dispatched[blk.get("id")] = slug
            elif blk.get("type") == "tool_result":
                c = blk.get("content")
                if isinstance(c, list):
                    c = "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
                results[blk.get("tool_use_id")] = c if isinstance(c, str) else ""

    if not dispatched:
        return 0

    problems = []
    for tuid, slug in sorted(dispatched.items(), key=lambda kv: str(kv[0])):
        out = results.get(tuid)
        if out is None:
            continue          # still running, or the result never landed — not this hook's call
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(suffix=".md")
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(out)
            p = subprocess.run([sys.executable, validator, tmp, "--require", "--json"],
                               capture_output=True, text=True, timeout=30)
            if p.returncode != 0:
                detail = ""
                try:
                    detail = "; ".join((json.loads(p.stdout) or {}).get("errors", []))[:400]
                except Exception:
                    detail = (p.stdout or p.stderr or "").strip()[:400]
                if not detail:
                    detail = ("returned no ```verdict block. Every gate ends its output with one "
                              "(schema v3: verdict, integer confidence 0-10, falsifier, evidence, "
                              "standards[]).")
                problems.append("%s: %s" % (slug, detail))
        except Exception:
            continue          # fail-open on this dispatch rather than on the session
        finally:
            if tmp and os.path.exists(tmp):
                try:
                    os.unlink(tmp)
                except Exception:
                    pass

    if problems:
        print(json.dumps({
            "decision": "block",
            "reason": ("A gate verdict did not validate against verdict-schema.json, so this turn "
                       "cannot be treated as gated. Fix the block and re-emit it:\n  - "
                       + "\n  - ".join(problems[:5])
                       + "\n(Set BR_VERDICT_HOOK=off to disable this check for the session.)"),
        }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
