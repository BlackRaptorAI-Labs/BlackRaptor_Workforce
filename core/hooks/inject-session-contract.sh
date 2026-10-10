#!/bin/bash
# BlackRaptor Core — session contract, delivered as a SessionStart hook (2.4.0, PLAN-WF-2026-10-v2 R17).
#
# WHY A HOOK. The session contract (shared/session-contract.md: USER-PREFS honoring, the context-review
# reminder, observe-then-suggest) shipped only in the pack CLAUDE.md carriers, which do not load on a
# marketplace install (D-32). A SessionStart hook's additionalContext does load, once per session.
# The text below is a trimmed version (about 1,000 characters) of that file; keep the two in step.
#
# SWITCH. BR_SESSION_CONTRACT=off (or BR_HOOKS=off) turns it off, with one line to stderr. The default
# is set by DEFAULT_STATE below from the T-G measurement recorded in docs/workforce-state.md.
# FAIL-OPEN: any error emits nothing and exits 0.
DEFAULT_STATE="off"   # R17: only-core T-G with it on was 1,791 (> 1,500), so it ships off
HERE="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
if [ -f "$HERE/br-hooks-env.sh" ]; then
  . "$HERE/br-hooks-env.sh"
  br_hook_disabled "" "session-contract SessionStart hook" "the session contract is not injected this session." && exit 0
fi
[ "${BR_SESSION_CONTRACT:-$DEFAULT_STATE}" = "on" ] || exit 0
{
  txt="BlackRaptor session contract (main session). Honor USER-PREFS.md if present (reading level, verbosity, question style, checkpoints, decisions grouping, review cadence, units, role, declined and offered lists) without weakening the operating contract; verbosity defaults to brief. Give a decision as a numbered menu with one option marked recommended. assume-and-flag never covers an irreversible action: ask first. If a context file is overdue for review (quarterly: over 92 days; at-launches: when a campaign or release skill runs), say so once and drop it if declined. At most one preference suggestion per session, only on a quotable signal from this session: neutral, one dimension, no benefit claim. Write USER-PREFS.md only on an explicit yes; record a decline and never re-offer it. Never promise contact between sessions."
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$txt"
} 2>/dev/null || true
exit 0
