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

THE TRANSCRIPT FILE STORES THE NOTICE IN TWO OTHER SHAPES (D-164, 2.8.2, measured on client transcripts).
The `system`/`task_notification` event appears in the stream output, not in the transcript file this hook
reads. The file holds the notice as text, `<task-notification>` with `<tool-use-id>`, `<status>`,
`<result>` (the seat's returned text) and `<output-file>`: (1) when it lands inside the dispatching
turn, an `attachment` of type `queued_command` (commandMode `task-notification`); (2) when it lands
after that turn ended, a `user` event with `origin.kind` `task-notification`. Reading only the system
event made every backgrounded seat look "still running" after it had returned. Both shapes are read
now, `<result>` first. Shape (2) is not a human message (the client marks it "NOT USER INPUT"), so it
does not start a turn: the seats it reports are checked in the turn where their notice lands.

A MEASURED VERDICT MUST POINT AT A REAL RUN (D-146, 2.7.0). For every verdict block that validates, if
its `evidence` opens with MEASURED, at least one backticked span in it must match the `command` of a
Bash `tool_use` anywhere in this SESSION: the main transcript (every turn so far, not only this one) and
every `subagents/agent-*.jsonl` beside it. Whole session, because a test gate cites the run another
gate made, in an earlier turn or a sibling subagent. Match (D-179, 2.8.2): the span is split into
simple commands (on ; && || | and newlines, redirections such as `2>&1` dropped), and EVERY simple
command in the span must carry exactly the tokens of a simple command that Bash call ran: its first
token and every argument token, nothing missing and nothing added. The span must also be at least 8
characters after whitespace collapse. So a one-letter span, or a span that pads a real `ls` with an
unrun `python3 -m pytest`, does not match. No match blocks with "MEASURED command not executed in this
session". A non-zero exit is counted, never blocked: a mutation run is supposed to go red.

A VERDICT FILE A BASH COMMAND TOUCHED IS UNVERIFIED (D-175, 2.8.2). Check 1c reads a verdict file's
content from the Write call that made it. Any Bash `tool_use` in the turn (main session or a dispatched
subagent) whose command names a `*.verdict.md` marks that file unverified: with no Write or Edit of it
this turn it is reported exactly as "verdict file not produced by a gate dispatch this turn"; with one,
its content is read back from disk, since the shell may have changed it. A `$name` in the path (a
shell loop) is matched as `*` against the files on disk. Read verdict files with the Read tool, not
`cat`; running the validator on a file you wrote with Write is fine (the file is read back and checked).
Checks 1b and 1c read a backgrounded dispatch's returned text from its stored notice, as check 1 does.

FILES ARE CHECKED ON DISK, NOT ONLY IN THE COMMAND TEXT (D-190, 2.8.2). A name built at run time
(`'sec.verdict'+'.md'`, `${F}ict.md`, `$(printf verdict)`) or an archive extract writes a verdict file no
text match sees. So the same script also runs as a snapshot hook: at turn start (UserPromptSubmit) and after
every Bash result (PostToolUse, matcher Bash) it records every `*.verdict.md` (any case) and every plain
`.md` under a `.br-assets`-marked folder (relative path and sha256; `.git`, `node_modules` and virtualenvs
skipped) in a file beside the transcript. At Stop, a file that appeared or changed since turn start with
no Write or Edit of it in the turn is "not produced by a gate dispatch" (a verdict file) or a DRAFT/GATED
promotion (a marked `.md`), and the turn blocks naming it. With no turn-start snapshot (an upgrade
mid-session, a test harness), the baseline is the files git reports clean plus the files older than the
turn's first user message. The command-text match stays as the early check.

LOOP GUARD: `stop_hook_active` is honoured. If the turn is already continuing because this hook
blocked, do not block again. Claude Code cuts a hook off after 8 consecutive blocks; that is a
backstop, not a design.
"""

from __future__ import print_function

import glob
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile

# D-192 (2.8.2, audit 3 G9): the gate roster is read from verdict-schema.json (`gates`, beside the validator),
# the one list verify.sh, this hook and validate_verdict.py share. `council_seats` may also sign a verdict
# block (the council skill validates them); a project adds gates in .claude/gates-allow.txt. Filled in main().
GATES, SEATS = set(), set()


def load_roster(validator, project_dir):
    """(gates, seats, allowed) from the schema beside the validator and the project's allow file."""
    try:
        sch = json.load(open(os.path.join(os.path.dirname(validator), "verdict-schema.json"), encoding="utf-8"))
        gates, seats = set(sch.get("gates") or []), set(sch.get("council_seats") or [])
    except Exception:
        gates, seats = set(), set()
    allowed = set()
    try:
        allowed = {l.strip() for l in open(os.path.join(project_dir, ".claude", "gates-allow.txt"), encoding="utf-8")
                   if l.strip() and not l.startswith("#")}
    except OSError:
        pass
    return gates | allowed, seats

# The fixed prefix of a backgrounded Agent/Task dispatch's async-launch tool_result (D-65). Never
# treated as a gate's returned text, whether or not a task_notification has arrived yet.
STUB_PREFIX = "Async agent launched"

# The validator's own fence rule (validate_verdict.py FENCE), used here only to read each block's
# `agent` for the author check (D-112, R22). Validity is still judged by the validator itself.
FENCE = re.compile(r"^[ \t]*```verdict[ \t]*\n(.*?)\n[ \t]*```", re.S | re.M)

# A *.verdict.md path named in a Bash command (D-175).
VERDICT_REF = re.compile(r"[^\s'\"<>|;&()=`]*\.verdict\.md")   # a $name or ${name} in it is globbed as *

# Check 3 match (D-179): simple commands, redirections dropped, compared token for token.
REDIRECT = re.compile(r"(?<!\S)[0-9]*(?:&>>?|>>?&?|<)\s*[^\s;|&<>]+")
CMD_SEP = {";", "&&", "||", "|", "&", "|&"}


def _simple_commands(text):
    """[(token, ...)] for each simple command in a shell text, redirections dropped (D-179)."""
    text = REDIRECT.sub(" ", text.replace("\n", " ; "))
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=";&|")
        lex.whitespace_split = True
        toks = list(lex)
    except ValueError:
        toks = text.split()
    out, cur = [], []
    for t in toks + [";"]:
        if t in CMD_SEP:
            if cur:
                out.append(tuple(cur))
            cur = []
        elif t not in ("(", ")", "{", "}"):
            cur.append(t)
    return out


