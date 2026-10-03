# BlackRaptor Core hooks

The Core pack ships three hooks. Claude Code loads them from `hooks/hooks.json` when the pack is
installed; you do not wire anything yourself.

| Hook | Event | What it does | Timeout |
|---|---|---|---|
| `inject-onboarding-rule.sh` | `SessionStart` | Offers the first-run welcome when a project has no context file or no `USER-PREFS.md`. Silent once you are set up. | 10 s |
| `enforce-draft-gate.sh` | `PreToolUse` (Write, Edit, MultiEdit) | In a folder marked for marketing assets only, blocks writing a final `.md` until a sibling `.verdict.md` exists that validates as PASS or CONCERNS. Inert everywhere else. | 10 s |
| `validate-verdicts.sh` | `Stop` | When a turn dispatched a gate agent, the turn does not end until that gate's verdict block validates. | 45 s |

## Turning them off

Set an environment variable before you start Claude Code:

- `BR_HOOKS=off` turns off all three hooks.
- `BR_VERDICT_HOOK=off` turns off the verdict check only.
- `BR_CLAIMS_HOOK=off` turns off the marketing write gate only.

A hook that is off prints one line to stderr saying so. Every hook fails open: if it breaks or a
tool it needs is missing, your session continues and that hook checks nothing.

## What they need

- `bash` and `python3` on your PATH. Without `python3` the write gate and the verdict check do
  nothing. The `workforce-doctor` skill checks for it.
- On Windows, run Claude Code with Git Bash available (Git for Windows), since the hooks are bash
  scripts.
