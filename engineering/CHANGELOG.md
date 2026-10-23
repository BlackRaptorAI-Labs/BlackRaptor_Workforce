## 2.8.3 — 2026-10-19 — Read-only reviewers cite runs instead of being told to make them

Reviewers without a shell are never told to run checks and cite the completion audit's run instead, test-auditor can pass on that cited run, security-architect fails an exploitable finding unless the Change Record accepts the risk, completion-auditor fails any claim it could not verify, and a reviewer flags the cheap checks as not run only when it could have run them.
CI decides whether tests pass, on a clean machine, for the exact commit. The local check is an early warning. Agents judge whether tests are strong. You decide. The new workforce-proof workflow (head-suite and base-suite) is that CI judge; /gate-review, /pre-merge and dev-team now tell the session to push the branch before the quality gates and to report the CI state per gate (run live for /gate-review). Code under test that is written to cheat its own tests runs inside CI too; it is visible in the diff, where code-reviewer and a person review it. test-auditor's and completion-auditor's passes are also checked first by the review check's own run of your test command, an early warning that blocks a suite that runs no test or fails one, and blocks when the runner config changes (the pytest, jest, vitest, mocha, karma and playwright config files, the pytest parts of pyproject.toml, setup.cfg and tox.ini, setup.py and pytest11 entry points, the test scripts and test-runner keys in package.json, files the test command names, and in an in-repo virtualenv or node_modules the startup files (.pth, sitecustomize.py, usercustomize.py), pytest plugin entry points, install state and the files a jest, vitest or mocha config names there). Without the CI judge (--no-ci-judge), anything else the test run loads can still be written to fake a pass; CI on every pull request is the proof.
/gate-review, /pre-merge, /red-team and dev-team mark the completion-auditor dispatch that only runs the check ladder, so it owes no verdict, and the Tier-3 hook now says it is an early warning: with the sandbox on, no agent's shell command can write the enforcement files.
The code-owners template and every code-owners step are removed: the owner approves every pull request, while write access stays with the owner and one agent account (the branch-protection checklist says how), and required checks and the owner's approval gate the merge. /workforce-init --setup-branch-protection now asks for one approving review with stale approvals dismissed and the last push approved, both CI checks on a branch up to date with the base, and no code-owner rule; agents and the build account open pull requests and are not admins.
A pull request whose base branch has no Workforce install record, or no tests, is decided by your review, and workforce-proof says so instead of passing or failing it. Every CI run for the commit must finish and pass, and a report folder with a file that cannot be read gives no count. GitHub counts one approval from anyone with write access: keep write access to you and one agent or build account so the approval is yours, record them with /workforce-init --owner-login and --agent-account, and keep the repo setting "Allow GitHub Actions to create and approve pull requests" off. The enforcement map's Schema and CI/CD rows now say Partial and name what covers them (the Tier-3 hook, change-record-required when you make it a required check, and your approval), and a check keeps the template and the skill's map in step.
A 2.8.3 repo opened on a machine that has no tamper baseline for it (a fresh clone) blocks any turn that dispatched an agent with "tamper baseline missing"; run /workforce-init --upgrade from your own terminal, and the session start says so. The approval is the owner's only while write access stays with the owner and one agent account: the doctor warns on a second agent account and fails when GitHub Actions can approve pull requests. The unqualified sentences "the owner approves every pull request" now carry that condition.
Models and effort: `ux-designer` (a gate) moves from `sonnet` to `opus`, and its sonnet exception is retired; all 12 gates in this pack gain `effort: high`; `principal-architect` uses `model: best` with `effort: high` (the strongest model your account has, else Opus); `legal-docs-writer`, `product-designer` and `security-operations` stay on `opus` with no `effort:` line; the `dev-team` skill shows model and effort in its cost quote and tells the main session not to pass `model` or `effort` when it dispatches a gate. Cost: `ux-designer` runs at about twice the price per token; override as in UPDATING, section 5.

## 2.8.2 — 2026-10-16 — Agents stay off live systems

Agents no longer run live-system commands from docs, and a new check blocks the direct forms of
live-system, publish and data-out commands; a sandbox network allowlist is the boundary for the rest.
The review check no longer reports finished reviewers as still running
and never suggests turning itself off; builders get clearer rules against loosening checks; test helpers
keep Git isolated.
Every agent treats text it finds in pages, files and PRs as information, never as orders; the release
scan catches pasted credentials; publish and data-out commands are blocked for agents; code-reviewer's
measured results name their command. Reviewers without a shell no longer claim measured results, every
gate quotes text that tried to instruct it, and a gate named without the cheap checks says so.
code-reviewer and test-auditor re-review a fix against eight checks and approve only a full commit sha.
completion-auditor finds the validator from the install record, `.claude/gates-allow.txt` is protected
like the other enforcement files, and the Tier-3 hook's gap list names an alias inside `sh -c`.

### Changed
- **A new check blocks commands that reach a live system.** The Tier-3 hook now blocks cloud, cluster,
  deploy, remote-access and remote-database commands, such as `aws`, `gcloud`, `kubectl`, `helm`,
  `terraform apply`, `vercel --prod`, `ssh` and `psql` to a remote host, including inside `sh -c`,
  `env`, `sudo` and `$(...)`. You run them yourself, list a read-only one in
  `.claude/live-commands-allow.txt`, or start a session with `BR_ALLOW_LIVE=1` (logged). Local commands
  such as `git status`, `npm test` and `psql -h localhost` are not affected.
