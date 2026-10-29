# Updating Your BlackRaptor Workforce

*BlackRaptor Workforce alpha — updating installed packs. Covers the alpha packs: Core,
Engineering, Council, Hardware, Marketing. Last updated 2026-10-26.*

Claude turns automatic updates **off by default** for marketplaces that Anthropic doesn't run,
including ours — so unless you've switched auto-update on for the BlackRaptor marketplace,
updates won't reach you on their own. Either way, a new pack version won't appear in a
conversation that's already running. This page shows you how to update, on both surfaces.

> **Coming from 2.8.3: update the plugins; plugin-mode repos with a recorded test command need nothing else, copy-mode
> repos run /workforce-init --upgrade once.** See [2.8.4](#284--what-changed-and-what-you-must-update). Coming from an older version: 2.8.3 needs
> /workforce-init --upgrade in each repo (run it from your own terminal); until then test-auditor and completion-auditor
> passes may be blocked. See [2.8.3](#283--what-changed-and-what-you-must-update).

## 2.0.0 — what changed, and what you must update

**2.0.0 is a breaking release across all five packs.** Nothing you have installed stops working,
but two things you may have written yourself will need updating.

**Gates are strict by design.** `CONCERNS` with a list of conditions is the common verdict on sound work — `PASS` is not the default and a `CONCERNS` is not a sign something is wrong with your change. Read the conditions, meet the ones that matter, and record the decision.

### 1. The gate verdict block changed shape

If you keep Change Records, the machine `verdict` blocks in them are now validated against a new
schema and **existing blocks will fail** until re-emitted. What changed:

| Field | Was | Is |
|---|---|---|
| `confidence` | `"high"` / `"medium"` / `"low"` | an **integer 0-10** |
| `standards` | did not exist | **required** — each entry gives the designation, edition, clause, how you reached the text, and the date you verified it; or the single literal `"none: practice applied: <x>"` |
| `evidence` | an array of strings | a **string** |
| `verdict` | included `N/A` | `N/A` **removed** — a gate that does not apply emits no block, and the Change Record row carries the N/A |

You do not need to rewrite old records unless CI re-validates them. New reviews produce the new
shape automatically. If you copied the Change Record template into your repo, take the updated one.

### 2. A new Stop hook validates gate verdicts in your session

Core now ships a `Stop` hook. When a turn dispatched a gate agent, the turn does not end until that
gate's verdict block validates. Before this, the validator only ever ran in a CI workflow you had to
install yourself — so on a marketplace install nothing checked the contract at all.

**If it gets in your way, turn it off:** set `BR_VERDICT_HOOK=off` in your environment. When
disabled, the hook writes one line to stderr. Interactive sessions show it; `claude -p` does not
surface hook stderr, so on that path check the `BR_VERDICT_HOOK` variable instead. It fails closed on its own
errors (D-267): a crash blocks the turn with "the verdict check crashed (...): this turn is not gated; report it",
and a missing python3 or helper prints "gates in this turn are NOT checked" on every stop. It judges every stop, including the one after it blocked, so a re-emitted block is checked too; it
blocks at most 3 times in one turn (4 when the first block came from the shell wrapper answering for a check that could not;
a damaged background-task notice in the transcript can give one turn a second count of three blocks, a known limit to be fixed in 2.8.5),
and after that it lets the turn end with a message that starts
"Verdict check FAILED and was not fixed:", so the failure is on record.

### 3. Two gate seats moved (Engineering pack)

A gate that can edit what it judges is not a gate, so two seats were split:

- **Schema sign-off** moved from `data-engineer` to the new read-only **`schema-reviewer`**.
- **Test/coverage sign-off** moved from `qa-test-engineer` to the new read-only **`test-auditor`**.

`data-engineer` and `qa-test-engineer` are unchanged as producers and keep their tools. **If you
dispatch gates by name, update those two call sites.** `seat-list.md` in the pack is already updated.

### 4. Some seats can now run their own arithmetic

The four hardware analysis seats and the four council numbers seats now hold `Bash` (the hardware
seats also hold `Write`, restricted to the program's `sim/` directory). Every figure they compute
carries its script and inputs and is **re-executed by a context that did not produce it** before it
is used. If your workflow assumed these seats were read-only, they are not any more — the write
target is charter-restricted, but the grant is real.

### 5. The retired-claims list moved (Marketing pack)

`claims-gate` no longer carries the banned-claims list in its body; it reads **§4b of your
`MARKETING-CONTEXT.md`**. If you maintain that file, add the §4a/§4b tables from the template — the
gate returns COULD NOT ASSESS for the retired-claims check if it cannot find the register, rather
than guessing.

## 2.1.0 — what changed, and what you must update

### 1. `product-marketing` moved from the Engineering pack to the Marketing pack

If you have an **engineering-only install** (no Marketing pack), you no longer have this agent.
Release notes, positioning, and regulated-claim review for shipped features now route to the
Marketing pack's `product-marketing` agent when that pack is installed alongside; otherwise the
main session drafts the comms itself and you gate them before anything ships. If you dispatch it by
name in a script or a Change Record template, install `blackraptor-marketing` or update the call
site to the guarded fallback.

### 2. The DRAFT/GATED file convention is now mechanical (Marketing pack)

Marketing asset producers (and `product-marketing`, `product-docs-writer`) write an asset as
`<name>.DRAFT.md`; it becomes `<name>.md` only once the isolated `claims-gate` agent has written a
validating `<name>.verdict.md` holding a claims-gate PASS, written in the same turn as the asset (a CONCERNS verdict is a HOLD:
fix the copy and gate it again; an approval from an earlier turn does not clear new copy). Two new controls enforce
it, both scoped to a directory your session has marked with a `.br-assets` file (written by the
`marketing-campaign` skill at campaign start) — outside a marked directory neither one judges asset
writes (the hooks README lists what the write gate still checks everywhere):

- A **PreToolUse hook** refuses an ungated `Write`/`Edit` of the final `.md` inside a marked
  directory. **Kill switch:** `BR_CLAIMS_HOOK=off`.
- The existing verdict `Stop` hook additionally blocks the turn if you wrote a `.DRAFT.md` under a
  marked directory and never dispatched `claims-gate` afterward in the same session. Same kill
  switch as before, `BR_VERDICT_HOOK=off`, covers this check too.

If either hook gets in your way on a non-marketing directory and the hooks README (beside the hooks in the installed Core
plugin) does not describe that block, that is a bug, so please report it.

### 3. The verdict hook now waits for a subagent still running in the background

Claude Code (measured on `claude_code_version` 2.1.258) can run a subagent dispatch in the
background and hand you its result later as a notification, instead of always waiting for it
inline. The verdict `Stop` hook did not know about that second path: it looked only at the
dispatch's immediate tool result, so a gate seat that was still finishing in the background looked
to the hook like a seat that never produced a verdict at all. The hook now also reads a
backgrounded seat's completed notification, and if the seat has not finished yet when your turn is
about to end, it blocks with a plain reason — "gate seat still running; wait for its result before
ending the turn" — rather than treating an in-progress dispatch as a missing one. No schema change,
no new kill switch: `BR_VERDICT_HOOK=off` still turns this check off along with the rest of the
verdict hook.

---

## 2.3.0 — what changed, and what you must update

### 1. Every verdict's evidence line now starts with a label

The verdict schema is now 3.1. The `evidence` string must open with one of `MEASURED`, `CITED`,
`COMPUTED`, `ESTIMATED` or `ASSUMED`, saying how the evidence was obtained. Gates emit the label on
their own. If you keep Change Records, a record that a pull request adds or changes is validated
against 3.1 once your copy of the validator updates, so add the label to any block you wrote by hand
(for example `"evidence":"CITED src/auth.ts:42 ..."`). Nothing else in the block changed.

### 2. The Tier-3 hook override has a new name (Engineering pack)

If you start sessions with `ALLOW_TIER3=1` to allow intentional Tier-3 edits, switch to
`BR_ALLOW_TIER3=1`. Since 2.8.0 the old name no longer overrides the hook.

### 3. One switch turns every Core hook off

`BR_HOOKS=off` turns off all five Core hooks at once. `BR_VERDICT_HOOK=off` and
`BR_CLAIMS_HOOK=off` still work for one hook each. No action needed unless you want it.

---

## 2.8.4 — what changed, and what you must update

### 1. Update the plugins; most repos need nothing else

Update the marketplace and the installed plugins. A repo installed with 2.8.3 in plugin mode (the default) that has a recorded test
command needs no re-run of `/workforce-init`: the hooks run from the plugin. One with no test command is still told at session
start to run `/workforce-init --upgrade`, as in 2.8.3; add `--test-cmd "<your test command>"`. A repo installed in copy mode keeps its own copies of the agents and skills (the gate hooks
run from the plugin in every mode), so run `/workforce-init --upgrade` there once, from your own terminal, to copy in the 2.8.4
versions; each session start says so until you do. A repo
installed before 2.8.3 still needs the 2.8.3 steps below.

### 2. Claude Code 2.1.288 or newer

The verdict check now blocks a turn that ran an agent when the agent's own transcript folder is missing ("subagent transcripts
are missing"). That folder was confirmed on Claude Code 2.1.288 and 2.1.296; an older client may not write it. Update Claude Code if yours is older; `/workforce-doctor` checks it.

### 3. What changed in the checks

- A folder the disk check cannot read is reported on every turn ("disk check skipped (a folder could not be read: ...)"), and
  marked folders inside git-ignored folders are now checked too, up to 8 levels deep and outside node_modules and Python
  environment and cache folders.
- The marketing write gate is built to answer within 9 of its 10 seconds when its helper hangs (a 7-second watchdog, then 1 second
  to stop the helper). When its helper is missing, crashes or runs out of time, it denies a write to a file named `.md` and a shell
  command that names a `.md` file, copies a folder, unpacks an archive, copies with a wildcard or is over 2048 characters long,
  until the helper works, without
  searching for marked folders; other calls pass (the hooks README lists what it cannot see).
- A marketing asset is cleared only by a claims-gate PASS in the verdict file beside it, and a verdict file counts only when it
  holds the block the gate returned, unchanged. If your workflow edited a gate's block before saving it, save it unchanged.
- A verdict counts only for the gate that was dispatched, wherever its result came from, and whether a test-auditor or
  completion-auditor pass needs CI is decided by the gate dispatched, not by the name in its block.
- A background gate whose result arrives after you sent another message is checked in that turn; an agent resumed with
  SendMessage has its own transcript checked.
- The verdict check answers within 840 of the Stop call's 900 seconds, and its shell watchdog by about 856, at least 30 seconds
  before the 900.
- A verdict validator that cannot run, or a gate's output file that cannot be read, blocks the turn and says which.
- A gate dispatched with no result at the end of a turn is reported as INCOMPLETE; the closing line counts only verdicts that
  passed the validator.
- A block lists every note and, past five problems, says how many more.

## 2.8.3 — what changed, and what you must update

### 1. Re-run the installer in each repo, from your own terminal

Run `/workforce-init --upgrade` once in each repo you installed with `/workforce-init` (or run the script it
prints from your own terminal if the sandbox is already on). It turns on the sandbox settings below, records
your test command, and, in plugin mode, records the enforcement files' fingerprints and your test runner
config. Without a recorded test command, a test-auditor or completion-auditor PASS is blocked with "no test
command recorded"; add one with `--upgrade --test-cmd "<your test command>"`. Record the test runner itself
(for example `python3 -m pytest`, `npx vitest run`, `go test ./...`, or `npm test` when the package.json test
script is a single jest, vitest, mocha or `node --test` command): a script, `make test` or `turbo test` has no
report the hook can read, so a PASS on it is blocked (section 3 below lists what to record instead). Until you
upgrade, each new session in that repo says so.

### 2. What the hooks can and cannot do

Hooks catch honest mistakes and shortcuts; they are not a security boundary on their own. With the sandbox
on, the enforcement files are protected: no agent's shell command can write them. `/workforce-init` now turns
on `sandbox.failIfUnavailable` (Claude Code will not start without the sandbox), turns off unsandboxed
commands, and lists every enforcement file in `sandbox.filesystem.denyWrite`. `--no-sandbox` opts out and says
what you give up. CI decides whether tests pass, on a clean machine, for the exact commit. The local check is
an early warning. Agents judge whether tests are strong. You decide. A test-auditor or completion-auditor PASS
stands only when GitHub Actions ran the workforce-proof workflow for the exact commit and both its jobs passed
(section 4); until then the review check says INCOMPLETE. Code under test that is written to cheat its own
tests runs inside CI too; it is visible in the diff, where code-reviewer and a person review it. Before CI is
asked, the hook runs your test command itself as an early warning, not by what the reviewer printed. That run
blocks a suite that runs no test or fails one; a test the change skips, rewrites
or deletes still runs in CI's base-suite.
When the runner config changes (the pytest, jest, vitest, mocha, karma and playwright config files, the pytest parts of pyproject.toml, setup.cfg and tox.ini, setup.py and pytest11 entry points, the test scripts and test-runner keys in package.json, files the test command names, and in an in-repo virtualenv or node_modules the startup files (.pth, sitecustomize.py, usercustomize.py), pytest plugin entry points, install state and the files a jest, vitest or mocha config names there), the PASS is blocked until a person reviews the change and runs
`/workforce-init --accept-runner-config` from their own terminal; the hooks README has the full list. Without
the CI judge (`--no-ci-judge`), anything else the test run loads can still be written to fake a pass; CI on every
pull request is the proof.
Tamper detection needs plugin mode: when a hook file, an allow
file or the hooks in `.claude/settings.json` change, the next stop blocks until you run `--upgrade` (add
`--replace-enforcement` for a changed hook file) or `--accept-changes` if you made the change. Without the
sandbox, the tamper check can also be edited, so it no longer protects you. Nothing in a session replaces CI:
CI should re-run the tests on every pull request.

### 3. Direct test commands

The hook needs a test command whose runner writes a machine report, so record the runner itself. You can record
several with `/workforce-init --upgrade --test-cmd "<first>" --test-cmd "<second>"`; each must pass.

| Your project | Record this | Not this (no machine report) |
|---|---|---|
| Python, pytest | `python3 -m pytest -q`, `.venv/bin/python -m pytest -q`, `uv run pytest -q`, `poetry run pytest -q` | `make test`, `nox`, a script |
| Python, tox | the pytest command tox runs, with that env's interpreter: `.tox/py/bin/python -m pytest -q` | `tox` |
| JavaScript, jest | `npx jest`, or `npm test` when the package.json test script is just `jest` | an `npm test` script that runs several tools |
| JavaScript, vitest | `npx vitest run` | |
| Node's own runner | `node --test` | |
| mocha | `npx mocha` | |
| Go | `go test ./...` | `make test` |
| Rust | none yet: `cargo test` has no report the hook reads; CI is the check | `cargo test` |
| .NET | `dotnet test` | |
| Java | `mvn test` or `./mvnw test` | `gradle test` (no reader yet) |
| Bun | `bun test` | |
| Monorepo: pnpm + turbo + vitest | `npx vitest run` with a vitest workspace file that lists the packages, or one entry per package: `--test-cmd "npx vitest run --root packages/a" --test-cmd "npx vitest run --root packages/b"` | `pnpm test`, `turbo test` |
| Monorepo: nx + jest | one entry per project: `--test-cmd "npx jest -c apps/web/jest.config.ts"` | `nx test`, `nx run-many` |

### 4. CI is the judge

2.8.3 adds `.github/workflows/workforce-proof.yml` to the engineering pack. Its two jobs run on GitHub Actions for
every push to a branch and every pull request: `head-suite` runs your recorded test commands on the commit as
pushed, installing only from your lockfile; `base-suite` runs them again with the base branch's own tests and
test-runner config put back. The review check reads those two results for the exact commit.

1. Run `/workforce-init --upgrade` from your own terminal (it installs the workflow and records its hash).
2. Commit and push; let both jobs run once.
   A repo cloned onto a second machine has no tamper baseline there. Any turn that dispatched an agent then blocks with
   "tamper baseline missing" until you run `/workforce-init --upgrade` from your own terminal; the session start says so.
3. From your own terminal: `/workforce-init --setup-branch-protection`. It asks GitHub to require `head-suite`
   and `base-suite` (up to date with the base) and one approving review, with stale approvals dismissed
   (`--dry-run` prints the call;
   the doctor reads back what GitHub set). It needs your admin login. On GitHub Free this needs a public
   repo or a paid plan for a private one.
4. Agents and the build account open pull requests and must not be admins on the repo. You approve every pull
   request and merge it; required checks and your approval gate the merge. GitHub does not let you approve
   your own pull request, so yours merge by an admin override, which GitHub shows as a bypass. Workforce no longer uses a code-owners file (D-258).
   GitHub counts one approval from anyone with write access. Keep write access to you and one agent or build
   account, so the approval is yours. Record them with `/workforce-init --upgrade --owner-login <your GitHub login>
   --agent-account <build account>`; from your own terminal, `/workforce-doctor` lists everyone with write, maintain or
   admin access and reports a FAIL when anyone else has it. Keep the repo setting "Allow GitHub Actions to create and
   approve pull requests" off.
5. Install and sign in to the GitHub CLI (`gh auth login`) where you run Claude Code: the review check reads CI
   with it.

No GitHub, or Actions off: a test pass stays INCOMPLETE. `/workforce-init --upgrade --no-ci-judge` makes this
machine's check the judge, and every result says it can be faked; `--ci-judge` turns CI back on.

**A pnpm + turbo + vitest monorepo.** CI runs the commands you record, not `pnpm test`. Record
one direct command per package, or one with a vitest workspace file:

```
/workforce-init --upgrade --test-cmd "npx vitest run --root packages/api" --test-cmd "npx vitest run --root packages/web"
```

Commit `pnpm-lock.yaml` and set `packageManager` in the root `package.json`; CI runs `pnpm install
--frozen-lockfile`. Each command must pass on its own, and a red package names itself ("command 2 of 2"). This
was run on GitHub with a two-package workspace: green passed both jobs; breaking one package failed both and named it.

### 5. Models and effort moved (22 Oct 2026)

Six agents now run on `opus` instead of `sonnet`: `ux-designer` (a gate), `product-manager`, and the council seats `revenue`, `gtm-strategy`,
`people-org` and `technology-strategy`. Every gate (17) now has `effort: high` in its own agent file, so a gate does not run thin because your
session is set low. `principal-architect` uses `model: best`, which Claude Code resolves to the strongest model your account has (Opus
if it has nothing stronger), with `effort: high`. No other agent has an `effort:` line, so your session's effort setting decides for them.

Cost effect: the six moved agents cost about twice as much per token (Sonnet 5.5 $2 in and $10 out per million tokens, Opus 5.5 $4 and $20); a gate may
run at a higher effort than your session; `principal-architect` on a model stronger than Opus costs more again (the top published tier is $10 and $50 per million).

To override: your session's effort setting for every agent without an `effort:` line; the environment variable `CLAUDE_CODE_EFFORT_LEVEL` for every agent,
gates included; `CLAUDE_CODE_SUBAGENT_MODEL` for a subagent's model when the call and the agent file name none. To pin the architect to Opus instead of
`best`, edit `principal-architect`'s frontmatter to `model: opus` and `effort: xhigh`. `/workforce-doctor` prints each gate's model and effort as the files
ask for them; it cannot see what a past run used.

## The one rule to remember

**A session keeps the pack versions it started with.** Updating doesn't retroactively change a
conversation already in progress — the same way a phone app finishes what it's doing and
applies its update on the next launch. On the command line you can pull changes into a running
session with `/reload-plugins`; in the Claude app, and any time you want certainty, just
**start a fresh session** after updating.

## Updating in the Claude app (Cowork)

1. Open the plugin settings (Settings → Plugins / Extensions).
2. Find the **blackraptor marketplace** entry and refresh/update it first. This re-reads the
   catalog. The per-pack **Update** buttons may stay grayed out until you do this step.
3. Update each BlackRaptor pack that shows an update: Core, Council, Hardware, Marketing.
4. **Start a new conversation.** The new session picks up the new versions; existing
   conversations keep the old ones.

## Updating on the command line (Claude Code)

Run these in order — the refresh must come first, or the update check can compare against a
stale catalog and report you are already current:

```bash
claude plugin marketplace update blackraptor
claude plugin update blackraptor-core@blackraptor
claude plugin update blackraptor-council@blackraptor
claude plugin update blackraptor-hardware@blackraptor
claude plugin update blackraptor-marketing@blackraptor
```

Then either run `/reload-plugins` in your session or — for certainty — restart it (exit and
start `claude` again).

If you installed a pack at **project scope** (tied to one repository), update it from inside
that project folder and add `--scope project` to the update command.

## Upgrading a repo install

If you ran `/workforce-init` in a repo, update the packs first (above), start a fresh session in the
repo, then run:

```
/workforce-init --upgrade
```

It reads `.claude/workforce-installed.json`, prints the files the new packs add, change and no longer
ship, updates the ones you have not edited (a file you changed is kept and named), rewrites the
installed list (and, in copy mode, the checksum file); the command then runs `workforce-doctor`. In copy mode
it stops before deleting any copy the new packs no longer ship and names it, with the pack it moved
to if it moved; nothing changes until you say yes. Add `--dry-run` to see the list without writing.

## How to check what you're running (about 10 seconds)

In a **fresh** session, say:

> run workforce-doctor

The doctor reports each installed pack and its version — compare those against the latest
release's `CHANGELOG.md` (shipped inside each pack) or the release announcement to see if
you're current. In a Cowork session it also reports the timestamp of the
session's pack snapshot, so you can see how old your session's copy is. If the doctor ever
reports **STALE SNAPSHOT — CANNOT CERTIFY**, that means packs were added or removed after your
session started — start a fresh session and run it again.

## Troubleshooting

- **The Update button is gray.** Refresh the *marketplace* entry first (step 2 above), then
  check the pack again. If the marketplace refresh itself fails or the buttons stay gray,
  remove and re-add the blackraptor marketplace. **Note: removing a marketplace also
  uninstalls the packs you installed from it** — after re-adding it, reinstall Core, Council,
  Hardware, and Marketing, then start a fresh session.
- **The command line says "already at latest" but you know there's a release.** Usually the
  marketplace refresh was skipped — run `claude plugin marketplace update blackraptor` and try
  again. If the refresh reports a failure, remove and re-add the marketplace — remember this
  uninstalls your packs, so reinstall them afterward.
- **An open conversation is acting like the old version.** It is — sessions keep their startup
  versions. Start a fresh conversation (or use `/reload-plugins` on the command line).
- **The doctor says STALE SNAPSHOT.** Working as intended: packs were added or removed after
  your session started. Start a fresh session.

## What's in each release

Each pack ships a `CHANGELOG.md` describing what changed. Every release bumps the pack
version — **we treat any content change as requiring a version bump**, so the version number
is your reliable signal of what you're running. If you ever suspect a pack changed without a
version bump, tell us: that's a defect on our side and we want to hear about it.
