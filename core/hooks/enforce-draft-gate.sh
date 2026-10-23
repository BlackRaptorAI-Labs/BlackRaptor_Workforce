#!/bin/bash
# BlackRaptor Core — DRAFT/GATED write guard, delivered as a PreToolUse hook (the 2.1.0 claims-gate change).
#
# WHY A HOOK. The `compliance-claims-gate` skill's DRAFT/GATED convention (write `<name>.DRAFT.md`,
# promote to `<name>.md` only once a validating `<name>.verdict.md` exists) was, until this hook,
# checklist-only: nothing stopped a producer from writing the final `.md` directly. This hook makes
# the convention mechanical for the one surface it can see — a Write/Edit whose target is a `.md`
# file under a directory the session has marked as a marketing-asset directory.
#
# SCOPE. Inert everywhere the session has not written a `.br-assets` marker file (see
# `enforce-draft-gate.py` for the exact directory-marking rule). This is the scoping the August
# unscoped Stop hook lacked and over-blocked trying to approximate; an engineering or council
# session never touches a marked directory and sees zero blocks from this hook.
#
# BASH (D-175, 2.8.2). The hook also runs on Bash and, everywhere, blocks a command that writes a
# `*.verdict.md` file, so the Stop hook can read every verdict file's content from a Write call.
#
# CONTRACT (Claude Code PreToolUse hooks): stdin = JSON {tool_name, tool_input, cwd, ...};
# exit 0 = allow; exit 2 = block, stderr is the reason fed back to the agent.
#
#   1. KILL SWITCH. BR_CLAIMS_HOOK=off (this hook) or BR_HOOKS=off (every core hook) disables it,
#      with one line to stderr so a disabled control is never silent. Parsed by br-hooks-env.sh.
#   2. FAIL CLOSED (D-267, D-269). This hook guards a gated write, so an error never lets one through
#      silently. A missing python3 or helper, or a helper that crashes (any exit status but 0 and 2), denies
#      a write under a `.br-assets`-marked folder with "the claims-gate check could not run (<reason>): this
#      write is not allowed; report it". Any other write passes, with one line on stderr. From here the
#      payload is read as text: the target is the "file_path" of a Write/Edit; a Bash command counts when it
#      names a .md and the project has a marked folder, or when it names a .verdict.md. A .DRAFT.md or
#      .verdict.md write is always allowed, as in the helper. The kill switch is the owner's way out.
#   3. DEADLINE (D-278). hooks.json gives this hook 10 s, and Claude Code (measured on client 2.1.296) lets the write through when a hook outlives it. The helper arms
#      its own alarm at 7 s; this wrapper kills the helper at 9 s and denies a marked write itself ("the claims-gate check ran out of
#      time: this write is not allowed; report it"); any other write passes with one line on stderr.
#   4. Hands the hook payload on stdin to the helper, and passes through only its stderr/exit code.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$HERE/br-hooks-env.sh" ]; then
  . "$HERE/br-hooks-env.sh"
  br_hook_disabled BR_CLAIMS_HOOK "DRAFT/GATED PreToolUse hook" "marketing-asset writes and shell writes of verdict files are not being checked this session." && exit 0
fi
HELPER="$HERE/enforce-draft-gate.py"
VALIDATOR="${CLAUDE_PLUGIN_ROOT:-$HERE/..}/skills/gate-verdict-format/validate_verdict.py"
PAYLOAD="$(cat)"
PROJ="${CLAUDE_PROJECT_DIR:-$(pwd)}"