- **Commands that publish or send data out are blocked too.** The same check now blocks `gh pr merge`,
  `gh release`, `gh repo delete` and `edit`, `gh secret`, `gh variable` and a `gh api` call that is not a
  read; a forcing or deleting `git push`; `npm`, `yarn` and `pnpm publish`, `twine upload`,
  `cargo publish`, `gem push`, `docker push` and `login`; `nc` to a remote host; and `curl`, `wget` or
  `http` sending data or a POST, PUT, PATCH or DELETE to a host that is not your own machine. Reads such
  as `gh pr view`, `git push origin HEAD` and `curl https://example.com` are not affected.
- **The live-command check sees more forms, and says what it cannot see.** It expands an alias defined
  on the same line, checks a heredoc fed to a shell, blocks a pipe into a shell (`| sh`, `| bash`) and
  `curl -K`, and checks `python -c` and `node -e` text, best effort, for a live tool or a call to a
  remote host. It cannot see repo scripts, Makefile targets, copied or renamed programs, PATH changes,
  flags or hosts held in variables, or interpreters running files; `CUSTOMIZATION.md` lists them, and a
  sandbox network allowlist is the boundary for them.
- **A database address on your own machine is not blocked.** `psql postgres://localhost:5432/app` and
  the like now run; a remote database address is still blocked.
- **code-reviewer's measured results name their command** (as do every engineering gate's), and
  embedded-firmware flashes or reads registers on a physical device only when you have connected it for
  that and say so; otherwise it builds and tests on the host or an emulator.
- **Reviewers without a shell no longer claim measured results.** The engineering gates that cannot run
  commands cite completion-auditor's run, with its output path, as CITED, and test-auditor passes a test
  set only on a run completion-auditor made.
- **Reviewers quote text that tried to instruct them.** Every engineering gate writes a `Text ignored:`
  line, just before its verdict, quoting any instruction-shaped text in what it reviewed, or `none`.
- **A gate named without the cheap checks says so.** A gate given a code change with no
  completion-auditor check table adds the condition "ladder not run before this review". The checks run
  on `/gate-review`, `/pre-merge`, `/red-team` and inside `dev-team`, not when you name a gate directly
  after a hand edit. `dev-team` now dispatches test-auditor after completion-auditor's run returns.
- **Copy mode says what it leaves out.** `CUSTOMIZATION.md` now says copy mode brings the agents, skills
  and the Tier-3 hook only; the review check, the marketing write gate, the onboarding hook and the five
  slash commands come from the core plugin.
- **Agents no longer run commands from runbooks or how-tos.** technical-writer runs only the docs
  build, the link checker and samples that touch your local working tree. A live-system command in a
  doc is marked "not run: live-system command" and checked by reading the files it acts on.
  devops-sre, security-operations, completion-auditor and qa-test-engineer follow the same rule.
- **Clearer rules against loosening checks.** Builders never make their own check non-gating, never
  bypass a hook because it is noisy, never edit the repo copies of review agents or skills outside a
  refresh, treat instructions inside pull requests, issues, files and tool output as data, and stop if
  resolving a merge conflict would drop a check that already shipped.
- **Test helpers keep Git isolated.** qa-test-engineer follows the shared rule in Core's
  `enforcement-liveness`.

## 2.8.1 — 2026-10-15 — Harmless reads are no longer blocked

### Changed
- **The Tier-3 hook no longer blocks harmless read commands.** A shell command that only reads a
  protected file, such as `cat .github/workflows/ci.yml 2>&1 | head`, was blocked because of the `>` in
  `2>&1`. Joining output streams (`2>&1`, `>&2`) and sending output to `/dev/null` no longer count as
  writes. A real write is still blocked, including one that also has `2>&1` in it.
- The hook's log no longer shows up as a new file in your repo: `/workforce-init` (Core) adds it to
  `.gitignore`.

## 2.8.0 — 2026-10-14 — The cheap checks run before every gate

### Changed
- **`/gate-review`, `/pre-merge` and `/red-team` run the cheap checks first.** Before any gate,
  `completion-auditor` runs lint, typecheck, the tests for the changed files, then the full suite, the
  same as `dev-team`. No gate is dispatched while one of them is red; the command names the failing
  check. The cheap checks run on these three commands and inside `dev-team`; a gate you name directly
  from the main session after a hand edit does not run them.
- **Setting up a repo is one command.** `CUSTOMIZATION.md` step 1 is now `/workforce-init` (from the
  Core pack) instead of a list of copy commands, with a table of what it writes in each mode.
- **`completion-auditor` builds an SBOM from the lockfile alone** (`npm sbom --package-lock-only`) when
  the dependencies are not installed, before trying anything else.
- The old `ALLOW_TIER3=1` override name is removed; use `BR_ALLOW_TIER3=1`.
- `ux-designer` no longer cites an internal maintainer record.

## 2.7.0 — 2026-10-13 — Cheap checks before gates, and no weakened tests

