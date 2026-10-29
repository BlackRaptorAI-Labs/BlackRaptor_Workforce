#!/bin/bash
# BlackRaptor Core — verdict validator, delivered as a Stop hook (2.0.0, AGENT-SPEC-v3 §7).
#
# WHY A HOOK. `validate_verdict.py` has existed for a year and only ever ran in one place: a CI
# template the user had to install into their own repo. On the marketplace path — the way almost
# everyone actually installs this product — nothing enforced the verdict contract at all. A gate
# could return prose with no block, or a block with a word confidence and no falsifier, and nothing
# noticed. This hook puts the validator on the live path: when a turn dispatched a gate agent, the
# turn does not end until that gate's verdict block validates.
#
# This wrapper does five things and delegates the rest to validate-verdicts.py:
#   1. KILL SWITCH. BR_VERDICT_HOOK=off (this hook) or BR_HOOKS=off (every core hook) disables it,
#      with one line to stderr so a disabled control is never silent — a control you cannot tell is
#      off is worse than no control. Parsed by the shared br-hooks-env.sh. It is the owner's announced
#      way out; an error is never one.
#   2. FAIL CLOSED (D-267, D-268). This hook guards a gate, so it never ends a turn quietly on an error.
#      A helper that crashes, exits non-zero with nothing on stdout, or prints something that is not a
#      JSON decision gets a block from here: "the verdict check crashed (...): this turn is not gated;
#      report it". The first Stop blocks; a Stop that arrives with stop_hook_active (already bounced once,
#      read from the payload text) gets a "Verdict check FAILED" systemMessage instead, so a broken hook
#      cannot loop. A missing python3, helper or validator prints a systemMessage on every Stop ("verdict
#      check could not run (...): gates in this turn are NOT checked") and the doctor FAILs. The snapshot
#      calls (UserPromptSubmit, PostToolUse) only record; their errors are a systemMessage, never a block.
#   3. DEADLINE (D-278). hooks.json gives this wrapper 900 s on a Stop and 20 s on a snapshot call; Claude Code (measured on client 2.1.296, audit 10V X1: _eval/proofs/2026-10-patch283/amendment11/z6/audit10v-timeout/AUDIT-10V-REPORT.md) cancels a hook that
#      outlives that and lets the turn end silently. The helper arms its own alarm at 840 s / 12 s; this wrapper kills the helper at
#      855 s / 17 s and prints the block (or the systemMessage) itself, so no decision outlives the client's timeout.
#   4. Hands the hook payload on stdin to the helper (read once here, so the payload text is on hand).
#   5. Passes through the helper's stdout only when it is exactly one of the two answers the helper prints (D-325, audit 13R F6):
#      {"decision": "block", "reason": "<text>"} or {"systemMessage": "<text>"}; after a non-zero exit, only the block. Anything else
#      is not a decision and gets the block below. Its stderr is passed on too. From the helper's end to the answer the wrapper waits
#      on no other program (shell built-ins only); the temporary files are removed by a background `rm`, which never delays the
#      answer (D-325, F7).
set -uo pipefail

