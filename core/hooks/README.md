# BlackRaptor Core hooks

The Core pack ships five hooks. Claude Code loads them from `hooks/hooks.json` when the pack is
installed; you do not wire anything yourself.

| Hook | Event | What it does | Timeout |
|---|---|---|---|
| `inject-onboarding-rule.sh` | `SessionStart` | Offers the first-run welcome when a project has no context file or no `USER-PREFS.md`. Silent once you are set up. | 10 s |
| `inject-session-contract.sh` | `SessionStart` | Off by default. With `BR_SESSION_CONTRACT=on` it adds the session contract (honor `USER-PREFS.md`, the context-review reminder, at most one preference suggestion per session) to each session, at a cost of about 270 tokens per turn. | 10 s |
| `upgrade-notice.sh` | `SessionStart` | When this repo's install record is older than the running Core pack or has no test command, tells you once per session: "Workforce <version> needs /workforce-init --upgrade in this repo (run it from your own terminal). Until then test-auditor and completion-auditor passes are blocked." Silent otherwise. | 10 s |
| `enforce-draft-gate.sh` | `PreToolUse` (Write, Edit, MultiEdit, Bash) | In a folder marked for marketing assets only, blocks writing a final `.md`, with the Write tool or a shell command (cp, mv, a redirect, an archive extract), until a sibling `.verdict.md` exists that validates as PASS. Everywhere, blocks a Bash command that writes a `.verdict.md` file: verdict files are written with the Write tool so the gate check can read them. | 10 s |
| `validate-verdicts.sh` | `Stop`; also `UserPromptSubmit` and `PostToolUse` (Bash) to record verdict and asset files on disk | When a turn dispatched a gate agent, the turn does not end until that gate's verdict block validates. A verdict block must name the agent that returned it. A verdict file, or an asset under a marked folder, that appeared or changed in the turn with no Write or Edit of it blocks the turn. A test-auditor or completion-auditor PASS is checked by the hook's own run of your test command. | 900 s (Stop; it may run your tests), 20 s (snapshots) |

## What the hooks can and cannot do

Hooks catch honest mistakes and shortcuts; they are not a security boundary on their own. With the sandbox
on, the enforcement files are protected: no agent's shell command can write them (measured on Claude Code
2.1.296 for the main session, the built-in general-purpose and `claude` agents, and every pack agent with a
shell). `/workforce-init` turns the sandbox on by default. CI decides whether tests pass, on a clean machine,
for the exact commit. The local check is an early warning. Agents judge whether tests are strong. You decide.
A test-auditor or completion-auditor PASS stands only when GitHub Actions ran the workforce-proof workflow for
the commit and both its jobs passed (see "CI is the judge" below); the hook's own run of your test command
comes first and blocks a red suite at once. Code under test that is written to cheat its own tests runs inside
CI too; it is visible in the diff, where code-reviewer and a person review it. Tamper detection needs plugin mode, and without the sandbox the tamper check can also be edited.

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
  `.claude/gates-allow.txt`, one name per line (with the sandbox on, no agent's shell command can write it;
  without the sandbox, an agent with a shell can).
- It runs in print mode (`claude -p`) as well as interactive sessions.
- A verdict whose evidence opens with MEASURED must name, in backticks, a command that a Bash call in
  this session actually ran: in the main conversation (any turn so far) or in any subagent's own run.
  The backticked text must be that command: every part of it, its program and all its arguments, with
  nothing added, and at least 8 characters long unless it is exactly one command that ran (`go test`,
  `pytest`). Quoting one step of a longer command line is fine.
  A path may differ only in form: absolute or relative to the repo, with or without a leading `./`, or
  shortened to its last two parts (`scratchpad/probe.py`); a `<name>` placeholder stands for one word.
  If none of its backticked commands was run, the turn is blocked with "MEASURED command not executed
  in this session", naming the nearest command that did run. A cited path may be shortened (D-225,
  D-238, D-248): repo-relative or absolute, a leading `…/` or `.../` for any prefix, `<name>` for one whole
  argument or one path segment, but at least one folder of the cited path must be written out
  (`…/scratchpad/probe.py`, not `…/probe.py` or `<dir>/check.py`). A script matches by its basename alone
  only when the run reached it through a shell variable or substitution the hook cannot expand (`bash
  $S/mutants.sh`, `python3 $(pwd)/probe.py`); never another runner or another script name. A command that exited non-zero still counts
  as run. A command written over several lines is read as the separate commands its lines hold. This shows
  a command ran, not what it proved.