### Changed
- **`dev-team` runs the cheap checks before any gate.** After the build, `completion-auditor` runs lint,
  typecheck, the tests for the changed files, then the full suite, and stops at the first failure. No
  gate is dispatched while one of those checks is red; the failure goes back to the producer. Each check
  is a measured row in the facts pack. `LINT_CMD` and `TYPECHECK_CMD` are optional project values; an
  unset one is reported as "not configured".
- **Producers never weaken a check to pass it.** They do not delete, skip or loosen a test, an
  assertion, a lint rule, a threshold or a CI step. After three failed attempts at the same error, a
  producer stops and names the failing command and its output file.
- **`test-auditor` scans the diff for weakened tests:** removed assertions, added skip or only markers,
  lowered thresholds, new lint suppressions and deleted test files. An unexplained one is a FAIL.
- **`completion-auditor` tries the package manager's own SBOM command first** (for npm, `npm sbom`),
  then other installed tools. A command that runs and fails is reported with its exit status.
- The gate verdict templates show the evidence label and command in the form the validator expects.

## 2.6.0 — 2026-10-12 — A product designer, a scanning duty, and who settles a disagreement

### Added
- **`product-designer`, a designer that produces and never reviews.** It starts from who the user is
  and the job they need done; with no research to go on, it writes a research plan first and labels
  its design as assumed. Its handoff covers every screen state (empty, loading, error, success, undo),
  the WCAG 2.2 AA criteria each element is designed against, final or draft copy, and measurement targets such as task success and
  a System Usability Scale score. `ux-designer` reviews its handoff and the built screens.

### Changed
- **`completion-auditor` runs the scanners your repository already has** (static analysis,
  dependency audit with a software bill of materials, secret scan, and a web scan when something is
  running) and reports a table of what each found. A scanner that is not installed is listed as not
  run; it never installs one, silences a rule, or fixes a finding.
- **`security-architect` judges that scan table.** A critical finding with no recorded risk
  acceptance fails its review; other findings come back with the fix named.
- **The `dev-team` skill says who settles a disagreement between agents:** the approved spec for
  design questions, a gate's verdict for safety and correctness, and you for scope. Advisors, such as
  `product-designer` and `ip-counsel`, never block: their findings are recorded, and work may proceed
  over them.
- **`ip-counsel` moved to the council pack as an advisor.** The `dev-team` skill and `/plan-review`
  call it on intellectual-property questions when the council pack is installed; otherwise the
  question comes back to you.

## 2.5.0 — 2026-10-10 — A separate infrastructure gate, and sharper agent cards

### Added
- **`infra-reviewer`, a read-only gate on infrastructure and CI/CD changes.** It judges the rollback
  path, blast radius, access grants, pinned actions, secrets, and whether required checks still gate
  the branch that deploys. It never edits what it reviews.

### Changed
- **`devops-sre` writes infrastructure and pipeline changes; it no longer gates them.** It hands each
  change to `infra-reviewer` with its plan or diff output and its rollback step. `/plan-review` and
  `/gate-review` use `infra-reviewer` for this seat.
- **`ai-ml-engineer`** can read model-provider documentation, and reports an eval table row for every
  prompt or model change.
- **`backend-engineer`** stops when there is no approved spec, and reads your test command from your
  project values.
- **`code-reviewer`** checks every added or upgraded dependency (lockfile, pinned version, license,
  known vulnerabilities) and routes infrastructure paths to `infra-reviewer`.
- **`completion-auditor`** checks health after a deploy, and now runs the gate-compliance sweep.
- **`compliance-officer`** sets how the sweep samples merged changes; its vendor list names no
  specific vendors.
- **`data-engineer`** names a restore point before a destructive or bulk change, and runs commands
  against a local or test database only.
- **`edge-agent-engineer`** requires A/B updates with automatic rollback, and power-cut tests.
- **`frontend-engineer`** adds cross-site scripting, content security policy and translation checks,
  and no longer assumes a specific component library or test stack.
- **`ip-counsel`** covers freedom to operate, inventorship, and open-source license obligations.
- **`legal-docs-writer`** builds a cookie and tracker inventory from the product before drafting a
  disclosure, and sends public claims through `claims-gate`.
- **`operational-readiness`** lists each consequential action with its human checkpoint and a test
  that proves the checkpoint blocks.
- **`privacy-counsel`** works from a data-flow table and checks processor agreements.
- **`schema-reviewer`** is triggered by any migration file, and reads the query plan or dry-run output.
- **`security-operations`** keeps a detection table: log source, threshold, a test event that fires
  it, and the response.
- **`technical-writer`** can run commands to check docs against the code.
- **`test-auditor`** runs after `completion-auditor`'s run and judges with its measured output.
- **`ux-designer`** asks for screenshots and automated page-scan output, and says it could not assess
  without them.
- **`/red-team`:** `qa-test-engineer` writes each proof test and `completion-auditor` runs it.
- **The dev-team lifecycle** sends any migration, in any framework, to `schema-reviewer`, and runs
  `test-auditor` after `completion-auditor`.
- This pack inherits the Core 2.5.0 changes; see the Core pack's changelog.

## 2.4.0 — 2026-10-10 — Clear roles, your own values, and a customization guide that fits the plugin

