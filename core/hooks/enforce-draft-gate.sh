#!/bin/bash
# BlackRaptor Core — DRAFT/GATED write guard, delivered as a PreToolUse hook (the 2.1.0 claims-gate change).
#
# WHY A HOOK. The `compliance-claims-gate` skill's DRAFT/GATED convention (write `<name>.DRAFT.md`,
# promote to `<name>.md` only once `<name>.verdict.md` holds a claims-gate PASS that validates) was, until this hook,
# checklist-only: nothing stopped a producer from writing the final `.md` directly. This hook makes
# the convention mechanical where it can see the write by name: a Write/Edit whose target is a `.md` file, or a Bash
# command that writes one (see enforce-draft-gate.py), under a directory the session has marked as a marketing-asset directory.
#
# SCOPE. Its DRAFT/GATED rule applies under a folder marked with a `.br-assets` marker file, with the exceptions below (see
# `enforce-draft-gate.py` for the exact directory-marking rule). This is the scoping the August
# unscoped Stop hook lacked and over-blocked trying to approximate; an engineering or council
# session that touches no marked directory is blocked by this hook only for a Bash command that names a verdict file it
# writes, a `cd` the helper cannot resolve before a relative `.md` write in a form it parses or an archive extract (D-314: in every project, since no record
# of where the marked folders are can be trusted to be current), or, when the check cannot finish, by the rule in 2 below.
#
# BASH (D-175, 2.8.2). The hook also runs on Bash and, everywhere, blocks a command whose text names the
# `*.verdict.md` file it writes in a form the helper parses (a redirect, tee, cp/mv/install/ln/rsync, sed or perl -i, dd, truncate, or an interpreter -c/-e text; enforce-draft-gate.py
# lists them), so the Stop hook can read a verdict file's content from a Write call. A name built at run time, a script, or a
# writer it does not parse (curl -o, wget -O, touch, awk; _eval/proofs/2026-10-patch284/amend1/q6/r4-probe.txt) is not seen here; the Stop hook treats any
# verdict file a Bash command names as unverified, and its disk check catches the rest where it runs.
#
# CONTRACT (Claude Code PreToolUse hooks): stdin = JSON {tool_name, tool_input, cwd, ...};
# exit 0 = allow; exit 2 = block, stderr is the reason fed back to the agent.
#
#   1. KILL SWITCH. BR_CLAIMS_HOOK=off (this hook) or BR_HOOKS=off (every core hook) disables it,
#      with one line to stderr so a disabled control is never silent. Parsed by br-hooks-env.sh.
#   2. FAIL CLOSED (D-267, D-305). This hook guards a gated write, so an error never lets one through
#      without a record: the allow line below goes to stderr, which Claude Code keeps in the transcript as the hook's
#      `stderr` (_eval/proofs/2026-10-patch284/amend1/q4/live/claims_helper_missing/transcript.jsonl). When the helper cannot answer (python3 or the helper missing, no temporary file, a crash with
#      any exit status but 0 and 2, or no answer by the watchdog), this wrapper does not guess where the marked
#      folders are: it searches nothing and runs no program. It denies a Write, Edit or MultiEdit whose target is named `.md`,
#      a call whose text names `.md` (a Bash command once its quotes, escapes and line continuations are taken out, or a Write or
#      Edit whose target cannot be read whole), a Bash command that copies a folder, unpacks an archive or copies with a wildcard
#      (the shapes in re_bulk below), a Bash command over 2048 bytes long as sent (D-329, D-333: too long to rewrite in time), and a call it cannot read (no tool name, no command), with "the claims-gate check could not
#      run (<reason>): this call is not allowed until the check works; report it". Every other call passes, with one line on
#      stderr. A file it cannot see by name (a link named otherwise, a moved folder, a script) is not denied here; where the Stop
#      hook's disk check runs, the Stop blocks the turn unless a claims-gate PASS sits beside it, and where that check is skipped
#      or partial the Stop says so (the hooks README beside this file, "Limits that remain"). The kill switch is the owner's way out.
#   3. DEADLINE (D-278, D-290). hooks.json gives this hook 10 s, and Claude Code (measured on client 2.1.296; audit 10V X1: _eval/proofs/2026-10-patch283/amendment11/z6/audit10v-timeout/AUDIT-10V-REPORT.md)
#      lets the write through when a hook outlives it. The helper arms its own alarm at 5 s; this wrapper kills the helper at its 7 s watchdog (TERM, then KILL
#      1 s later) and answers with the rule in 2. Every path that runs before the helper starts answers at once, since the rule reads only the payload.
#   4. Hands the hook payload on stdin to the helper, and passes through only its stderr/exit code. The payload and the helper's
#      messages are read by the shell itself (audit 13 R9), and its own folder is found by the shell too, so a slow program on
#      PATH cannot delay them; making the two temporary files (mktemp) is the one step before the watchdog that runs another program.
set -uo pipefail

