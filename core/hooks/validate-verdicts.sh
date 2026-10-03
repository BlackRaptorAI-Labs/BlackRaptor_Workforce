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
# This wrapper does three things and delegates the rest to validate-verdicts.py:
#   1. KILL SWITCH. BR_VERDICT_HOOK=off (this hook) or BR_HOOKS=off (every core hook) disables it,
#      with one line to stderr so a disabled control is never silent — a control you cannot tell is
#      off is worse than no control. Parsed by the shared br-hooks-env.sh.
#   2. FAIL-OPEN. No python3, no validator, no helper -> exit 0 and let the turn end. A broken hook
#      must never wedge a session. It fails closed only on the thing it is FOR: a gate verdict it
#      read and found invalid.
#   3. Hands the hook payload on stdin to the helper, and passes through only its stdout.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$HERE/br-hooks-env.sh" ]; then
  . "$HERE/br-hooks-env.sh"
  br_hook_disabled BR_VERDICT_HOOK "verdict Stop hook" "gate verdicts are not being validated this session." && exit 0
fi
HELPER="$HERE/validate-verdicts.py"
VALIDATOR="${CLAUDE_PLUGIN_ROOT:-$HERE/..}/skills/gate-verdict-format/validate_verdict.py"

[ -f "$HELPER" ] || exit 0
[ -f "$VALIDATOR" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

python3 "$HELPER" "$VALIDATOR" 2>/dev/null || exit 0
exit 0