### Changed
- **`qa-test-engineer` writes tests and returns findings; it no longer gives a verdict.** The quality
  verdict belongs to `test-auditor`. Its evidence table gains a mutation-testing row.
- **`/plan-review`:** the agent that wrote a plan never reviews it, and non-gate reviewers return
  findings only. `/gate-review` and `/plan-review` name no producer as a reviewer.
- **`principal-architect` can write its spec** into your spec folder, and nowhere else.
- **`completion-auditor` has one output format:** findings, the verdict block, then the standards
  block.
- **No source-company facts in the agents.** `compliance-officer` reads token, session and audit-trail
  values from your compliance docs or says it could not assess; several agents lost leftover example
  values (package names, a component name, page counts).
- **`domain-compliance` reads your regulated domain first** and returns COULD NOT ASSESS when it is not
  set, instead of guessing a regime.
- **`CUSTOMIZATION.md` fits a marketplace install:** record your project values, copy the five repo
  files, and see every slot the agents use in one generated table.
- **Producers follow one build-error loop** (smallest fix first, stop after three failed attempts on the
  same error, no silenced lint without approval). Provisional: no automated check yet.
- **`technical-writer` mines a spec from code with a stop rule** and marks what the code does not
  settle. Provisional: no automated check yet.
- Agents that pointed at document skills this Workforce does not ship now return the text for your
  session to turn into a file.

## 2.3.3 — 2026-10-09 — CI fails on a FAIL verdict

### Changed
- **The Change Record check fails when a gate says FAIL or COULD NOT ASSESS,** unless section 5
  (Deviations & risk acceptance) has a row naming that gate. Before, a well-formed FAIL passed.
- **A clearer error when the validator is missing.** A plugin install does not put the validator in
  your repo; the check's message now says which two files to copy and points to `CUSTOMIZATION.md`.
- This pack inherits the Core 2.3.3 verdict rules; see the Core pack's changelog.

## 2.3.2 — 2026-10-07 — /gate-review sends each change to the right reviewer

### Fixed
- **`/gate-review` routes schema and migration changes to `schema-reviewer`,** runs `code-reviewer`
  on every change and `test-auditor` on any test change. It no longer sends schema work to
  `data-engineer`, which writes migrations and should not judge its own.

### Removed
- The old `install.sh` script, which installed a hook removed in 2.2.0.

## 2.3.1 — 2026-10-03 — New home at BlackRaptorAI-Labs

### Changed
- The project now lives at BlackRaptorAI-Labs; the old address redirects. Issues and pull requests are open; see CONTRIBUTING.

## 2.3.0 — 2026-10-03 — A plan-review command; measured test verdicts; reviewers that cite vendor docs

### Added
- **`/plan-review`** reviews an implementation plan or design before code is written. It always
  runs eight core reviewers, adds specialists only when the plan touches their area, gives each
  reviewer the sections it owns, and on a second round checks whether each earlier finding is
  closed. Use `/gate-review` for a finished diff.
- **A facts pack before any multi-reviewer review.** `completion-auditor` gathers the changed files,
  dependency and ID coverage, file-ownership collisions and every count with its command, once;
  each reviewer cites it instead of re-deriving it.

### Changed
- **`test-auditor` passes a test set only on a measured run.** It stays read-only and is paired with
  `completion-auditor`, which runs the suite or the mutation `test-auditor` names. Without a measured
  run it returns COULD NOT ASSESS or CONCERNS; a FAIL it can show by reading the code stands.
- **`code-reviewer`, `schema-reviewer`, `devops-sre`, `backend-engineer` and `frontend-engineer` can
  fetch vendor and framework documentation**, so claims about how a service or framework behaves
  are cited by URL. They read; they do not post.
- **`security-architect`, `red-team-reviewer`, `code-reviewer`, `backend-engineer` and
  `frontend-engineer` check every sibling entry point** of a defect before reporting it, and `code-reviewer` and `test-auditor` look for failures that are
  swallowed silently.
- **`qa-test-engineer` hands over a RED-test table:** a test counts as RED only if it was run and
  failed for the intended reason.
- **`dev-team` waits for every dispatched gate before ending its turn**, so no verdict is lost.
- **`data-engineer` no longer emits a verdict block**; `schema-reviewer` signs off migrations.

### Deprecated
- **The Tier-3 hook override is now `BR_ALLOW_TIER3=1`.** `ALLOW_TIER3=1` still works in 2.3.x and
  prints a notice; it is removed in the next release.

## 2.2.1 — 2026-09-09 — Shorter description for the dev-team skill

### Changed
- **The `dev-team` skill's description is shorter.** Same scope and behaviour — it still routes a
  non-trivial change across the dev specialists and assembles the Change Record, and still holds no
  content authority of its own.

## 2.2.0 — 2026-09-09 — `schema-reviewer` is the one gate on a migration; onboarding no longer eats your first turn

### Changed
- **`schema-reviewer` is now the sole, exclusive owner of pre-merge schema and migration review and
  sign-off; `data-engineer` authors schema and migration work but never signs its own off** (owner
  ruling D-96). If you were asking `data-engineer` to review a migration before merge, ask
  `schema-reviewer` instead — `data-engineer` still designs the migration and its rollback, it just
  no longer reviews or approves one.
