#!/usr/bin/env python3
# BlackRaptor Core — the one reader of the client's transcript for both gate hooks (D-337, 2.8.5).
#
# WHY ONE MODULE. Before 2.8.5 the Stop hook and the write hook each had their own copy of "which message starts this turn" and
# "is this a task notice", and the copies disagreed on a notice whose content is null (the Stop's main path called it the user, its
# crash path a notice), so one turn could be counted under two keys. The write hook also compared times as text, so a time written
# with an offset (+02:00) sorted wrong. Every rule both hooks need now lives here, once; verify fails on a copy anywhere else (D-349).
#
# THE TURN RECORD. turn_record(lines) returns {index, id, ts, key, legacy, source}:
#   id   the client's own turn id (`promptId` on the turn's first user message; Claude Code 2.1.310 sends the same value as
#        `prompt_id` to every hook, measured in PATCH-285 M1), or None. Turn equality uses id only, and a missing id equals nothing.
#   ts   the message's time as seconds since the epoch, or None. A time is never read from an id, and an unknown time is never
#        "earlier" than anything.
#   key  the block count's key for the turn: "p:<id>" when there is an id, else the message's timestamp text, else "idx<n>"
#        (the 2.8.4 keys), so a turn has one key on every path that can read the transcript.
#   legacy  the key 2.8.4 gave the same turn (its timestamp as 2.8.4 wrote it into the key, any JSON value, else "idx<n>"): a count
#        2.8.4 kept for this turn before an upgrade in mid-session is carried to `key` once, so the upgrade gives the turn no fresh
#        blocks (audit 14 F01); and the Stop keeps 2.8.4's own count under it, the limit of every block (audit 14e).
#   source  which rule found it ("promptId", "timestamp", "index", "none").
# A path that cannot load this module or read the transcript has no turn ("unknown"); the Stop hook charges it by its own rule (D-337),
# never with a copy of these tests.
import json
from datetime import datetime


def parse_ts(value):
    """An ISO 8601 time (`Z` or an offset) as seconds since the epoch, or None when it is missing or not a time. A time with no offset
    is not guessed at: it is None."""
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None
    return dt.timestamp()


def content_of(ev):
    """The message content of a transcript event (a string, a list of blocks, or None)."""
    msg = ev.get("message") if isinstance(ev, dict) else None
    return msg.get("content") if isinstance(msg, dict) else None


def carries_tool_result(ev):
    """True if the event's message holds a `tool_result` block (a tool result is stored as a `user` event, D-112)."""
    c = content_of(ev)
    return isinstance(c, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c)


def notice_text(ev):
    """The `<task-notification>` text an event carries, or None when it is not a task notice (D-164). An event the client marks as a
    notice by its origin is a notice whatever its content: its text is then "" when the content is null or not text (D-337: the one
    predicate checks `origin.kind` before the content)."""
    if not isinstance(ev, dict):
        return None
    att = ev.get("attachment")
    if ev.get("type") == "attachment" and isinstance(att, dict) and att.get("type") == "queued_command":
        text = att.get("prompt")
        if att.get("commandMode") == "task-notification":
            return text if isinstance(text, str) else ""
        if isinstance(text, str) and text.lstrip().startswith("<task-notification>"):
            return text
        return None
    if ev.get("type") != "user":
        return None
    c = content_of(ev)
    if isinstance(c, list):
        c = "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text"
                      and isinstance(b.get("text"), str))
    origin = ev.get("origin")
    if isinstance(origin, dict) and origin.get("kind") == "task-notification":
        return c if isinstance(c, str) else ""
    if isinstance(c, str) and c.lstrip().startswith("<task-notification>"):
        return c
    return None


def is_real_user(ev):
    """A message that starts a turn: a `user` event that is not synthetic or meta, carries no tool result and is not a task notice."""
    if not isinstance(ev, dict) or ev.get("type") != "user" or ev.get("isSynthetic") or ev.get("isMeta"):
        return False
    return not carries_tool_result(ev) and notice_text(ev) is None


def turn_record(lines):
    """The current turn: the last real user message of `lines` (raw transcript lines). See the header for the fields."""
    rec = {"index": 0, "id": None, "ts": None, "key": "idx0", "legacy": "idx0", "source": "none"}
    for idx, line in enumerate(lines):
        line = line.strip() if isinstance(line, str) else ""
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:   # D-259 (b): a line that is not JSON is not an event (the Stop reports unreadable call lines, D-270)
            continue
        if not is_real_user(ev):
            continue
        pid = ev.get("promptId")
        pid = pid if isinstance(pid, str) and pid else None
        stamp = ev.get("timestamp") if isinstance(ev.get("timestamp"), str) and ev.get("timestamp") else None
        old = ev.get("timestamp")      # audit 14e E01: 2.8.4 keyed a turn by any timestamp value, not only text
        rec = {"index": idx, "id": pid, "ts": parse_ts(stamp),
               "key": ("p:" + pid) if pid else (stamp or "idx%d" % idx), "legacy": ("%s" % (old,)) if old else "idx%d" % idx,
               "source": "promptId" if pid else ("timestamp" if stamp else "index")}
    return rec


def same_turn(a, b):
    """True only when both turn ids are present and equal (a missing id equals nothing)."""
    return isinstance(a, str) and bool(a) and a == b


def other_turn(a, b):
    """True only when both turn ids are present and differ: then a record of turn a is not turn b's. When either is missing (a client
    that sends no turn id), this is False and the caller keeps its 2.8.4 rule (the same project and session), so a client without
    turn ids is judged exactly as before (D-338)."""
    return isinstance(a, str) and bool(a) and isinstance(b, str) and bool(b) and a != b