- CI is the judge (D-252). For a test-auditor or completion-auditor PASS the hook first runs your test command
  locally (the early warning below). If that passes, it reads GitHub once (20 s at most, with `gh`, outside the
  sandbox) for the current `HEAD`: the work tree must have no uncommitted change, `HEAD` must be on GitHub, the
  workforce-proof workflow file in that commit must match the hash `/workforce-init` recorded, and that
  workflow's own `head-suite` and `base-suite` check runs for the commit (app `github-actions`, the run's check
  suite) must have concluded success. Commit statuses are never read; a check run with the same name from
  another workflow or app does not count. Outcomes: both passed → the PASS stands ("CI passed for <sha>");
  still running → "Verdict check INCOMPLETE: tests: waiting on CI for <sha>; the gate is not passed yet" (the
  turn may end; a later turn re-reads CI); a job failed → blocked, naming the job and its URL; not pushed or
  uncommitted changes → INCOMPLETE "commit and push; CI decides"; `gh` missing, offline or not signed in →
  INCOMPLETE with the reason. head-suite runs the commit as pushed on a clean runner, installing only from the
  lockfile; base-suite puts back the base branch's test files and runner config first and removes the test
  files the change added, so the base branch's own tests judge the new code. The test commands come from the
  install record at the merge base, so a change cannot pick its own. When the base branch has no install record
  (the first Workforce pull request) both jobs fail and the review check ends INCOMPLETE "base branch has no
  Workforce install record; the first Workforce pull request is approved by the owner on review, not by CI";
  when the base branch has no test files, base-suite fails "no base tests to run" and the review check ends
  INCOMPLETE: the owner's review decides that pull request (D-261). Every workforce-proof run for the commit
  (the push run and the pull-request run) must be complete: one still running is INCOMPLETE, and a failed,
  cancelled or timed-out job in any of them blocks (D-262). The base the review check uses is the open pull request's
  base branch (read with `gh pr view --json baseRefName`, outside the sandbox) when the current branch has one, else the default
  branch, and the message says which ("base used: ..."). CI's pull-request run uses the pull request's base, so a CI run that judged a
  different base than this check used leaves the check INCOMPLETE, never a PASS; a base that is not in this clone is INCOMPLETE until
  you fetch it (D-275).
- No GitHub remote, or `/workforce-init --no-ci-judge` (D-254): with no remote a quality PASS is INCOMPLETE
  "no CI judge for this repo". `--no-ci-judge` makes the local run the judge and every clean line says "No CI
  judge: test passes are checked only on this machine, where an agent can fake them. Use CI for real proof."
  Without the CI judge, anything else the test run loads can still be written to fake a pass; CI on every
  pull request is the proof.
- Agents never merge. A person merges once CI and the gates pass; `/workforce-init
  --setup-branch-protection` (from your own terminal) asks GitHub to require `head-suite` and `base-suite` (up
  to date with the base) and one approving review with stale approvals dismissed (D-253, D-260);
  `--dry-run` prints the exact call. Agents and the build account open pull requests and must not be admins; the
  owner approves and merges, and merges their own pull requests by an admin override, which GitHub shows as a
  bypass.
  GitHub counts one approval from anyone with write access. Keep write access to you and one agent or build
  account, so the approval is yours (D-273): `/workforce-init` records your GitHub login and the agent or build
  account name (`--owner-login`, `--agent-account`) in the install record, and `/workforce-doctor`, from your own
  terminal, lists everyone with write, maintain or admin access to the repo and reports a FAIL when anyone other
  than those accounts has it. Keep the repo setting "Allow GitHub Actions to create and approve pull requests" off.
  GitHub applies it only with an admin login and a plan that allows it; the doctor reads back what is set.