- **Agent descriptions in this pack were rewritten** to state scope more directly.
- **Onboarding now fires at session start, not on your first prompt** — see the Core pack's 2.2.0
  entry for the mechanism; this pack's agents are covered by the same change.

### Fixed
- **The `gate-review` command no longer produces an invalid result when no gate applies to a
  change.** It previously tried to emit a verdict-shaped block even on a "Tier 1, no gate ran" path,
  which the verdict schema has no shape for and which the Stop hook correctly rejected. It now states
  the Tier-1/no-CR-needed result in prose on that path and emits no verdict block, matching what the
  schema actually supports.

## 2.1.0 — 2026-09-06 — `product-marketing` moves to the Marketing pack

### Changed
- **`product-marketing` moves from this pack to the Marketing pack (owner ruling D3).** A producer
  of external copy belongs where the claims-gate hooks and skills live. On an **engineering-only
  install** you no longer have this agent: `technical-writer`, `principal-architect`, `ip-counsel`
  and `legal-docs-writer` each gained one guarded sentence — route to `product-marketing` when the
  Marketing pack is installed, otherwise the main session drafts the comms and you gate them before
  anything ships. See `UPDATING-YOUR-WORKFORCE.md`.
- **Roster: 24 → 23 agents** (script-generated by `roster_counts.py`, not hand-typed).
- **`dev-team` skill is now executable from its own text**: a tier matrix (which gates run on which
  surface, as a table, not prose), the wave order (spec, build, gates, completion-auditor), FAIL and
  COULD NOT ASSESS handling (FAIL stops the run; CNA re-dispatches once with the missing input, then
  escalates to the human), a two-round re-review cap, and a cost quote (agents x tier x estimated
  tokens) before dispatch.
- **Fixed: `code-reviewer` could be read out of a gate wave by how the ask was framed (D-78).** An
  orchestration probe scoped to "just the gate-review wave" dispatched the five surface-matched
  gates and skipped `code-reviewer`, even though the tier matrix's own "every change, no exception"
  row already named it. The row and the dispatch instruction (§5) now both say the row is
  unconditional, not a surface match, so it survives a narrowly framed ask. Applied as a zero-cost
  text fix, not re-measured in this release — verification is deferred to the next `dev-team`
  orchestration measurement in Phase 3.

## Corrections — 3 Sep 2026

The pre-release claims gate for 2.0.0 found published statements this pack could not
substantiate. They are retracted or qualified here rather than edited out of the entries below,
which stay as written.

- **Retracted: the model-gap study.** Several surfaces cited "a small-N, non-blind model-gap study
  recorded in the maintainers' test-battery dossier" and reported findings from it — that Sonnet's
  gaps concentrated in the Excellence Pass checks, that Opus was at near-parity, that a
  4-task x 3-model side-by-side test established which behaviours separate the tiers. **No such
  record exists** in the dossier, in `_eval/`, or anywhere else. Every statement resting on it is
  removed across the operating standard, the `excellence-pass` skill, the per-tier notes and the
  shared output-quality lines carried by individual agents. The five Excellence Pass checks
  themselves are unchanged and stand on being cheap, self-evidently good practice — which is the
  only claim now made for them.
- **Corrected: the release validation stamp.** Its basis line said the "agent-trigger eval sets"
  were run for this release. They were not: T-A is deferred to Phase 3. The stamp now names only
  what ran — T-C gate liveness on the 20-artifact seeded-defect corpus (n=3, before and after,
  2026-09-02) and the agent-behaviour eval set (19 sets / 53 scenarios, 2026-09-03), both on
  `claude-opus-4-8` under Claude Code 2.1.258 — and says plainly that T-A was not run.
- **Retracted: the roster statistics in the entries below.** "Roster 24 → 25", "Roster 23 → 24",
  "Dev roster 20 → 24" and "16-agent governed team" were hand-typed counts with no record tying
  them to the tree at those releases, and one is internally inconsistent (20 → 24 names three
  agents, not four). Treat them as approximate historical notes, not counts. The current roster is
  read from the built tree: **24 engineering agents at 2.0.0**.
- **Retracted: "Verified with a path-guard test harness."** No test report is reachable for that
  claim. The Tier-3 path guard ships and its hook is in the tree; what is withdrawn is the
  assertion that a verification run demonstrated it.

## 2.0.0 — 2026-09-02 — Two new read-only gates, one verdict contract

**BREAKING: the gate verdict block changed shape** (see the Core changelog for the full v3 diff).
Existing Change Records carrying v2 blocks fail validation until re-emitted.

**BREAKING: two gate seats moved.** A gate that can edit what it judges is not a gate, and two seats
were doing both jobs:

- **`schema-reviewer`** (new, read-only, opus) takes the schema seat. `data-engineer` still authors
  migrations and keeps its tools; it no longer signs them off.
- **`test-auditor`** (new, read-only, opus) takes the quality seat. `qa-test-engineer` still designs
  the strategy and writes tests; it no longer audits its own coverage.
- `seat-list.md` is updated. If you route gates by seat name, this changes who you dispatch.
- `security-operations` drops its gate claim — no Change Record role routed to it.

