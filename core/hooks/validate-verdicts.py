#!/usr/bin/env python3
"""Stop-hook helper: validate every gate verdict emitted this turn, AND (the 2.1.0 claims-gate change) catch a
DRAFT written under a marketing-asset directory with no later claims-gate dispatch in the session.

Invoked by validate-verdicts.sh with the path to validate_verdict.py as argv[1] and the Stop-hook
payload on stdin. Prints a `{"decision":"block", ...}` object when either check fails, and nothing
at all otherwise.

FAIL-OPEN everywhere except the two judgements it exists to make. Unreadable transcript,
unparseable event, missing tool_result, validator crash, any unexpected exception -> exit 0
quietly. It blocks ONLY when (a) it successfully read a gate's output and neither the gate's
inline text nor a verdict file it wrote validates, or (b) it saw a `*.DRAFT.md` written under a
`.br-assets`-marked directory with no `claims-gate` dispatch anywhere after it in the same
transcript. This second check is what makes the DRAFT/GATED convention (`compliance-claims-gate`
skill) mechanical rather than checklist-only, extending this hook rather than adding a second
Stop hook (the 2.1.0 claims-gate change §3(c)) — scoped to marked directories only, so an engineering or council
session sees zero blocks from it.

CHECK 1 LOOKS IN TWO PLACES (D-57, GO-BLOCK-P2-BUILD-v1-AMENDMENT-5 §1). Some gate names — most
notably `ethics-governance` — serve two roles: a standalone artifact gate that returns an inline
fenced ```verdict block, and a council seat (COUNCIL.md §3a) that instead writes
`council/<slug>.verdict.md` and returns prose. The same agent name cannot be told apart by name
alone, so for every dispatch of a GATES member Check 1 looks, in order: (a) an inline fenced
```verdict block in the subagent's own returned text; failing that, (b) a `council/<slug>.verdict.md`
write in the transcript (any GATES member may be dispatched as a seat); failing that and only for
`claims-gate`, (c) a `<name>.verdict.md` write beside a `<name>.DRAFT.md` write. All file content is
read from the transcript's own `Write` tool-call input, never from disk, so a stale file on disk
cannot satisfy it. No exemption exists for a council context and seats get no second inline block —
if none of (a)/(b)/(c) validates, the turn blocks naming the gate and every location checked.

A DISPATCH'S "RETURNED TEXT" IS NOT ALWAYS ITS `tool_result` (D-65, GO-BLOCK-P2-BUILD-v1-AMENDMENT-8
§1). Claude Code 2.1.258 launches every Agent/Task dispatch in the background unless the call sets
`run_in_background: false`; a backgrounded dispatch's `tool_result` is a fixed async-launch stub
("Async agent launched successfully ...") and the gate's real text arrives later as a `system` event,
`subtype: "task_notification"`, carrying the same `tool_use_id`. So for (a) above, the text tried is,
in order: (i) a `task_notification` event matching the dispatch's `tool_use_id`, its `summary` field,
or — if `summary` is absent or empty and `output_file` exists — the last assistant text in that file;
(ii) otherwise the `tool_result`, as before. A `tool_result` that is the async-launch stub is never
treated as returned text. If a dispatch has a stub result and no completed notification yet, the turn
BLOCKS with "<slug>: gate seat still running; wait for its result before ending the turn" rather than
falling through to (b)/(c) or silently permitting — a still-running gate is not the same as one whose
text simply failed to validate.

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

# The fixed prefix of a backgrounded Agent/Task dispatch's async-launch tool_result (D-65). Never
# treated as a gate's returned text, whether or not a task_notification has arrived yet.
STUB_PREFIX = "Async agent launched"


def find_marker_dir(start_dir, project_dir):
    """Same rule as enforce-draft-gate.py: `.br-assets` in start_dir or any ancestor up to (and
    including) project_dir, bounded to 25 hops so a session rooted somewhere unexpected can never
    make this loop indefinitely."""
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


def _read_output_file_text(path):
    """The last assistant text in a task's own output file (D-65). The file may be a JSONL
    transcript in the same shape as the main one (assistant `message.content` text blocks) or
    plain text; fail open (None) on anything unreadable rather than raise."""
    try:
        content = open(path, encoding="utf-8", errors="replace").read()
    except Exception:
        return None
    last_text, parsed_any = None, False
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        parsed_any = True
        if ev.get("type") == "assistant":
            for blk in ((ev.get("message") or {}).get("content") or []):
                if isinstance(blk, dict) and blk.get("type") == "text":
                    last_text = blk.get("text")
    if parsed_any:
        return last_text
    return content or None


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

    # TURN BOUNDARY: `transcript_path` is the whole SESSION transcript,
    # cumulative across every turn — confirmed live downstream (a status-report turn that only
    # mentioned `code-reviewer` in prose got blocked) and traced to source: nothing here bounded
    # the scan, so a gate dispatched in an EARLIER turn whose verdict was never found valid stayed
    # in `dispatched` and got re-flagged on every LATER Stop-hook firing, including turns that
    # never touched that gate. Bound the scan to the current turn: everything from the most
    # recent REAL (non-synthetic) user message onward. A hook's own "Stop hook feedback"
    # continuation is marked `isSynthetic: true` and does NOT start a new turn — the user is still
    # waiting on the one exchange the hook bounced back for revision. Fail open (scan everything,
    # today's behaviour) if no real user message is found at all.
    turn_start = 0
    for idx, line in enumerate(lines):
        line_s = line.strip()
        if not line_s:
            continue
        try:
            ev = json.loads(line_s)
        except Exception:
            continue
        if ev.get("type") == "user" and not ev.get("isSynthetic"):
            turn_start = idx
    lines = lines[turn_start:]

    project_dir = os.path.realpath(
        os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())

    dispatched, results, task_idx = {}, {}, {}
    notifications = {}         # tool_use_id -> {"summary": str|None, "output_file": str|None}
    draft_writes = []          # [(index, abs_path)] — DRAFT writes under a marked directory
    claims_gate_at = []        # [index, ...] — every claims-gate dispatch, in transcript order
    md_writes = []             # [(index, abs_path, content)] — every Write of a *.md file
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if ev.get("type") == "system" and ev.get("subtype") == "task_notification":
            tuid = ev.get("tool_use_id")
            if tuid:
                notifications[tuid] = {"summary": ev.get("summary"), "output_file": ev.get("output_file")}
        for blk in ((ev.get("message") or {}).get("content") or []):
            if not isinstance(blk, dict):
                continue
            if blk.get("type") == "tool_use" and blk.get("name") in ("Task", "Agent"):
                # subagent_type is "<plugin>:<slug>" for a plugin agent, or a bare slug
                slug = str((blk.get("input") or {}).get("subagent_type") or "").split(":")[-1].strip()
                if slug in GATES:
                    dispatched[blk.get("id")] = slug
                    task_idx[blk.get("id")] = idx
                if slug == "claims-gate":
                    claims_gate_at.append(idx)
            elif blk.get("type") == "tool_use" and blk.get("name") == "Write":
                try:
                    inp = blk.get("input") or {}
                    fp = inp.get("file_path") or ""
                    if fp.endswith(".DRAFT.md"):
                        abs_path = fp if os.path.isabs(fp) else os.path.join(project_dir, fp)
                        abs_path = os.path.realpath(abs_path)
                        if find_marker_dir(os.path.dirname(abs_path), project_dir):
                            draft_writes.append((idx, abs_path))
                    if fp.endswith(".md"):
                        abs_path = fp if os.path.isabs(fp) else os.path.join(project_dir, fp)
                        abs_path = os.path.realpath(abs_path)
                        md_writes.append((idx, abs_path, inp.get("content") or ""))
                except Exception:
                    pass
            elif blk.get("type") == "tool_result":
                c = blk.get("content")
                if isinstance(c, list):
                    c = "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
                results[blk.get("tool_use_id")] = c if isinstance(c, str) else ""

    def validates(text):
        """Run validate_verdict.py over `text`; True if it contains at least one valid block."""
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(suffix=".md")
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
            p = subprocess.run([sys.executable, validator, tmp, "--require", "--json"],
                               capture_output=True, text=True, timeout=30)
            return p.returncode == 0
        except Exception:
            return False       # fail-closed on THIS lookup only; caller still tries other locations
        finally:
            if tmp and os.path.exists(tmp):
                try:
                    os.unlink(tmp)
                except Exception:
                    pass

    problems = []

    # Check 1: every dispatched gate's verdict validates — inline (2.0.0), or in a file it wrote
    # (D-57, 2.1.0): council/<slug>.verdict.md for any GATES member dispatched as a seat, or
    # <name>.verdict.md beside <name>.DRAFT.md for claims-gate specifically.
    for tuid, slug in sorted(dispatched.items(), key=lambda kv: str(kv[0])):
        tool_out = results.get(tuid)
        is_stub = isinstance(tool_out, str) and tool_out.startswith(STUB_PREFIX)

        out, out_location = None, None
        note = notifications.get(tuid)
        if note:
            summary = (note.get("summary") or "").strip()
            if summary:
                out, out_location = note.get("summary"), "task_notification summary"
            else:
                out_file = note.get("output_file")
                if out_file and os.path.isfile(out_file):
                    text = _read_output_file_text(out_file)
                    if text:
                        out, out_location = text, "task_notification output_file (%s)" % out_file

        if out is None:
            if tool_out is None:
                continue      # still running, or the result never landed — not this hook's call
            if is_stub:
                # Backgrounded dispatch, stub tool_result, no completed notification yet (D-65):
                # a still-running gate is not the same as one whose text failed to validate.
                problems.append(
                    "%s: gate seat still running; wait for its result before ending the turn" % slug)
                continue
            out, out_location = tool_out, "inline ```verdict block"

        t_idx = task_idx.get(tuid, -1)

        if validates(out):
            continue

        locations_checked = [out_location]
        found_valid = False

        seat_path_suffix = os.path.join("council", "%s.verdict.md" % slug)
        for w_idx, abs_path, content in md_writes:
            if w_idx < t_idx:
                continue
            if abs_path.endswith(seat_path_suffix):
                locations_checked.append(os.path.relpath(abs_path, project_dir))
                if validates(content):
                    found_valid = True
                    break
        if found_valid:
            continue

        if slug == "claims-gate":
            # The DRAFT is written by the PRODUCER, earlier in the transcript than claims-gate's
            # own dispatch — no ordering constraint relative to t_idx here. What must come at/after
            # t_idx is the *.verdict.md write itself, so a stale verdict from an unrelated earlier
            # draft/gate pair cannot satisfy this dispatch.
            draft_stems = {dp[: -len(".DRAFT.md")] for _w_idx2, dp in draft_writes}
            for w_idx, abs_path, content in md_writes:
                if w_idx < t_idx or not abs_path.endswith(".verdict.md"):
                    continue
                stem = abs_path[: -len(".verdict.md")]
                if stem in draft_stems:
                    locations_checked.append(os.path.relpath(abs_path, project_dir))
                    if validates(content):
                        found_valid = True
                        break
        if found_valid:
            continue

        detail = ("no valid verdict found in: %s. Every gate ends its output with a valid "
                   "```verdict block (schema v3: verdict, integer confidence 0-10, falsifier, "
                   "evidence, standards[]), or — for a council seat or the claims gate — writes "
                   "one to the file location this hook checked." % "; ".join(locations_checked))
        problems.append("%s: %s" % (slug, detail))

    # Check 2 (the 2.1.0 claims-gate change): a DRAFT under a marked directory needs a LATER claims-gate dispatch.
    for idx, abs_path in draft_writes:
        if not any(g > idx for g in claims_gate_at):
            problems.append(
                "DRAFT/GATED: '%s' was written under a marketing-asset directory with no "
                "claims-gate dispatch afterward in this session." % (
                    os.path.relpath(abs_path, project_dir)))

    if problems:
        # De-duplicate while preserving order (P3-FOLLOWON-v2 §3): a same-turn retry dispatches the
        # same gate twice, producing two identical problem lines (e.g. `security-architect` invalid
        # both attempts) that read as two separate failures to the user. Distinct problems, including
        # a distinct gate, are never collapsed — only an exact repeat of the same line.
        seen = set()
        deduped = []
        for p in problems:
            if p not in seen:
                seen.add(p)
                deduped.append(p)
        problems = deduped
        print(json.dumps({
            "decision": "block",
            "reason": ("This turn cannot be treated as gated. Fix and re-emit:\n  - "
                       + "\n  - ".join(problems[:5])
                       + "\n(Set BR_VERDICT_HOOK=off or BR_CLAIMS_HOOK=off to disable the "
                         "relevant check for the session.)"),
        }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
