# BlackRaptor Core hooks

The Core pack ships four hooks. Claude Code loads them from `hooks/hooks.json` when the pack is
installed; you do not wire anything yourself.

| Hook | Event | What it does | Timeout |
|---|---|---|---|
| `inject-onboarding-rule.sh` | `SessionStart` | Offers the first-run welcome when a project has no context file or no `USER-PREFS.md`. Silent once you are set up. | 10 s |
| `inject-session-contract.sh` | `SessionStart` | Off by default. With `BR_SESSION_CONTRACT=on` it adds the session contract (honor `USER-PREFS.md`, the context-review reminder, at most one preference suggestion per session) to each session, at a cost of about 270 tokens per turn. | 10 s |
| `enforce-draft-gate.sh` | `PreToolUse` (Write, Edit, MultiEdit) | In a folder marked for marketing assets only, blocks writing a final `.md` until a sibling `.verdict.md` exists that validates as PASS. Inert everywhere else. | 10 s |
| `validate-verdicts.sh` | `Stop` | When a turn dispatched a gate agent, the turn does not end until that gate's verdict block validates. A verdict block must name the agent that returned it. | 45 s |

## What the verdict check covers

- It checks the verdict block of every gate dispatched in the turn, and every `.verdict.md` file written
  in the turn, including files a subagent writes in its own run. A verdict file must carry a block that a
  dispatch of that same agent returned in the turn.
- It does not check a verdict block the main session writes in its own reply. Only a gate's verdict
  counts.
- It runs in print mode (`claude -p`) as well as interactive sessions.
- After a clean turn that dispatched gates it prints one line: "BlackRaptor verdict check: gates checked
  N, verdicts valid N." A turn with no gate prints nothing.

## Turning them off

Set an environment variable before you start Claude Code:

- `BR_HOOKS=off` turns off all four hooks.
- `BR_SESSION_CONTRACT=on` turns the session-contract hook on (it is off by default).
- `BR_VERDICT_HOOK=off` turns off the verdict check only.
- `BR_CLAIMS_HOOK=off` turns off the marketing write gate only.

A hook that is off prints one line to stderr saying so. Every hook fails open: if it breaks or a
tool it needs is missing, your session continues and that hook checks nothing.

## Engineering: the files your CI reads

The engineering pack's Change Record check (`change-record-required.yml`) runs in your repo's CI, not
in Claude Code, so it reads the verdict validator from your repo. A plugin install does not put it
there. Copy `validate_verdict.py` and `verdict-schema.json` from this pack's
`skills/gate-verdict-format/` into `.claude/skills/gate-verdict-format/` in your repo and commit them;
without them the check fails closed. The engineering pack's `CUSTOMIZATION.md` (step 1) lists every
file to copy.

## What they need

- `bash` and `python3` on your PATH. Without `python3` the write gate and the verdict check do
  nothing. The `workforce-doctor` skill checks for it.
- On Windows, run Claude Code with Git Bash available (Git for Windows), since the hooks are bash
  scripts.