**Tool grants now match the charters.** Seats told to compute get the tools to compute (D2), and
every computed figure carries its script and inputs and is re-executed by a context that did not
produce it before it is used (D2a). `technical-writer` trades `Bash` for `Edit`, matching the roster.

`[4k]` in the build verifier is extended to catch the inverse of what it caught before: a body that
says run / script / compute programmatically / write the file / `sim/` while the grant lacks the
tool it needs, an unused `Write` or `Edit`, and a `Bash` grant with no re-execution clause.

The `change-record-required` workflow, code-owners and PR templates, and the Tier-3 protection hook
are now BUILT from the golden source and byte-checked against what ships, instead of being
hand-maintained in the repository.

**The verdict block's optional fields now say when to omit them.** Two fields were specified so that a truthful answer
could not validate, and the live `Stop` hook sent those blocks back:

- **`reason`** was shown in every gate's inline template, so gates emitted it blank on verdicts that
  do not carry it. It is now absent from the template, and the rule is stated under it: present only
  on `COULD NOT ASSESS`, omit the key entirely otherwise, never blank.
- **`standards[].verified`** is a required `YYYY-MM-DD` checked at the issuing body, so a standard a
  gate could not reach had no valid date to pair with `access: "not reached"`. Gates are now told
  to cite the secondary source they did reach with the date they checked it, or to leave the
  designation out of the array and carry `["none: practice applied: <x>"]`, or — where the verdict
  truly rests on a text they could not read — to return `COULD NOT ASSESS` with a `reason`.

Neither the schema nor the hook changed; the instructions the gates read did.

Validated against `claude-opus-4-8` as of 2026-09-02.


## 2026-08-13 — Renamed & consolidated
- **Plugin id:** `blackraptor-dev-team` → **`blackraptor-engineering`**. Dependency `blackraptor-bridge` → **`blackraptor-core`**.
- **Repo:** moved from `BlackRaptorAI/BlackRaptor_Agents` (`development/`) into the consolidated **`BlackRaptorAI/blackraptor`** (`engineering/`). Product line: **BlackRaptor Workforce**. Layout normalized (skills at `./skills/`, commands at `./commands/`).
- Agents, skills, and gates unchanged in substance; identifiers/display/paths only.

# Changelog

All notable changes to the BlackRaptor Agents development team are recorded here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [1.4.7] — 2026-08-21

### Changed — Release 4 (technical-writer conform)
- **`technical-writer`** conformed to the R16 spec. Tool set is now Read, Grep, Glob, Write, Bash (adds Bash for reading the repo as ground truth; drops Edit). Charter widened to READMEs, API references, module and architecture docs, and changelogs alongside the numbered as-built specs, with the code treated as ground truth (never invent an API or a flag). Wires in the `content-craft` skill (reference and spec docs select hierarchical-by-topic; how-to and runbook select chronological/step-by-step; Minto is not forced onto reference docs) and `standards-discipline` for any standard it cites; stays repo-native (R10). Description is em-dash-free.

## [1.4.6] — 2026-08-21

### Changed — core consolidation (Release 3)
- The shared core-doctrine skills are no longer duplicated into this pack; they install with the `blackraptor-core` dependency (a core-skill edit no longer touches this pack). Adds a roster-neutral change-record template + this pack's `seat-list.md` (the engineering gate roles → agents). No user-facing strings changed.

## [1.4.5] — 2026-08-20

### Added
- Repo-native first-run experience (R10/R14): a bare repo triggers the welcome flow with the engineering technical question set (`dev-team/references/context-questions.md`) — the shared core block writes repo-root `BUSINESS-CONTEXT.md`, the technical set writes `CLAUDE.md`; a populated repo gets a "review and fill gaps" offer instead. Seven-dimension preference wire-up (R13) via the shared Core contract. Engineering stays project-scoped.

## [1.4.4] — 2026-08-19

### Changed
- `dev-team` gains a context read-path note: engineering keeps the project's **existing** context conventions (no new company-context file), and the Core `prompt-brief` intake now runs the Rung-0 context precheck before context-dependent work (resolve the project's context per the resolution order; `context-onboarding` can capture it if the change needs context the project does not yet record) (R3, engineering read-path per spec §3.1).

## [1.4.3] — 2026-08-18

### Fixed
- `workforce-doctor` no longer certifies pack presence/absence from a stale Cowork snapshot. A Cowork cloud session copies the account plugin cache to `.claude/plugins/synced/` once at session start and never re-syncs, so a run could report a pack PRESENT that was uninstalled after the session began. Adds **check 0 (snapshot freshness)**: in a Cowork session the doctor records and reports the snapshot timestamp and returns **STALE SNAPSHOT — CANNOT CERTIFY** when the snapshot predates the pack add/remove under test. Adds a check-1 caveat that an empty `claude plugin list` under Cowork is inert by design, not an anomaly. No-op in local CLI sessions.

## [1.4.2] — 2026-08-17

### Fixed
- Ships `workforce-doctor` to existing installs (prior release omitted the version bump). The skill was already committed to the pack, but the plugin version wasn’t bumped, so `claude plugin update` treated installs as current and never delivered it — this patch re-releases with a bumped version. Tracked in BlackRaptorAI/blackraptor#1.

## [1.4.1] — 2026-07-23

