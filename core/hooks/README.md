# BlackRaptor Core hooks

The Core pack ships four hooks. Claude Code loads them from `hooks/hooks.json` when the pack is
installed; you do not wire anything yourself.

| Hook | Event | What it does | Timeout |
|---|---|---|---|
| `inject-onboarding-rule.sh` | `SessionStart` | Offers the first-run welcome when a project has no context file or no `USER-PREFS.md`. Silent once you are set up. | 10 s |
| `inject-session-contract.sh` | `SessionStart` | Off by default. With `BR_SESSION_CONTRACT=on` it adds the session contract (honor `USER-PREFS.md`, the context-review reminder, at most one preference suggestion per session) to each session, at a cost of about 270 tokens per turn. | 10 s |
| `enforce-draft-gate.sh` | `PreToolUse` (Write, Edit, MultiEdit, Bash) | In a folder marked for marketing assets only, blocks writing a final `.md`, with the Write tool or a shell command (cp, mv, a redirect, an archive extract), until a sibling `.verdict.md` exists that validates as PASS. Everywhere, blocks a Bash command that writes a `.verdict.md` file: verdict files are written with the Write tool so the gate check can read them. | 10 s |
| `validate-verdicts.sh` | `Stop`; also `UserPromptSubmit` and `PostToolUse` (Bash) to record verdict and asset files on disk | When a turn dispatched a gate agent, the turn does not end until that gate's verdict block validates. A verdict block must name the agent that returned it. A verdict file, or an asset under a marked folder, that appeared or changed in the turn with no Write or Edit of it blocks the turn. | 45 s (Stop), 20 s (snapshots) |

## What the verdict check covers

- It checks the verdict block of every gate dispatched in the turn, and every `.verdict.md` file written
  in the turn with the Write or Edit tool, including files a subagent writes in its own run. A verdict
  file must carry a block that a dispatch of that same agent returned in the turn.
- A `.verdict.md` file that any Bash command in the turn names (a write, or a read such as `cat`) is
  unverified: with no Write or Edit of it in the turn, it blocks as "verdict file not produced by a gate
  dispatch this turn". Read verdict files with the Read tool.
- It does not check a verdict block the main session writes in its own reply. Only a gate's verdict
  counts: a block signed by an agent that is not a gate (or a council seat) is rejected as "not a gate
  agent", inline or in a verdict file. The gate list is `gates` in the core pack's
  `skills/gate-verdict-format/verdict-schema.json`; a project adds its own gates to
  `.claude/gates-allow.txt`, one name per line (a Tier-3 file: agents cannot edit it).
- It runs in print mode (`claude -p`) as well as interactive sessions.
- A verdict whose evidence opens with MEASURED must name, in backticks, a command that a Bash call in
  this session actually ran: in the main conversation (any turn so far) or in any subagent's own run.
  The backticked text must be that command: every part of it, its program and all its arguments, with
  nothing added, and at least 8 characters long unless it is exactly one command that ran (`go test`,
  `pytest`). Quoting one step of a longer command line is fine.
  If none of its backticked commands was run, the turn is blocked with "MEASURED command not executed
  in this session". A command that exited non-zero still counts as run.
- A gate dispatched in the background is checked when its completion notice arrives, in the same turn
  or a later one. A gate with no result and no notice yet blocks as "still running".
- After a clean turn that dispatched gates it prints one line: "BlackRaptor verdict check: gates checked
  N, verdicts valid N; measured: N runs matched, M non-zero." A turn with no gate and no verdict or
  asset file touched prints nothing; a turn with no gate that reads a verdict file with Bash, or changes
  one, still blocks, and the message says why.

## Turning them off

Set an environment variable before you start Claude Code:

- `BR_HOOKS=off` turns off all four hooks.
- `BR_SESSION_CONTRACT=on` turns the session-contract hook on (it is off by default).
- `BR_VERDICT_HOOK=off` turns off the verdict check only.
- `BR_CLAIMS_HOOK=off` turns off the marketing write gate only.

A hook that is off prints one line to stderr saying so. Every hook fails open: if it breaks or a
tool it needs is missing, your session continues and that hook checks nothing.

These switches are for you, not for the agents. A block message never offers them: it tells the agent
to stop and report to you why it thinks the block is wrong, and leaves the decision to you.

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