def span_matches(span, cmd):
    """True when every simple command in a MEASURED span is, token for token, a simple command that the
    executed Bash command ran (D-179). The 8-character floor applies only when the span is not itself one
    executed simple command token for token (D-195): `go test` or `pytest`, run and cited exactly, matches."""
    ran = set(_simple_commands(cmd))
    cited = _simple_commands(span)
    if not cited or not all(c in ran for c in cited):
        return False
    return len(cited) == 1 or len(" ".join(span.split())) >= 8


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


NOTICE_TAG = re.compile(r"<(tool-use-id|status|result|summary|output-file)>(.*?)</\1>", re.S)


def _notice_text(ev):
    """The `<task-notification>` text a transcript event carries as a stored completion notice, or
    None (D-164): an `attachment` of type `queued_command`, or a `user` event from a task notice."""
    att = ev.get("attachment")
    if ev.get("type") == "attachment" and isinstance(att, dict) and att.get("type") == "queued_command":
        text = att.get("prompt")
        if isinstance(text, str) and (att.get("commandMode") == "task-notification"
                                      or text.lstrip().startswith("<task-notification>")):
            return text
    if ev.get("type") == "user":
        content = (ev.get("message") or {}).get("content")
        if isinstance(content, list):
            content = "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
        if isinstance(content, str) and ((ev.get("origin") or {}).get("kind") == "task-notification"
                                         or content.lstrip().startswith("<task-notification>")):
            return content
    return None


def _parse_notice(text):
    """{tool-use-id, status, result, summary, output-file} from a stored notice's tags (first of each)."""
    out = {}
    for tag, val in NOTICE_TAG.findall(text or ""):
        out.setdefault(tag, val.strip())
    return out