- The local early warning: a test-auditor or completion-auditor PASS is checked by the hook's own run of your test command: the
  `test_cmd` that `/workforce-init` recorded in `.claude/workforce-installed.json`. The run must exit 0 and
  its machine report must show at least 1 passed and 0 failed or errored. What the gate printed is never
  read for this. The hook asks the runner for its machine report (pytest, jest, vitest, go test, node --test,
  mocha, bun test, dotnet test, maven; `npm test`, `pnpm test` or `yarn test` when the package.json test
  script is one of those, alone), written to a folder the hook owns outside the repo. `uv run`, `poetry run`,
  `pipenv run`, `hatch run`, `pdm run` and `rye run` in front of one of those runners are read through, with
  the wrapper's own flags; a wrapper flag that takes a value is not parsed, so that command has no report
  (D-246). A command with no machine report (a script, `make test`, `turbo test`, `nx test`, `tox`, `cargo
  test`) cannot carry a PASS: it blocks with "the test command `<cmd>` has no machine report the hook can
  read; record a direct runner command" and names the "Direct test commands" table below (D-234, D-246), and
  `.claude/test-summary-patterns.txt` no longer makes one pass. `test_cmd` may be a list (give
  `/workforce-init --test-cmd` more than once): every command must have a machine report and pass, and the
  counts add; the block names the command that failed ("command 2 of 2: ..."). No recorded command blocks
  with "no test command recorded; run /workforce-init". The run uses `NO_COLOR=1`, `FORCE_COLOR=0` and
  `CI=1`: CI is the reference, so a test that passes only under `CI=1` passes here too (D-235). It runs for
  at most `test_timeout` seconds (default 300, capped at 600 so the whole hook finishes inside its 870-second budget; past that it blocks with "test run exceeded N s; raise
  test_timeout or split the suite"). On macOS the run cannot write the enforcement files (`sandbox-exec`);
  elsewhere it is not confined, and the clean line says so. If the recorded command names test files, one
  must reach the change: a changed file, its folder, or a file that imports it directly or through a package
  `__init__.py` or `index.js`; a test file counts as changed only when the change adds a test case to it.
  The change is measured against `origin/HEAD`, else the upstream branch, else main, master, trunk or
  develop. A heredoc body is not a command that ran unless the heredoc feeds a shell or interpreter.
- Test runner config (D-233). Before that run can carry a PASS, the files that steer the runner must match
  what a person last accepted. The list is one constant, `RUNNER_CONTROL` in `validate-verdicts.py` (the
  installer keeps the same list): every `conftest.py`, `pytest.ini`, `.pytest.ini`, `pytest.toml`,
  `.pytest.toml`, `sitecustomize.py`, `usercustomize.py` and `*.pth` at any depth; `jest.config.*`,
  `vitest.config.*`, `vitest.workspace.*`, `vite.config.*`, `.mocharc*`, `karma.conf.*` and
  `playwright.config.*` at any depth; the `[tool]` and `[tool.pytest*]` tables of `pyproject.toml`,
  `[tool:pytest]` in `setup.cfg` and `[pytest]` in `tox.ini` (only those parts); in `package.json` the
  scripts named `test*`, `pretest*` and `posttest*` and the `jest`, `mocha`, `ava` and `vitest` keys (only
  those); `setup.py` (the whole file) and the `pytest11` entry points in `pyproject.toml`
  (`[project.entry-points."pytest11"]`, `[tool.poetry.plugins."pytest11"]` and any line naming `pytest11`)
  and in `setup.cfg` (an `entry_points` or `options.entry_points` section naming `pytest11`); and any repo
  file the test command names (test files aside). The walk skips `.git`, `node_modules`, `.venv`, `venv`,
  `__pycache__`, `.pytest_cache`, `.tox` and `.mypy_cache`, but reads these files inside the in-repo
  environments (D-243): in every `.venv`, `venv`, `.tox/<env>` and any folder holding `pyvenv.cfg`, and in
  the virtualenv the test command's interpreter lives in even when it is outside the repo, each
  `site-packages` folder's `*.pth`, `sitecustomize.py` and `usercustomize.py`, and every
  `*.dist-info/entry_points.txt` or `*.egg-info/entry_points.txt` with a `[pytest11]` section (entry points
  are skipped in a `site-packages` with more than 5,000 entries; the startup files are always read); in
  every `node_modules` folder its install state (`.package-lock.json`, `.modules.yaml`, `.yarn-state.yml`);
  and every file inside `node_modules` that a jest, vitest or mocha config names as `setupFiles`,
  `setupFilesAfterEnv`, `globalSetup`, `globalTeardown`, `reporters`, `reporter`, `testRunner` or
  `require`. An ordinary package install changes none of these unless it ships a startup file or a pytest
  plugin; `npm install`, `pnpm install` and `yarn install` change the install state, so they block until
  accepted. In plugin mode
  the accepted state is in the tamper baseline under the core plugin's data folder, written at install and
  `--upgrade`; an added, changed or removed input blocks with "test runner config changed since it was last
  accepted: <files>. A person must review it, then run /workforce-init --accept-runner-config from their
  own terminal." A plugin-mode repo with a test command and no recorded runner config (installed before
  2.8.3, or a plugin bump with no re-init) is recorded by the hook itself on its first quality PASS, which
  prints once "Workforce recorded this repo's test runner config for the first time. Review it with
  /workforce-doctor; from now on a change to it needs /workforce-init --accept-runner-config." and goes on to
  its own run and then CI, as for any quality PASS (D-245). The hook does that only when the sandbox protects the install record,
  or when the baseline already has an entry for this repo path from an earlier install; otherwise it still
  blocks with "no accepted test runner config for this repo; run /workforce-init --upgrade from your own
  terminal". When the baseline file itself is missing (D-270: nothing from 2.8.3 was ever installed or
  upgraded for this machine, or the file was deleted) the hook records nothing and a turn that dispatched an agent
  (a gate or not) blocks with "tamper baseline missing: run /workforce-init --upgrade from your own terminal"; a turn that
  dispatched no agent is not affected. Copy mode compares with the merge base of the base branch instead, which is weaker: an agent can
  rewrite git refs. The in-repo environments are not in git, so copy mode does not check them.