case "$0" in */*) HERE="${0%/*}" ;; *) HERE="." ;; esac   # string gate r10: the shell itself, no dirname before the watchdog
HERE="$(cd "$HERE" && pwd)"
if [ -f "$HERE/br-hooks-env.sh" ]; then
  . "$HERE/br-hooks-env.sh"
  br_hook_disabled BR_VERDICT_HOOK "verdict Stop hook" "gate verdicts are not being validated this session." && exit 0
fi
HELPER="$HERE/validate-verdicts.py"
VALIDATOR="${CLAUDE_PLUGIN_ROOT:-$HERE/..}/skills/gate-verdict-format/validate_verdict.py"
IFS= read -r -d '' PAYLOAD || true       # audit 13 R9: a shell built-in, so no program on PATH is run before the deadline is armed
MODE="${1:-}"

RE_ACTIVE='"stop_hook_active"[[:space:]]*:[[:space:]]*true'
RE_BLOCK='^\{"decision": "block", "reason": "([^"\\]|\\.)*"\}$'
RE_NOTICE='^\{"systemMessage": "([^"\\]|\\.)*"\}$'
RE_TEXT='[^[:space:]]'
# The text below never holds a quote or a backslash, so it is valid inside a JSON string as it stands.
say_notice() { printf '{"systemMessage": "%s"}\n' "$1"; }
say_block() { printf '{"decision": "block", "reason": "This turn cannot be treated as gated:\\n  - %s\\nStop and report it to the human with the reason above; do not disable the check."}\n' "$1"; }
fail_closed() {
  if [ "$MODE" = "--snapshot" ]; then
    say_notice "Verdict check: the turn snapshot could not be recorded ($1); the Stop check falls back to counting files it cannot compare as changed."
  elif [[ $PAYLOAD =~ $RE_ACTIVE ]]; then     # D-325 (audit 13R F7): the shell's own match, no grep
    say_notice "Verdict check FAILED and was not fixed: $1"
  else
    say_block "$1"
  fi
  exit 0
}

missing=""
[ -f "$HELPER" ] || missing="the helper validate-verdicts.py"
[ -n "$missing" ] || [ -f "$VALIDATOR" ] || missing="the validator validate_verdict.py"
[ -n "$missing" ] || command -v python3 >/dev/null 2>&1 || missing="python3"
if [ -n "$missing" ]; then
  [ "$MODE" = "--snapshot" ] && exit 0
  say_notice "Verdict check could not run ($missing is missing): gates in this turn are NOT checked. Run /workforce-doctor."
  exit 0
fi

# D-278 (Amendment 11, Z1): the watchdog. hooks.json gives the Stop call 900 s and the snapshot calls 20 s, and Claude Code cancels a
# hook that outlives its timeout and lets the turn end, silently (measured on client 2.1.296, audit 10V; path in 3 above). The helper arms its own alarm below that (840 s and 12 s); this
# watchdog, a few seconds later, is the backup for a helper that cannot answer at all: it kills the helper and prints the block here.
# BR_WATCHDOG_S can only LOWER the limit (the fixtures and the scratch live proof use it).
WD_STOP=855                    # D-310: 855 + 1 s kill grace + the answer leaves at least 30 s of the 900
WD_SNAPSHOT=17
if [ "$MODE" = "--snapshot" ]; then WD="$WD_SNAPSHOT"; else WD="$WD_STOP"; fi
case "${BR_WATCHDOG_S:-}" in
  ''|*[!0-9]*) ;;
  *) if [ "$BR_WATCHDOG_S" -gt 0 ] && [ "$BR_WATCHDOG_S" -lt "$WD" ]; then WD="$BR_WATCHDOG_S"; fi ;;
esac

INF="$(mktemp 2>/dev/null)" && OUTF="$(mktemp 2>/dev/null)" && ERRF="$(mktemp 2>/dev/null)" \
  || fail_closed "no temporary file could be made, so the helper could not be run under its deadline"
FIRED="$INF.fired"
printf '%s' "$PAYLOAD" > "$INF"
set -m
python3 "$HELPER" "$VALIDATOR" "$@" < "$INF" > "$OUTF" 2> "$ERRF" &     # "$@": --snapshot turn-start|bash (D-190)
PID=$!
(
  SECONDS=0                      # D-310: wall-clock time; audit 12 measured 892.5 s on an 885 s watchdog that counted sleeps
  while [ "$SECONDS" -lt "$WD" ]; do
    sleep 1
    kill -0 "$PID" 2>/dev/null || exit 0
  done
  : > "$FIRED"
  kill -TERM -- "-$PID" 2>/dev/null || kill -TERM "$PID" 2>/dev/null
  sleep 1
  kill -KILL -- "-$PID" 2>/dev/null || kill -KILL "$PID" 2>/dev/null
) > /dev/null 2>&1 &
wait "$PID" 2>/dev/null; RC=$?
# the watchdog sees the helper gone within a second and ends itself (killing it would print a job-control line)
set +m
OUT="$(< "$OUTF")" 2>/dev/null || OUT=""
ERR="$(< "$ERRF")" 2>/dev/null || ERR=""
ERR="${ERR:0:600}"
FIRED_NOW=0; [ -e "$FIRED" ] && FIRED_NOW=1
( rm -f "$INF" "$OUTF" "$ERRF" "$FIRED" ) > /dev/null 2>&1 &     # D-325: removed in the background, never delaying the answer
[ -z "$ERR" ] || printf '%s\n' "$ERR" >&2
[ "$FIRED_NOW" -eq 0 ] || fail_closed "the verdict check ran out of time (it did not answer within $WD s): this turn is not gated; report it"

# D-329 (audit 13S S7): a match, never a rewrite. bash 3.2 rewrites long text in quadratic time (D-329 records the measured times),
# and nothing past the helper's end is under the watchdog.
if ! [[ $OUT =~ $RE_TEXT ]]; then
  [ "$RC" -eq 0 ] && exit 0
  fail_closed "the verdict check crashed (exit status $RC): this turn is not gated; report it"
fi
# D-325 (audit 13R F6): exactly one of the helper's two answers passes; after a non-zero exit, only its block (it fails closed already)
if [[ $OUT =~ $RE_BLOCK ]] || { [ "$RC" -eq 0 ] && [[ $OUT =~ $RE_NOTICE ]]; }; then
  printf '%s\n' "$OUT"; exit 0
fi
fail_closed "the verdict check printed output that is not a decision (exit status $RC): this turn is not gated; report it"