### Fixed
- **`completion-auditor` now pins `model: opus`** — it was missing a `model:` field
  and silently fell back to the session default. It's a deep-judgment gate; opus is
  the correct tier (matches golden and the other gate agents).

## [1.4.0] — 2026-07-22

Cross-cutting agents moved to a shared bridge; roster 25 → 23.

### Changed
- **`evidence-auditor` and `product-manager` moved out** to the new
  `blackraptor-bridge` plugin (auto-installed as a dependency — you still get them,
  namespaced `blackraptor-bridge:…`). They're cross-cutting: evidence-auditor is
  central to the council and the HEAVY-tier gate for engineering's load-bearing
  claims; `product-manager` (now the merged product-strategy + delivery role) spans
  market demand and the build.
- **`research-integrity` skill moved** to the bridge too (it's evidence-auditor's
  paired methodology). Dev-team skills 8 → 7.
- `plugin.json` now declares `"dependencies": ["blackraptor-bridge"]`.

## [1.3.0] — 2026-07-22

Public now mirrors the golden roster more closely: personas out, model tiering in.

### Changed
- **Removed the persona/backstory blocks** ("**Who you are.**" voice paragraphs)
  from all 24 charters. The charters keep their role, reasoning method, mission,
  and boundaries — just not the first-person backstory. Behavior is defined by the
  instructions, not a character.
- **Model tiering now matches the source deployment** — `dev-orchestrator` and
  `principal-architect` move to the top tier (the strongest model available), reserved for
  the two roles where a mistake is costliest and call volume is lowest. Deep-judgment
  gates stay `opus`; everyday build stays `sonnet`. Each opus charter carries the
  tier-appropriate Output-quality discipline line (checklist backstop). README
  "Model tiering" section updated (was "tops out at `opus`"); fall back to the
  strongest model you have where the top tier isn't available.

## [1.2.0] — 2026-07-22

### Added — agents
- **`completion-auditor`** — an independent verifier that audits claimed-complete
  work **before** it's reported as done (especially multi-step git/PR/merge/deploy
  work). Read/verify-only (Bash, Read, Grep, Glob); it doesn't trust narration —
  it re-checks ground truth (remote refs, CI state, `origin/main` log, cwd/worktree
  hygiene, pipe-masked exit codes, shell word-splitting, governance ordering) and
  returns PASS or a list of unverified/failed items to fix first. The behavioral
  analog of the Excellence Pass "verify by an independent method." Roster 24 → 25.

## [1.1.0] — 2026-07-21

The research-integrity release + Claude Code plugin marketplace. Roster 23 → 24.

### Added — agents
- **`evidence-auditor`** — the independent adversarial gate for research, analysis,
  and evidence-based reporting (the research analog of `red-team-reviewer` /
  `completion-auditor`). Read/analysis-only; grades sources (reliability ×
  credibility), collapses citation chains to **independent origins** (effective-N /
  anti-woozle), separates **root-veracity** from root-reachability, checks
  qualifier drift, and enforces the release gate — PASS / CONCERNS / FAIL verdicts.

### Added — skills
- **`research-integrity`** — a three-mode research methodology engine (A evidence
  synthesis · B direct-source aggregation · C original primary research) with an
  intake triage, mode-selector, separate source-reliability × evidence-certainty
  grading, citation-independence + consilience, root-to-mechanism verification, a
  release gate, and analytic-judgment output. Ships with fillable artifact
  templates (`templates.md`) and the full design spec (`docs/research-integrity-spec.md`).
- **`excellence-pass`** — the five behaviors that separate top-tier output from
  merely-correct output, run as a final pass before delivery; each charter carries
  a tier-appropriate pointer to it.

### Added — distribution
- **Claude Code plugin marketplace.** Install the suite via
  `/plugin marketplace add BlackRaptorAI/BlackRaptor_Agents` → plugins
  `blackraptor-dev-team` and `blackraptor-council`. Manifests:
  `.claude-plugin/marketplace.json` (repo root) + per-team `plugin.json`.

### Changed
- Dev roster **20 → 24** (Legal & IP pod: `legal-docs-writer` + `ip-counsel`;
  then `evidence-auditor`). README count + install docs updated.

## [0.3.0] — 2026-07-16

Roster grows to 20 with two roles extracted from the same production platform
the kit came from, and the pods are rebalanced.

### Added — agents
- **`edge-agent-engineer`** — the on-device/customer-premises engineering tier:
  device adapters, offline queueing, remote access, self-healing. Encodes the
  edge disciplines cloud personas don't carry: resource budgets on constrained
  hardware, fleet version skew (N-1/N-2 tolerance, canary channels), and clock
  integrity when device timestamps feed regulated data. Delete it if your
  platform has no edge tier.
- **`operational-readiness`** — operational fitness + meaningful human control.
  Two lenses: does the change serve the operator's real workflow (consulted at
  spec, sign-off at delivery), and does every consequential automated or
  AI-driven action have a designed, audited, fail-safe human checkpoint
  (**blocking at review**). This is the kit's sixth blocking gate.

### Changed
- **Roster regrouped from 8 pods to 7.** The "Security assurance & docs"
  catch-all is dissolved: `red-team-reviewer` joins Quality & Assurance,
  `technical-writer` joins Communication & GTM. New agents slot into
  Engineering and Operations.