- Known limit of the local run (D-235, D-244). The tests, the code under test and the contents of installed packages (in
  `.venv` or `node_modules`, beyond the files listed above) run inside the hook's run, so any of them can
  still be written to forge a pass (for example by rewriting the report on exit). Anything else the test run
  loads can still be written to fake a pass; CI on every pull request is the proof.
- A run's result is reused only by a later stop in the same turn (the same last message from you), and for
  at most 10 minutes; a new turn runs the tests again (D-249). Within that window the key is the test
  commands, their timeout, every tracked and untracked file's content, the runner config above, and the
  path, size and modified time of every git-ignored file in the repo (the skipped folders above aside; with
  more than 2,000 such files, nothing is reused). Files outside the repo are not in the key, so a test that
  reads one can pass on a stale result only inside that window.
- In plugin mode, `/workforce-init` records the sha256 of every enforcement file (`.claude/hooks/`, the
  sandbox's `denyWrite` files, the hooks in `.claude/settings.json`) in the core plugin's data folder. Every
  stop compares them; a difference blocks with "enforcement file changed this session: <file>; run
  /workforce-init --upgrade to restore, or --accept-changes if you made it" (for a changed hook file,
  `--upgrade` stops and names it; add `--replace-enforcement` to put the pack's copy back). With the sandbox
  on, run these from your own terminal: a session's shell commands cannot write those files. Copy mode has
  no protected place for that record, so it has no tamper check.
- A `completion-auditor` dispatch whose prompt opens with the line `MODE: ladder-only (no verdict)` runs
  the check ladder and owes no verdict (D-237); `/gate-review`, `/pre-merge`, `/red-team` and `dev-team`
  wave 2b use it. Any verdict block such a dispatch returns is ignored and never counts as a PASS. The
  marker means nothing on any other gate.
- It checks every stop, including the one right after it blocked, so a re-emitted block is judged too. It
  blocks at most 3 times in one turn; on the next stop with problems it lets the turn end and prints them
  in a message that starts "Verdict check FAILED and was not fixed:". If the only problem is a reviewer
  still running, the message says "Verdict check INCOMPLETE" instead.
- A gate dispatched in the background is checked when its completion notice arrives, in the same turn
  or a later one. A gate with no result and no notice yet blocks as "still running".
- After a clean turn that dispatched gates it prints one line: "BlackRaptor verdict check: gates checked
  N, verdicts valid N; measured: N runs matched, M non-zero." A turn with no gate and no verdict or
  asset file touched prints nothing; a turn with no gate that reads a verdict file with Bash, or changes
  one, still blocks, and the message says why.

## Direct test commands

The hook needs a command whose runner writes a machine report. Record the runner itself (D-246):

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

## Turning them off

Set an environment variable before you start Claude Code:

- `BR_HOOKS=off` turns off all five hooks.
- `BR_SESSION_CONTRACT=on` turns the session-contract hook on (it is off by default).
- `BR_VERDICT_HOOK=off` turns off the verdict check only.
- `BR_CLAIMS_HOOK=off` turns off the marketing write gate only.

A hook that is off prints one line to stderr saying so. The two hooks that guard a gate, the verdict
check and the marketing write gate, fail closed (D-267): if one breaks or a tool it needs is missing, it
says so instead of passing quietly. The verdict check blocks the turn with "the verdict check crashed
(...): this turn is not gated; report it"; after three blocks in one turn (one, when the shell wrapper had to
answer for the helper) it ends with a "Verdict check FAILED" message, so it cannot loop. If python3, the helper or the validator is missing, it prints
"gates in this turn are NOT checked" on every stop, and `/workforce-doctor` reports a FAIL. The write gate
denies a write under a marketing-asset folder when its check cannot run, and lets other writes through with one
line on stderr. The three hooks that only inform (onboarding, session contract, upgrade notice) still fail open:
they cannot affect a PASS.