case "$0" in */*) HERE="${0%/*}" ;; *) HERE="." ;; esac   # string gate r10: the shell itself, no dirname before the watchdog
HERE="$(cd "$HERE" && pwd)"
if [ -f "$HERE/br-hooks-env.sh" ]; then
  . "$HERE/br-hooks-env.sh"
  br_hook_disabled BR_CLAIMS_HOOK "DRAFT/GATED PreToolUse hook" "marketing-asset writes and shell writes of verdict files are not being checked this session." && exit 0
fi
HELPER="$HERE/enforce-draft-gate.py"
VALIDATOR="${CLAUDE_PLUGIN_ROOT:-$HERE/..}/skills/gate-verdict-format/validate_verdict.py"
IFS= read -r -d '' PAYLOAD || true       # audit 13 R9: a shell built-in, so no program on PATH is run before the watchdog is armed

deny() {
  printf 'BLOCKED (DRAFT/GATED convention): the claims-gate check could not run (%s): this call is not allowed until the check works; report it\n' "$1" >&2
  printf 'If you believe this block is wrong, stop and report it to the human with the reason above; do not disable the check.\n' >&2
  exit 2
}
fallback() {   # $1 = why the helper could not answer. D-305: no scan and no program, only the payload text, so it answers at once
  shopt -s nocasematch
  tool=""; fp=""; cmd=""
  re_tool='"tool_name"[[:space:]]*:[[:space:]]*"([^"]*)"'
  re_fp='"file_path"[[:space:]]*:[[:space:]]*"([^"]*)"'
  re_cmd='"command"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)"'
  # a folder copy, an archive or a wildcard copy writes files the fallback cannot name (the list in enforce-draft-gate.py's BULK_WRITE)
  re_bulk='(^|[;&|( `])((cp|gcp|mv|install|ln)([[:space:]][^;&|]*)?[[:space:]](-[a-z]*[ra][a-z]*([^a-z]|$)|--(recursive|archive))|(cp|gcp|mv|install|ln)[[:space:]][^;&|]*[*?[]|(rsync|ditto|cpio|pax|unzip|7z|7za)([^a-z0-9]|$)|(tar|bsdtar|gtar)[[:space:]]+(-?[a-z]*x|--extract|--get|[^;&|]*[[:space:]](-[a-z]*x|--extract|--get)))'
  [[ $PAYLOAD =~ $re_tool ]] && tool="${BASH_REMATCH[1]}"
  [[ $PAYLOAD =~ $re_fp ]] && fp="${BASH_REMATCH[1]}"
  case "$tool" in
    Write|Edit|MultiEdit)
      if [[ -z $fp || $fp == *\\* ]]; then
        [[ $PAYLOAD == *.md* ]] && deny "$1"     # the target cannot be read whole: a call that names a .md is denied
      elif [[ $fp == *.md ]]; then
        deny "$1"
      fi ;;
    "")
      deny "$1" ;;                               # the call cannot be read: no tool name, so nothing can be ruled out
    Bash)
      [[ $PAYLOAD =~ $re_cmd ]] || deny "$1"     # the command cannot be read
      cmd="${BASH_REMATCH[1]}"
      # D-329 (audit 13S S7 class): bash 3.2 rewrites long text in quadratic time (D-329 records the measured times), and
      # this answer must arrive inside the client's 10 s; a command too long to rewrite quickly is denied, not rewritten
      # D-333 (audit 13T T4): counted in bytes of the command's text as sent, in every locale, as the helper's fallback counts it
      lc="${LC_ALL-}"; lcset="${LC_ALL+x}"; LC_ALL=C; n=${#cmd}          # no subshell: the fallback runs nothing (D-305)
      if [ -n "$lcset" ]; then LC_ALL=$lc; else unset LC_ALL; fi
      [ "$n" -le 2048 ] || deny "$1; a command over 2048 bytes is too long to check without the helper"
      cmd="${cmd//\\\\\\n/}"                         # a JSON-escaped backslash-newline joins two lines into one word
      cmd="${cmd//\\[ntr]/ }"                        # a JSON-escaped newline, tab or return separates words
      cmd="${cmd//[\"\'\\]/}"                    # quotes and backslashes out: `page.m"d"` names page.md
      if [[ $cmd == *.md* || $cmd =~ $re_bulk ]]; then deny "$1"; fi ;;
    *)
      [[ $PAYLOAD == *.md* ]] && deny "$1" ;;
  esac
  printf '[enforce-draft-gate] the claims-gate check could not run (%s); the target or command of this call names no .md file, so it is allowed\n' "$1" >&2
  exit 0
}

[ -f "$HELPER" ] || fallback "the helper enforce-draft-gate.py is missing"
command -v python3 >/dev/null 2>&1 || fallback "python3 is missing"

# D-278 (Amendment 11, Z1), D-290: the watchdog. hooks.json gives this hook 10 s, and Claude Code (measured on client 2.1.296, audit 10V; the path is in 3 above) lets the write
# through when a hook outlives its timeout. The helper arms its own alarm at 5 s; this watchdog counts whole seconds of clock time to 7, checking once after each 1 s
# sleep, so it fires a little after 6 s or a little after 7 s, after the helper's alarm. It is the backup for a helper that cannot answer at
# all: it kills the helper (1 s from TERM to KILL) and answers with the fallback rule above, which reads only the payload. Measured on this
# wrapper (_eval/proofs/2026-10-patch284/amend1/q6/claims-timing-r2.txt, 5 runs each): a hung helper answered between 6.11 and 7.12 s, one
# that ignores TERM between 7.12 and 8.14 s, all before the 10 s ([bud] checks 7 + 1 + 1 < 10).
# BR_WATCHDOG_S can only LOWER the limit.
WD=7
case "${BR_WATCHDOG_S:-}" in
  ''|*[!0-9]*) ;;
  *) if [ "$BR_WATCHDOG_S" -gt 0 ] && [ "$BR_WATCHDOG_S" -lt "$WD" ]; then WD="$BR_WATCHDOG_S"; fi ;;
esac
INF="$(mktemp 2>/dev/null)" && ERRF="$(mktemp 2>/dev/null)" || fallback "no temporary file could be made, so the helper could not be run under its deadline"
FIRED="$INF.fired"
printf '%s' "$PAYLOAD" > "$INF" && [ -s "$INF" ] || fallback "the call could not be handed to the helper"   # Rule F review: the helper reads an empty input as "not a hook call" and allows it, so the fallback answers instead
set -m
python3 "$HELPER" "$VALIDATOR" < "$INF" 2> "$ERRF" &
PID=$!
(
  SECONDS=0                      # D-310: wall-clock time, so the loop's own work cannot push the deadline later
  while [ "$SECONDS" -lt "$WD" ]; do
    sleep 1
    kill -0 "$PID" 2>/dev/null || exit 0
  done
  : > "$FIRED"
  kill -TERM -- "-$PID" 2>/dev/null || kill -TERM "$PID" 2>/dev/null
  sleep 1
  kill -KILL -- "-$PID" 2>/dev/null || kill -KILL "$PID" 2>/dev/null
) > /dev/null 2>&1 &
wait "$PID" 2>/dev/null; rc=$?
# the watchdog sees the helper gone within a second and ends itself (killing it would print a job-control line)
set +m
ERR="$(< "$ERRF")" 2>/dev/null || ERR=""     # audit 13 R9: read by the shell itself
FIRED_NOW=0; [ -e "$FIRED" ] && FIRED_NOW=1
( rm -f "$INF" "$ERRF" "$FIRED" ) > /dev/null 2>&1 &     # D-325: removed in the background, never delaying the answer
if [ "$FIRED_NOW" -eq 1 ]; then
  fallback "the helper did not answer within $WD s"
fi
[ -z "$ERR" ] || printf '%s\n' "$ERR" >&2
case "$rc" in
  0|2) exit "$rc" ;;
esac
fallback "the helper crashed (exit status $rc)"