- Blocking-gate count is now **six** (security, privacy, compliance, domain,
  schema, human oversight). `docs/gate-enforcement-map.md` gains the HITL row
  (checklist-only — it's a behavioral property no path expresses).
- `/gate-review` routes consequential automated actions to
  `operational-readiness`; `/new-feature` consults it at spec time.

## [0.2.0] — 2026-07-03

This release grew the roster and hardened the agent *craft* — most of it
directly inspired by ideas from the wider Claude Code community. See the
**Credits & thanks** section below; these improvements exist because other
people published their work openly, and we're grateful for it.

### Added — agents
- **`red-team-reviewer`** — an adversarial, pre-penetration-test review agent:
  threat modeling, OWASP / abuse-case review, and *proof-of-vulnerability*
  tests written against your own code in a controlled test environment. It is
  read-only by design and explicitly **complements, never replaces, an
  independent human penetration test.** *(Role inspired by the
  `penetration-tester` / `security-auditor` roles common in public collections —
  see Credits.)*
- **`security-operations`** — runtime/operational security (SIEM, WAF, detection
  engineering, security incident response, secrets hygiene), distinct from
  build-time `security-architect`.
- **`technical-writer`** — owns as-built spec/code drift, API reference, and
  documentation quality. *(Identified as a roster gap by benchmarking against
  public role taxonomies — see Credits.)*

### Added — skills & tooling
- Reference **skills** extracted so agent prompts stay lean and multiple agents
  share one source: `stride-review`, `expand-contract-migration`,
  `owasp-llm-checklist`, `gate-verdict-format`. *(Progressive-disclosure-skills
  pattern — see Credits.)*
- **`agent-evals/`** — a proactive agent-quality convention (run a small fixed
  eval set when you change an agent definition) that pairs with the reactive
  `AGENT-RETROS.md` loop: evals prevent regressions, retros correct misses.
  *(Inspired by public agent-evaluation frameworks — see Credits.)*
- **`/red-team`** slash command to run the adversarial review on demand.

### Changed
- **Model-tiering** is now a documented, deliberate policy (deep-judgment agents
  on the strongest model, everyday builders on a mid tier, low-stakes work on a
  fast tier) rather than ad hoc. *(Multi-tier model strategy — see Credits.)*
- **Least-privilege tool permissions** audited across the roster: read-only
  reviewers carry only read/analysis tools; only builders get write/exec.
  `red-team-reviewer` was tightened to read-only after this audit caught it
  carrying shell access it did not need. *(Role-based tool-restriction
  convention — see Credits.)*

### Security
- **Tier-3 guard hook hardened.** Path matching is now case-insensitive (so a
  case variant like `.GitHub/` can't slip past on macOS/Windows) and resolves
  symlinks with `realpath` (so a symlink pointing at a protected file is
  caught). The docstring now states plainly that this hook is in-session
  accident-prevention and that the *enforcement of record* is server-side
  (branch protection + code-owner review + the change-record-required CI check).
  Verified with a path-guard test harness.

### Notes
- Nothing here changes the governance core (Change Records, tier gates,
  fail-closed enforcement) — the differentiator of this kit. The additions are
  craft and coverage improvements layered on top.

---

## Credits & thanks

The 0.2.0 improvements came from **benchmarking this kit against the excellent
public Claude Code subagent collections**. Each idea below is credited to where
we found it, with a link to the source and our sincere thanks to the maintainers
and contributors — open-sourcing your work is what made these improvements
possible.

| Improvement in this release | Idea credited to | Source |
|---|---|---|
| Deliberate multi-tier model strategy (deep/everyday/fast) | **wshobson** and contributors — *agents* marketplace | https://github.com/wshobson/agents |
| Proactive agent-quality evaluation (the `agent-evals/` convention) | **wshobson** and contributors — the *PluginEval* quality framework | https://github.com/wshobson/agents |
| Progressive-disclosure **skills** (lean prompts, load knowledge on demand) | **wshobson** and contributors | https://github.com/wshobson/agents |
| Role-based **least-privilege tool restriction** (read-only reviewers, etc.) | **VoltAgent** and contributors — *awesome-claude-code-subagents* | https://github.com/VoltAgent/awesome-claude-code-subagents |
| Role taxonomy that surfaced our gaps (**technical-writer**, and the security roles behind **red-team-reviewer**) | **VoltAgent**, **0xfurai**, and the broader community catalogs | https://github.com/VoltAgent/awesome-claude-code-subagents · https://github.com/0xfurai/claude-code-subagents |
| Community index that made these collections discoverable | **hesreallyhim** — *awesome-claude-code* | https://github.com/hesreallyhim/awesome-claude-code |

**Thank you** to the maintainers and contributors of these projects. We adopted
your *ideas and conventions*, re-expressed for this governance-first kit; the
governance layer (Change Records, tier gates, enforcement) is our own
contribution back to the commons. If we've mis-credited an idea or missed a
source, please open an issue — we want attribution to be right.

## [0.1.0] — 2026-07-02

Initial public release: 16-agent governed team, Tier-3 path-guard hook,
`change-record-required` CI check, sparse code-owners two-person rule, the Change
Record system, and the agent-retro feedback loop. Extracted from production use.