def _carries_tool_result(ev):
    """True if the event's message content holds a `tool_result` block (D-112)."""
    content = (ev.get("message") or {}).get("content")
    return isinstance(content, list) and any(
        isinstance(b, dict) and b.get("type") == "tool_result" for b in content)


SNAP_SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".tox", ".mypy_cache"}
SNAP_LIMIT = 20000         # entries walked before the snapshot gives up (fails open)


def disk_snapshot(project_dir):
    """{relative path: sha256} for every *.verdict.md (any case) and every plain .md under a folder marked
    with .br-assets (D-190). None if the tree is too large to walk."""
    import hashlib
    out, seen = {}, 0
    root = os.path.realpath(project_dir)
    marked_roots = []
    for dp, ds, fs in os.walk(root):
        ds[:] = sorted(d for d in ds if d not in SNAP_SKIP)
        seen += len(fs) + len(ds)
        if seen > SNAP_LIMIT:
            return None
        if ".br-assets" in fs:
            marked_roots.append(dp)
        marked = any(dp == m or dp.startswith(m + os.sep) for m in marked_roots)
        for f in fs:
            fl = f.lower()
            if fl.endswith(".verdict.md") or (marked and fl.endswith(".md") and not fl.endswith(".draft.md")):
                fp = os.path.join(dp, f)
                try:
                    out[os.path.relpath(fp, root)] = hashlib.sha256(open(fp, "rb").read()).hexdigest()
                except OSError:
                    continue
    return out


def _snap_path(tpath):
    return (tpath[:-len(".jsonl")] if tpath.endswith(".jsonl") else tpath) + ".br-snapshot.json"


def snapshot_mode(event, payload):
    """UserPromptSubmit: record the turn-start snapshot. PostToolUse (Bash): record what that call changed."""
    tpath = payload.get("transcript_path")
    if not tpath:
        return 0
    project_dir = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())
    cur = disk_snapshot(project_dir)
    if cur is None:
        return 0
    sp = _snap_path(tpath)
    if event == "turn-start":
        state = {"turn_start": cur, "last": cur, "after_bash": []}
    else:
        try:
            state = json.load(open(sp))
        except Exception:
            return 0      # no turn-start record: the Stop check uses its fallback baseline
        last = state.get("last") or {}
        changed = sorted(k for k in cur if last.get(k) != cur[k])
        if changed:
            state.setdefault("after_bash", []).append({"tool_use_id": payload.get("tool_use_id"), "changed": changed})
        state["last"] = cur
    try:
        json.dump(state, open(sp, "w"))
    except OSError:
        pass
    return 0


def _fallback_baseline(project_dir, cur, turn_ts):
    """Files git reports clean, plus files older than the turn's first user message (D-190 fallback)."""
    base = {}
    try:
        p = subprocess.run(["git", "-C", project_dir, "status", "--porcelain", "--untracked-files=all", "--", "."],
                           capture_output=True, text=True, timeout=20)
        if p.returncode == 0:
            dirty = {l[3:].strip().strip('"') for l in p.stdout.splitlines() if len(l) > 3}
            tracked = subprocess.run(["git", "-C", project_dir, "ls-files"], capture_output=True, text=True, timeout=20)
            for rel in tracked.stdout.splitlines():
                if rel in cur and rel not in dirty:
                    base[rel] = cur[rel]
    except Exception:
        pass
    if turn_ts:
        try:
            from datetime import datetime
            t0 = datetime.fromisoformat(turn_ts.replace("Z", "+00:00")).timestamp()
            for rel, sha in cur.items():
                if os.path.getmtime(os.path.join(project_dir, rel)) < t0:
                    base[rel] = sha
        except Exception:
            pass
    return base


