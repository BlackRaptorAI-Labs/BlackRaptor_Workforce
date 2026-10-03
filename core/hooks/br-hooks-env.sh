#!/bin/bash
# BlackRaptor Core — the one kill-switch parser, sourced by every core hook wrapper (2.3.0).
#
#   BR_HOOKS=off          turns OFF every BlackRaptor core hook (SessionStart, PreToolUse, Stop).
#   BR_VERDICT_HOOK=off   turns off the Stop verdict validator only.
#   BR_CLAIMS_HOOK=off    turns off the PreToolUse DRAFT/GATED write guard only.
#
# br_hook_disabled <per-hook variable name or ""> <label> <what stops being checked>
# Returns 0 (disabled) after one line to stderr, so a disabled control is never silent; returns 1
# otherwise. Sourced, never executed; a wrapper that cannot find this file runs its hook as normal.
br_hook_disabled() {
  local var="$1" label="$2" what="$3" val="on"
  if [ "${BR_HOOKS:-on}" = "off" ]; then
    echo "[blackraptor] $label DISABLED via BR_HOOKS=off — $what" >&2
    return 0
  fi
  if [ -n "$var" ]; then
    eval "val=\"\${$var:-on}\""
    if [ "$val" = "off" ]; then
      echo "[blackraptor] $label DISABLED via $var=off — $what" >&2
      return 0
    fi
  fi
  return 1
}