Each gate hook also has its own deadline, below the client's timeout (D-278), because Claude Code cancels a hook that
outlives its timeout and lets the turn end, or the write through, without a word. We measured this on client 2.1.296 by running a throwaway
install whose hook slept past its timeout: the client cancelled it and the turn ended, or the write went through, with no message. It is our
measurement, not a documented guarantee, and you can repeat it on your client with the same test. The verdict check answers within 870
of the Stop call's 900 seconds (12 of 20 for the snapshot calls); the write gate within 7 of its 10. At the deadline the
verdict check blocks the turn with "the verdict check ran out of time (<step>): this turn is not gated; report it" (a
systemMessage on a snapshot call), and the write gate denies a marked write with "the claims-gate check ran out of time:
this write is not allowed; report it". A shell watchdog a few seconds later does the same if the helper cannot answer
at all. The disk check lists files with git, so a large repo is still checked; where it cannot run (no git and a large
tree, or a huge marked folder) the Stop says "disk check skipped (<reason>): verdict files and marked assets written
outside the Write tool are not checked this turn", and `/workforce-doctor` warns.

How a gate can be off, and what is left (the list is complete):
- The kill switches above (BR_HOOKS=off, BR_VERDICT_HOOK=off, BR_CLAIMS_HOOK=off). Announced on stderr.
- The plugin disabled or not installed. Claude Code then runs none of its hooks and nothing is said; `/workforce-doctor`
  shows what is installed.
- CI as the judge of tests. The hook's own test run is an early warning; GitHub's `head-suite` and `base-suite` decide.
- Limits that remain: a hook killed from outside (the machine sleeps, the process is killed, the client crashes) cannot say
  anything; the disk check does not look inside git-ignored folders outside a marked folder; and the deadlines were measured
  on client 2.1.296 only (the test is described above).

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
