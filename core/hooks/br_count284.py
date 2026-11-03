#!/usr/bin/env python3
"""2.8.4's block count, frozen. Every function below is the released 2.8.4 function of the same name in core/hooks/validate-verdicts.py
(tag v2.8.4), copied unchanged; the release checks pin this file's hash and compare each function to that tag. validate-verdicts.py
runs bump_stop_blocks() here at every Stop it counts, on 2.8.4's own field (`stop_blocks`) and 2.8.4's own turn key, so the count 2.8.4
keeps is kept by 2.8.4's code on 2.8.4's data, whether 2.8.4's hooks, this version's, or both ran before. Do not edit: a change here
is not 2.8.4's count."""
import json
import os


def _blocks_path(tpath):
    """D-322 (audit 13R F4): the block budget's own file beside the transcript. No snapshot call writes or removes it."""
    return (tpath[:-len(".jsonl")] if tpath.endswith(".jsonl") else tpath) + ".br-stop-blocks.json"


def _snap_path(tpath):
    return (tpath[:-len(".jsonl")] if tpath.endswith(".jsonl") else tpath) + ".br-snapshot.json"


def bump_stop_blocks(tpath, payload, turn_key):
    """Count one more blocking Stop for this session and turn; return the new count, or None when the count cannot be read or kept
    (then a Stop that the hook already blocked once ends the turn with the FAILED line instead, D-286). Audit 13 R12: every path that
    blocks a turn (a problem, a crash, a timeout) counts under the one key of that turn (turn_identity()); a block whose turn cannot be
    read (turn_key None) is counted as pending and joins the next count of the session. D-322 (audit 13R F4): the count has its own
    file, so dropping a snapshot never resets it, and a count file that exists but cannot be read is None, never a fresh count of 0."""
    bp = _blocks_path(tpath)
    if os.path.exists(bp):
        try:
            state = json.load(open(bp))
            if not isinstance(state, dict):
                raise ValueError("the block count file is not a JSON object")
        except Exception:      # D-270 (closed; D-322): a count that cannot be read is not 0; None ends a bounced Stop loudly
            return None
    else:
        try:                   # D-322: carry over a count an older hook kept in the snapshot file (an upgrade in mid-session)
            snap = json.load(open(_snap_path(tpath)))
        except Exception:      # D-270 (normal; D-322): no older count to carry over
            snap = {}
        if not isinstance(snap, dict) or not isinstance(snap.get("stop_blocks", {}), dict):
            return None        # D-333 (audit 13T T3): a snapshot or older count that is not an object is a count it cannot read, never 0
        state = {"stop_blocks": snap.get("stop_blocks") or {}}
    sid = payload.get("session_id") or ""
    counts = state.setdefault("stop_blocks", {})
    if not isinstance(counts, dict):
        return None
    pend = "%s:pending" % sid
    key = pend if turn_key is None else "%s:%s" % (sid, turn_key)
    for k in {key, pend}:      # D-327 (audit 13S S8): a count is a whole number of 0 or more; anything else is a count it cannot read
        v = counts.get(k, 0)
        if type(v) is not int or v < 0:
            return None
    if turn_key is None:
        counts[key] = counts.get(key, 0) + 1
    else:
        counts[key] = counts.get(key, 0) + 1 + counts.pop(pend, 0)
    try:
        json.dump(state, open(bp, "w"))
    except OSError:   # D-270 (closed): None means the count cannot be kept, and the hook keeps blocking
        return None
    return counts[key]


def carry_legacy_count(sp):
    """D-328 (audit 13S S6): before 2.8.4 the block count lived in the snapshot file. Before a snapshot file is replaced or dropped,
    and only while the count has no file of its own, copy that older count into its own file (_blocks_path), so an upgrade in the
    middle of a session cannot lose it. A count file that already exists is never touched here."""
    bp = sp[:-len(".br-snapshot.json")] + ".br-stop-blocks.json"
    if os.path.exists(bp):
        return
    try:
        legacy = json.load(open(sp)).get("stop_blocks")
    except Exception:   # D-270 (normal; D-328): no readable snapshot, so no older count in it to carry
        return
    if isinstance(legacy, dict) and legacy:
        try:
            json.dump({"stop_blocks": legacy}, open(bp, "w"))
        except OSError:   # D-270 (closed; D-328): not carried; the Stop then reads no count file and falls back to the snapshot, if any
            pass


def _carries_tool_result(ev):
    """True if the event's message content holds a `tool_result` block (D-112)."""
    content = (ev.get("message") or {}).get("content")
    return isinstance(content, list) and any(
        isinstance(b, dict) and b.get("type") == "tool_result" for b in content)


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


def _own_tool_result(ev):
    """turn_identity(own=True)'s copy of _carries_tool_result: the same test, so the crash and deadline paths need no other helper."""
    c = (ev.get("message") or {}).get("content") if isinstance(ev.get("message"), dict) else None
    return isinstance(c, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c)


def _own_user_notice(ev):
    """turn_identity(own=True)'s copy of _notice_text for a `user` event: a task notice by its origin or its opening tag."""
    c = (ev.get("message") or {}).get("content") if isinstance(ev.get("message"), dict) else None
    if isinstance(c, list):
        c = "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    return (ev.get("origin") or {}).get("kind") == "task-notification" or (isinstance(c, str) and c.lstrip().startswith("<task-notification>"))


def turn_identity(lines, own=False):
    """D-322 (audit 13R F3): (index, key) of the current turn's real user message, by the one rule every path uses: a `user` event
    that is not synthetic or meta, carries no tool result and is not a task notice. key is its timestamp, or idx<n>. (0, "idx0")
    when there is none. The main check uses the shared helpers; the crash and deadline paths pass own=True and use this function's
    copies of the same two tests, so a helper that hung or failed cannot stop them (the grid checks both give the same turn)."""
    tool_result = _own_tool_result if own else _carries_tool_result
    notice = _own_user_notice if own else (lambda ev: _notice_text(ev) is not None)
    idx_, key_ = 0, "idx0"
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:  # D-259 (b): a line that is not JSON is not an event (the current turn's lines are checked, D-270)
            continue
        if not isinstance(ev, dict) or ev.get("type") != "user" or ev.get("isSynthetic") or ev.get("isMeta"):
            continue
        if tool_result(ev) or notice(ev):      # a tool result is stored as a user event (D-112); a task notice is not the user (D-164)
            continue
        idx_, key_ = idx, ev.get("timestamp") or "idx%d" % idx
    return idx_, key_


def _crash_turn_key(tpath):
    """The key of the turn, to bound the crash block (D-322: turn_identity(), the problem path's own rule), or None when the turn
    cannot be read, so the block is counted as pending and a Stop already bounced ends loudly."""
    try:
        return turn_identity(open(tpath, encoding="utf-8", errors="replace").read().splitlines(), own=True)[1]
    except Exception:   # D-270 (closed; D-322): the turn cannot be read; None counts the block as pending
        return None