path_marked() {   # is the folder of file $1 inside a folder holding .br-assets, up to the project root?
  p="$1"; case "$p" in /*) ;; *) p="$PROJ/$p" ;; esac
  d="$(dirname "$p")"; n=0
  while [ "$n" -lt 25 ]; do
    [ -f "$d/.br-assets" ] && return 0
    [ "$d" = "$PROJ" ] && return 1
    [ "$d" = "/" ] && return 1
    d="$(dirname "$d")"; n=$((n + 1))
  done
  return 1
}
project_marked() {   # any marked folder under the project root (bounded)
  [ -n "$(find "$PROJ" -maxdepth 8 \( -name .git -o -name node_modules \) -prune -o -name .br-assets -type f -print -quit 2>/dev/null)" ]
}
KIND=crash
deny() {
  if [ "$KIND" = "time" ]; then
    printf 'BLOCKED (DRAFT/GATED convention): the claims-gate check ran out of time: this write is not allowed; report it\n' >&2
  else
    printf 'BLOCKED (DRAFT/GATED convention): the claims-gate check could not run (%s): this write is not allowed; report it\n' "$1" >&2
  fi
  printf 'If you believe this block is wrong, stop and report it to the human with the reason above; do not disable the check.\n' >&2
  exit 2
}
fallback() {   # $1 = why the helper could not run
  tool="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)"
  fp="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)"
  case "$tool" in
    Write|Edit|MultiEdit)
      case "$fp" in
        "") project_marked && deny "$1" ;;
        *.DRAFT.md|*.verdict.md) ;;
        *.md) path_marked "$fp" && deny "$1" ;;
      esac ;;
    Bash)
      if printf '%s' "$PAYLOAD" | grep -q '\.md'; then
        if printf '%s' "$PAYLOAD" | grep -q '\.verdict\.md'; then deny "$1"; fi
        project_marked && deny "$1"
      fi ;;
    *)
      if [ -z "$tool" ]; then project_marked && deny "$1"; fi ;;
  esac
  printf '[enforce-draft-gate] %s; this write is outside every marked folder, so it is allowed\n' "$1" >&2
  exit 0
}

[ -f "$HELPER" ] || fallback "the helper enforce-draft-gate.py is missing"
command -v python3 >/dev/null 2>&1 || fallback "python3 is missing"

# D-278 (Amendment 11, Z1): the watchdog. hooks.json gives this hook 10 s, and Claude Code (measured on client 2.1.296) lets the write through when a hook outlives
# its timeout. The helper arms its own alarm at 7 s; this watchdog, at 9 s, is the backup for a helper that cannot answer at all: it
# kills the helper and denies a marked write here. BR_WATCHDOG_S can only LOWER the limit.
WD=9
case "${BR_WATCHDOG_S:-}" in
  ''|*[!0-9]*) ;;
  *) if [ "$BR_WATCHDOG_S" -gt 0 ] && [ "$BR_WATCHDOG_S" -lt "$WD" ]; then WD="$BR_WATCHDOG_S"; fi ;;
esac
INF="$(mktemp 2>/dev/null)" && ERRF="$(mktemp 2>/dev/null)" || fallback "no temporary file could be made, so the helper could not be run under its deadline"
FIRED="$INF.fired"
printf '%s' "$PAYLOAD" > "$INF"
set -m
python3 "$HELPER" "$VALIDATOR" < "$INF" 2> "$ERRF" &
PID=$!
(
  i=0
  while [ "$i" -lt "$WD" ]; do
    sleep 1
    kill -0 "$PID" 2>/dev/null || exit 0
    i=$((i + 1))
  done
  : > "$FIRED"
  kill -TERM -- "-$PID" 2>/dev/null || kill -TERM "$PID" 2>/dev/null
  sleep 1
  kill -KILL -- "-$PID" 2>/dev/null || kill -KILL "$PID" 2>/dev/null
) > /dev/null 2>&1 &
wait "$PID" 2>/dev/null; rc=$?
# the watchdog sees the helper gone within a second and ends itself (killing it would print a job-control line)
set +m
ERR="$(cat "$ERRF" 2>/dev/null)"
FIRED_NOW=0; [ -e "$FIRED" ] && FIRED_NOW=1
rm -f "$INF" "$ERRF" "$FIRED"
if [ "$FIRED_NOW" -eq 1 ]; then
  KIND=time
  fallback "the helper did not answer within $WD s"
fi
[ -z "$ERR" ] || printf '%s\n' "$ERR" >&2
case "$rc" in
  0|2) exit "$rc" ;;
esac
fallback "the helper crashed (exit status $rc)"