def main():
    if len(sys.argv) < 2:
        return 0
    validator = sys.argv[1]

    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if len(sys.argv) > 3 and sys.argv[2] == "--snapshot":
        return snapshot_mode(sys.argv[3], payload)

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
    # A tool result is ALSO stored as a `type: "user"` event (D-112, audit F1: measured on a live
    # `claude -p` transcript), so it never starts a turn; nor does an `isMeta` event. Without this the
    # turn began at the LAST tool result, after every dispatch, and the hook never saw a gate.
    turn_start, turn_ts = 0, None
    for idx, line in enumerate(lines):
        line_s = line.strip()
        if not line_s:
            continue
        try:
            ev = json.loads(line_s)
        except Exception:
            continue
        if ev.get("type") == "user" and not ev.get("isSynthetic") and not ev.get("isMeta") \
                and not _carries_tool_result(ev) and _notice_text(ev) is None:   # a task notice is not the user (D-164)
            turn_start = idx
            turn_ts = ev.get("timestamp")
    session_lines = lines      # the whole session, for the executed-command check (D-146)
    lines = lines[turn_start:]

    project_dir = os.path.realpath(
        os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())
    global GATES, SEATS
    GATES, SEATS = load_roster(validator, project_dir)
    if not GATES:
        return 0               # no roster readable: fail open, like a missing validator

    dispatched, results, task_idx = {}, {}, {}
    all_dispatched = {}        # tool_use_id -> slug, EVERY Task/Agent dispatch (R22 author check)
    agent_ids = {}             # tool_use_id -> the subagent's agentId (toolUseResult.agentId)
    notifications = {}         # tool_use_id -> {"summary": str|None, "output_file": str|None}
    draft_writes = []          # [(index, abs_path)] — DRAFT writes under a marked directory
    claims_gate_at = []        # [index, ...] — every claims-gate dispatch, in transcript order
    md_writes = []             # [(index, abs_path, content)] — every Write of a *.md file
    verdict_file_writes = []   # [(index, abs_path, content-or-None)] — Write/Edit/MultiEdit of *.verdict.md (R2)
    marked_md_writes = []      # [(index, abs_path)] — Write/Edit/MultiEdit of a plain .md under a marked dir (R2)
    bash_verdict_refs = []     # [raw path] — *.verdict.md named in a Bash command this turn (D-175)
    bash_cmds = []             # every Bash command of the turn, main session and subagents (D-190)
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
        ntext = _notice_text(ev)
        if ntext:
            n = _parse_notice(ntext)
            if n.get("tool-use-id"):
                notifications[n["tool-use-id"]] = {"summary": n.get("summary"), "output_file": n.get("output-file"),
                                                   "result": n.get("result"), "status": n.get("status")}
        for blk in ((ev.get("message") or {}).get("content") or []):
            if not isinstance(blk, dict):
                continue
            if blk.get("type") == "tool_use" and blk.get("name") in ("Task", "Agent"):
                # subagent_type is "<plugin>:<slug>" for a plugin agent, or a bare slug
                slug = str((blk.get("input") or {}).get("subagent_type") or "").split(":")[-1].strip()
                all_dispatched[blk.get("id")] = slug
                if slug in GATES:
                    dispatched[blk.get("id")] = slug
                    task_idx[blk.get("id")] = idx
                if slug == "claims-gate":
                    claims_gate_at.append(idx)
            elif blk.get("type") == "tool_use" and blk.get("name") == "Bash":
                bash_verdict_refs.extend(VERDICT_REF.findall(str((blk.get("input") or {}).get("command") or "")))
                bash_cmds.append(str((blk.get("input") or {}).get("command") or ""))
            elif blk.get("type") == "tool_use" and blk.get("name") in ("Write", "Edit", "MultiEdit"):
                try:
                    inp = blk.get("input") or {}
                    fp = inp.get("file_path") or ""
                    if fp.endswith(".md"):
                        ap = os.path.realpath(fp if os.path.isabs(fp) else os.path.join(project_dir, fp))
                        if ap.endswith(".verdict.md"):
                            verdict_file_writes.append(
                                (idx, ap, inp.get("content") if blk.get("name") == "Write" else None))
                        elif not ap.endswith(".DRAFT.md") and find_marker_dir(os.path.dirname(ap), project_dir):
                            marked_md_writes.append((idx, ap))
                    if blk.get("name") != "Write":
                        continue
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
                tur = ev.get("toolUseResult")
                if isinstance(tur, dict) and tur.get("agentId"):
                    agent_ids[blk.get("tool_use_id")] = str(tur.get("agentId"))

    last_error = {"msg": ""}   # the validator's first error from the latest validates() call (2.3.3: say why a gate's text failed)

    def validates(text):
        """Run validate_verdict.py over `text`; True if it contains at least one valid block. Keeps the
        validator's first error in last_error so a block message says WHY (no block vs a bad block)."""
        tmp = None
        last_error["msg"] = ""
        try:
            fd, tmp = tempfile.mkstemp(suffix=".md")
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
            p = subprocess.run([sys.executable, validator, tmp, "--require", "--json"],
                               capture_output=True, text=True, timeout=30)
            if p.returncode != 0:
                try:
                    errs = json.loads(p.stdout or "{}").get("errors") or []
                    last_error["msg"] = ("no ```verdict block in the returned text" if p.returncode == 3
                                         else str(errs[0]) if errs else "validator rc=%d" % p.returncode)
                except Exception:
                    last_error["msg"] = "validator rc=%d" % p.returncode
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
    validated = []             # [(slug, text)] — every gate text or file content that validated (D-146)

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
            if (note.get("result") or "").strip():
                out, out_location = note["result"], "task notice result"
            elif "result" in note and note.get("status") and note["status"] != "completed" \
                    and not (note.get("output_file") and os.path.isfile(note["output_file"])):
                problems.append("%s: gate seat ended with status %s and returned no text" % (slug, note["status"]))
                continue
            elif summary and "result" not in note:
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
            validated.append((slug, out))
            continue

        locations_checked = ["%s (%s)" % (out_location, last_error["msg"][:160]) if last_error["msg"] else out_location]
        found_valid = False

        seat_path_suffix = os.path.join("council", "%s.verdict.md" % slug)
        for w_idx, abs_path, content in md_writes:
            if w_idx < t_idx:
                continue
            if abs_path.endswith(seat_path_suffix):
                locations_checked.append(os.path.relpath(abs_path, project_dir))
                if validates(content):
                    validated.append((slug, content))
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
                        validated.append((slug, content))
                        found_valid = True
                        break
        if found_valid:
            continue

        detail = ("no valid verdict found in: %s. Every gate ends its output with a valid "
                   "```verdict block (schema v3.3: verdict, integer confidence 0-10, falsifier, "
                   "evidence opening with MEASURED, CITED, COMPUTED, ESTIMATED or ASSUMED, "
                   "standards[]; a PASS also needs a path:line or a backticked command and "
                   "never rests on ASSUMED; MEASURED names the backticked command it ran), or — for a council seat or the claims gate — writes "
                   "one to the file location this hook checked." % "; ".join(locations_checked))
        problems.append("%s: %s" % (slug, detail))

    # Check 1b (D-112, R22): a verdict block's `agent` must be the agent whose dispatch returned it.
    # Applies to EVERY dispatch, gate or not, so a producer cannot hand back a block signed as a gate.
    for tuid, slug in sorted(all_dispatched.items(), key=lambda kv: str(kv[0])):
        texts = []
        note = notifications.get(tuid) or {}
        if (note.get("summary") or "").strip():
            texts.append(note.get("summary"))
        if (note.get("result") or "").strip():          # a backgrounded seat's stored notice (D-164)
            texts.append(note.get("result"))
        out = results.get(tuid)
        if isinstance(out, str) and not out.startswith(STUB_PREFIX):
            texts.append(out)
        for text in texts:
            for raw in FENCE.findall(text):
                try:
                    obj = json.loads(raw)
                except Exception:
                    continue
                agent = obj.get("agent") if isinstance(obj, dict) else None
                if isinstance(agent, str) and agent.split(":")[-1].strip() != slug:
                    problems.append(
                        "%s: returned a verdict block signed by agent '%s'; a verdict block must "
                        "carry the agent of the dispatch that returned it" % (slug or "?", agent))
                elif isinstance(agent, str) and slug not in GATES | SEATS:
                    problems.append(
                        "not a gate agent: %s (it returned a verdict block; only a gate or a council seat signs "
                        "one, so a producer's own PASS is not a gate's verdict)" % slug)

    # Check 1c (D-117, R2, audit F2): a *.verdict.md written or edited this turn must carry blocks a gate
    # actually returned this turn — same agent, same verdict — so no producer or main session can write
    # its own PASS. Write content comes from the transcript; an Edit/MultiEdit is read from disk.
    def _norm_v(v):
        return "COULD NOT ASSESS" if v == "COULD_NOT_ASSESS" else v

    returned = set()           # {(agent slug, verdict)} from every dispatch's returned text this turn
    for tuid, slug in all_dispatched.items():
        texts = []
        note = notifications.get(tuid) or {}
        if (note.get("summary") or "").strip():
            texts.append(note.get("summary"))
        if (note.get("result") or "").strip():          # a backgrounded seat's stored notice (D-164)
            texts.append(note.get("result"))
        out = results.get(tuid)
        if isinstance(out, str) and not out.startswith(STUB_PREFIX):
            texts.append(out)
        for text in texts:
            for raw in FENCE.findall(text):
                try:
                    obj = json.loads(raw)
                except Exception:
                    continue
                if isinstance(obj, dict) and str(obj.get("agent") or "").split(":")[-1].strip() == slug:
                    returned.add((slug, _norm_v(obj.get("verdict"))))
    # A dispatched subagent's own writes live in its own transcript, beside the main one:
    # <transcript_path minus .jsonl>/subagents/agent-<agentId>.jsonl, linked by the dispatch's
    # toolUseResult.agentId (measured on client 2.1.288). Read them for every dispatch of this turn, so a
    # producer subagent with Write cannot write a verdict file or a marked .md unseen (D-117).
    sub_dir = os.path.join(tpath[: -len(".jsonl")] if tpath.endswith(".jsonl") else tpath, "subagents")
    for tuid in all_dispatched:
        aid = agent_ids.get(tuid)
        if not aid or not all(c.isalnum() or c in "-_" for c in aid):
            continue
        try:
            sub_lines = open(os.path.join(sub_dir, "agent-%s.jsonl" % aid), encoding="utf-8",
                             errors="replace").read().splitlines()
        except Exception:
            continue
        for sl in sub_lines:
            try:
                sev = json.loads(sl)
            except Exception:
                continue
            content_blocks = (sev.get("message") or {}).get("content")
            for sblk in content_blocks if isinstance(content_blocks, list) else []:
                if isinstance(sblk, dict) and sblk.get("type") == "tool_use" and sblk.get("name") == "Bash":
                    bash_verdict_refs.extend(VERDICT_REF.findall(str((sblk.get("input") or {}).get("command") or "")))
                    bash_cmds.append(str((sblk.get("input") or {}).get("command") or ""))
                    continue
                if not (isinstance(sblk, dict) and sblk.get("type") == "tool_use"
                        and sblk.get("name") in ("Write", "Edit", "MultiEdit")):
                    continue
                inp = sblk.get("input") or {}
                fp = inp.get("file_path") or ""
                if not fp.endswith(".md"):
                    continue
                ap = os.path.realpath(fp if os.path.isabs(fp) else os.path.join(project_dir, fp))
                if ap.endswith(".verdict.md"):
                    verdict_file_writes.append(
                        (-1, ap, inp.get("content") if sblk.get("name") == "Write" else None))
                elif not ap.endswith(".DRAFT.md") and find_marker_dir(os.path.dirname(ap), project_dir):
                    marked_md_writes.append((-1, ap))

    # D-190: the disk check. A verdict file or marked .md that appeared or changed since turn start with no
    # Write or Edit of it this turn was written by something no command-text match can see.
    try:
        cur = disk_snapshot(project_dir)
        if cur is not None:
            try:
                state = json.load(open(_snap_path(tpath)))
                base = state.get("turn_start") or {}
                by_bash = {c for e in state.get("after_bash") or [] for c in e.get("changed") or []}
            except Exception:
                base, by_bash = _fallback_baseline(project_dir, cur, turn_ts), set()
            touched = {os.path.relpath(ap, project_dir) for _i, ap, _c in verdict_file_writes}
            touched |= {os.path.relpath(ap, project_dir) for _i, ap in marked_md_writes}
            for rel in sorted(k for k in cur if base.get(k) != cur[k]):
                how = "a Bash command changed it" if rel in by_bash else "it appeared or changed on disk"
                if rel.lower().endswith(".verdict.md"):
                    if rel in touched:
                        bash_verdict_refs.append(rel)      # re-read from disk below and checked as before
                    else:
                        problems.append(
                            "'%s': verdict file not produced by a gate dispatch this turn (%s with no Write or "
                            "Edit of it this turn; verdict files are written with the Write tool so the gate "
                            "check can read them)" % (rel, how))
                elif rel not in touched:
                    marked_md_writes.append((-1, os.path.join(project_dir, rel)))   # judged as a Write (D-190)
    except Exception:
        pass                   # fail open on the snapshot itself, never on a judgement it made

    # D-190 (audit 3 G10): a Bash command whose write target is a plain .md under a marked folder promotes
    # an asset outside the Write path; the PreToolUse draft gate's own target parser names it.
    try:
        import importlib.util
        sys.dont_write_bytecode = True     # no __pycache__ beside the shipped hook (it is loaded, not imported)
        spec = importlib.util.spec_from_file_location("br_draft_gate", os.path.join(os.path.dirname(os.path.abspath(__file__)), "enforce-draft-gate.py"))
        dg = importlib.util.module_from_spec(spec); spec.loader.exec_module(dg)
        for c in bash_cmds:
            files, _dirs = dg.bash_write_targets(c)
            for path, srcs in files:
                ap = os.path.realpath(path if os.path.isabs(path) else os.path.join(project_dir, path))
                dests = [os.path.join(ap, os.path.basename(x.rstrip("/"))) for x in srcs] if (os.path.isdir(ap) or path.endswith("/")) else [ap]
                for dest in dests:
                    b = os.path.basename(dest).lower()
                    if b.endswith(".md") and not b.endswith(".draft.md") and not b.endswith(".verdict.md") \
                            and find_marker_dir(os.path.dirname(dest), project_dir):
                        marked_md_writes.append((-1, dest))   # same rule as a Write: a claims-gate dispatch this turn
    except Exception:
        pass

    # D-175: a verdict file a Bash command named this turn. With a Write/Edit origin, re-read it from disk
    # (the shell may have changed it); with none, it is not produced by a gate dispatch.
    bash_paths = set()
    for ref in bash_verdict_refs:
        ref = re.sub(r"\$\{?[A-Za-z_][A-Za-z0-9_]*\}?", "*", ref.strip("'\""))   # `council/$s.verdict.md` in a loop
        base = ref if os.path.isabs(ref) else os.path.join(project_dir, ref)
        found = glob.glob(base) if any(c in ref for c in "*?[") else [base]
        bash_paths.update(os.path.realpath(f) for f in found)
    written = {ap for _i, ap, _c in verdict_file_writes}
    verdict_file_writes = [(i, ap, None if ap in bash_paths else c) for i, ap, c in verdict_file_writes]
    for ap in sorted(bash_paths - written):
        problems.append(
            "'%s': verdict file not produced by a gate dispatch this turn (a Bash command named it and no "
            "Write or Edit made it; verdict files are written with the Write tool so the gate check can read "
            "them)" % os.path.relpath(ap, project_dir))
    for _w_idx, ap, content in verdict_file_writes:
        if content is None:
            try:
                content = open(ap, encoding="utf-8", errors="replace").read()
            except Exception:
                continue           # nothing to compare; the PreToolUse sibling rule still applies
        for raw in FENCE.findall(content or ""):
            try:
                obj = json.loads(raw)
            except Exception:
                continue
            if not isinstance(obj, dict):
                continue
            key = (str(obj.get("agent") or "").split(":")[-1].strip(), _norm_v(obj.get("verdict")))
            if key[0] not in GATES | SEATS:
                problems.append("'%s': not a gate agent: %s (a verdict file carries a gate's block, never a "
                                "producer's)" % (os.path.relpath(ap, project_dir), key[0] or "?"))
            elif key not in returned:
                problems.append(
                    "'%s': verdict file not produced by a gate dispatch this turn (block agent '%s', "
                    "verdict %s; no dispatch of that agent returned that verdict in this turn)" % (
                        os.path.relpath(ap, project_dir), key[0] or "?", key[1]))
    for _w_idx, ap in marked_md_writes:
        if not claims_gate_at:
            problems.append(
                "DRAFT/GATED: '%s' was written under a marketing-asset directory with no claims-gate "
                "dispatch this turn." % os.path.relpath(ap, project_dir))

    # Check 3 (D-146): a MEASURED verdict must cite a command this session ran. Executed commands come
    # from every Bash tool_use in the main transcript (all turns) and every subagent transcript.
    measured_matched = set()
    failed_ids = {"ids": set()}
    try:
        executed, failed = {}, set()   # tool_use_id -> whitespace-collapsed command; ids whose result is_error

        def _scan(src_lines):
            for sl in src_lines:
                try:
                    sev = json.loads(sl)
                except Exception:
                    continue
                cb = (sev.get("message") or {}).get("content")
                for b in cb if isinstance(cb, list) else []:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_use" and b.get("name") == "Bash":
                        c = (b.get("input") or {}).get("command")
                        if isinstance(c, str) and c.strip():
                            executed[b.get("id")] = " ".join(c.split())
                    elif b.get("type") == "tool_result" and b.get("is_error") is True:
                        failed.add(b.get("tool_use_id"))

        failed_ids["ids"] = failed
        _scan(session_lines)
        if os.path.isdir(sub_dir):
            for fn in sorted(os.listdir(sub_dir)):
                if fn.startswith("agent-") and fn.endswith(".jsonl"):
                    try:
                        _scan(open(os.path.join(sub_dir, fn), encoding="utf-8",
                                   errors="replace").read().splitlines())
                    except Exception:
                        continue
        for slug, text in validated:
            for raw in FENCE.findall(text or ""):
                try:
                    obj = json.loads(raw)
                except Exception:
                    continue
                ev = obj.get("evidence") if isinstance(obj, dict) else None
                if not (isinstance(ev, str) and re.match(r"^MEASURED\b", ev)):
                    continue
                spans = [" ".join(x.split()) for x in re.findall(r"`([^`]+)`", ev)]
                spans = [x for x in spans if x]
                hits = [tid for tid, cmd in executed.items() for sp in spans if span_matches(sp, cmd)]
                if hits:
                    measured_matched.update(hits)
                else:
                    problems.append("%s: MEASURED command not executed in this session: %s" % (
                        slug, ", ".join("`%s`" % x[:120] for x in spans[:3]) or "(no backticked command)"))
    except Exception:
        pass                   # fail open on the lookup itself, never on a judgement it made

    # Check 2 (the 2.1.0 claims-gate change): a DRAFT under a marked directory needs a LATER claims-gate dispatch.
    for idx, abs_path in draft_writes:
        if not any(g > idx for g in claims_gate_at):
            problems.append(
                "DRAFT/GATED: '%s' was written under a marketing-asset directory with no "
                "claims-gate dispatch afterward in this session." % (
                    os.path.relpath(abs_path, project_dir)))

    if not problems and dispatched:
        # W-09 completion signal (2.3.3): one line after a clean turn that dispatched gates, so a
        # quiet Stop hook is distinguishable from an absent one. Not a block: no "decision" key.
        n = len(set(dispatched.values()))
        print(json.dumps({"systemMessage": "BlackRaptor verdict check: gates checked %d, verdicts valid %d; "
                          "measured: %d runs matched, %d non-zero."
                          % (n, n, len(measured_matched), len(measured_matched & failed_ids["ids"]))}))
        return 0

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
                       + "\nIf you believe this block is wrong, stop and report it to the human with the "
                         "reason above; do not disable the check."),
        }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
