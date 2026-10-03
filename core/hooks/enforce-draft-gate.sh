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
# CONTRACT (Claude Code PreToolUse hooks): stdin = JSON {tool_name, tool_input, cwd, ...};
# exit 0 = allow; exit 2 = block, stderr is the reason fed back to the agent.
#
#   1. KILL SWITCH. BR_CLAIMS_HOOK=off (this hook) or BR_HOOKS=off (every core hook) disables it,
#      with one line to stderr so a disabled control is never silent. Parsed by br-hooks-env.sh.
#   2. FAIL-OPEN. No python3, no helper, malformed input -> exit 0 and let the write through,
#      logged to stderr. A broken hook must never wedge a session; it fails closed only on the one
#      judgement it exists to make (an ungated write inside a marked directory).
#   3. Hands the hook payload on stdin to the helper, and passes through only its stderr/exit code.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$HERE/br-hooks-env.sh" ]; then
  . "$HERE/br-hooks-env.sh"
  br_hook_disabled BR_CLAIMS_HOOK "DRAFT/GATED PreToolUse hook" "marketing-asset writes are not being checked this session." && exit 0
fi
HELPER="$HERE/enforce-draft-gate.py"
VALIDATOR="${CLAUDE_PLUGIN_ROOT:-$HERE/..}/skills/gate-verdict-format/validate_verdict.py"

[ -f "$HELPER" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

python3 "$HELPER" "$VALIDATOR"
exit $?
