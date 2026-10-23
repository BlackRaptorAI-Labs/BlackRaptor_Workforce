---
name: workforce-doctor
description: >-
  Diagnose an installed BlackRaptor Workforce — confirm the packs are present, versioned consistently, and structurally intact (dependencies resolve; the core hooks are wired for the current client). Read-only. Run when something seems off, or before filing a defect.
---

# Workforce Doctor

A read-only health check for an installed BlackRaptor Workforce. It **writes nothing**. It reads local files and the
plugin list, and it also runs two read-only commands: `shasum` (check 9 compares a repo file with the pack's copy)
and `gh` (check 13 reads GitHub for branch protection, the CI judge, who has write access, and whether GitHub Actions can
approve pull requests; it needs `gh` signed in, and an admin login for some of it). Use it to catch a broken or partial
install before it wastes your time, and to attach a clean diagnosis to a defect report.

## What to check

Work through these and collect anomalies as you go. Report **PASS** only if every check passes.

0. **Snapshot freshness (Cowork / cloud sessions only).** A Cowork cloud session copies the
   account's plugin cache to `.claude/plugins/synced/` **once at session start and never
   re-syncs**. Everything the doctor reads there is a point-in-time snapshot, not the live
   account state. Before any other check:
   - Record the snapshot timestamp (the `synced/manifest.json` mtime, or its `lastUpdated`
     field) and **state it in the report**.
   - If the user is asking the doctor to prove a pack was **added or removed**, compare the
     snapshot timestamp to when that change was made. If the snapshot **predates the change**,
     the doctor MUST refuse to certify pack presence or absence: report
     **STALE SNAPSHOT — CANNOT CERTIFY**, name the timestamp, and instruct the user to start a
     fresh session and re-run. A stale run can report a pack PRESENT that was uninstalled an
     hour earlier — a false negative on exactly the removal it is being asked to prove.
   - Rule of thumb: pack add/remove is only provable from a session started **after** the change.
   In a local (non-Cowork) CLI session this check is a no-op — note "local session, live plugin
   state" and move on.

1. **Installed packs + versions.** Run `claude plugin list`. Note each installed BlackRaptor pack
   (`blackraptor-engineering`, `blackraptor-council`, `blackraptor-marketing`, `blackraptor-hardware`,
   `blackraptor-core`) and its version and enabled/disabled state. Anomaly: a pack shows `disabled`,
   or a pack the user believes they installed is absent.
   **Cowork caveat:** under a Cowork cloud session `claude plugin list` returns
   "No plugins installed" **by design** — packs are synced, not CLI-installed, so an empty list
   there is NOT data and must not be reported as an anomaly. In that case answer this check by
   listing the pack directories under `.claude/plugins/synced/` and reading each pack's
   `.claude-plugin/plugin.json` (and the `synced/manifest.json` account entries), subject to the
   freshness rule in check 0.

2. **Core dependency resolves.** Any team pack (`engineering`, `council`, `marketing`, `hardware`)
   must pull in **`blackraptor-core`**. If any team pack is installed but `blackraptor-core` is not
   listed, that is an anomaly (dependency did not resolve).

3. **Per-pack file inventory + manifest version.** For each installed pack, read its
   `.claude-plugin/plugin.json` from the install location (`claude plugin list` / the marketplace
   directory shows it). Confirm the manifest exists and its `"name"` matches the pack id above, its
   `"version"` matches what `claude plugin list` reports, and the pack ships its expected top-level
   dirs (`agents/`, `skills/`, and for a team pack a `CLAUDE.md`, `LICENSE`, `NOTICE`). Anomaly: a
   missing manifest, a name/version mismatch, or an empty `agents/` or `skills/`.
   Report each pack's agent count as counted from its install folder (`ls <pack>/agents/*.md | wc -l`,
   top level only) and quote the command. Never take a count from a README, a manifest or memory.
   Then report each gate's model and effort (D-287, D-288). Read the list of gates from the `"gates"` key of the core
   pack's `skills/gate-verdict-format/verdict-schema.json`; for each gate whose agent file is in an installed pack, read the `model:` and
   `effort:` lines in that file's frontmatter (`sed -n '1,12p' <pack>/agents/<name>.md`) and print one line per gate, `<gate>: model <x>, effort <y>`
   (`effort <none>` when there is no line). Expected: every gate `model opus, effort high`. Also report any agent file in an installed pack whose `model:` line is `best` (the architecture authority of the engineering pack):
   expected `effort high`. A gate on any other model, or with a missing or different effort line, is an
   **ANOMALY (cosmetic, but say so)**: "gate <name> runs with model <x>, effort <y>; the shipped value is opus, high (a local edit or an older install)".
   Say plainly that this is what the files ask for; the session or the environment (`CLAUDE_CODE_EFFORT_LEVEL`, `CLAUDE_CODE_SUBAGENT_MODEL`)
   can still override it, and the doctor cannot see what a past run used.

4. **Core hooks wiring (R15.4; `blackraptor-core` is always installed).** Four hooks live in the
   CORE pack: the welcome/onboarding trigger and the session-contract hook (both `SessionStart`; the
   session-contract hook is off unless `BR_SESSION_CONTRACT=on`, so its silence is expected), the DRAFT/GATED write gate
   (`PreToolUse`), and the verdict validator (`Stop`). The one-shot claims-gate prompt-reminder hook
   that used to run on `UserPromptSubmit` was removed in 2.2.0 (its job is now carried directly in
   each producer's own instructions). Since 2.8.2 the `UserPromptSubmit` entry is the verdict
   validator recording verdict and asset files at turn start (it prints nothing). Report whether each
   of the four current hooks is wired:
   - `core/hooks/hooks.json` is present and lists one `SessionStart` entry, one `UserPromptSubmit`
     entry (`validate-verdicts.sh --snapshot turn-start`), one `PreToolUse` entry (matcher
     `Write|Edit|MultiEdit|Bash`), one `PostToolUse` entry (matcher `Bash`, `validate-verdicts.sh
     --snapshot bash`), and one `Stop` entry.
   - `core/hooks/inject-onboarding-rule.sh` and `core/hooks/inject-session-contract.sh` (`SessionStart`), `core/hooks/enforce-draft-gate.sh`
     (`PreToolUse`), and `core/hooks/validate-verdicts.sh` (`Stop`) are all present **and executable**
     (`test -x`). A hook the client cannot execute is a silently disabled rule.
   - `command -v python3` succeeds, and `core/hooks/validate-verdicts.py`, `core/hooks/enforce-draft-gate.py`
     and `core/skills/gate-verdict-format/validate_verdict.py` are present (D-267, D-268). The write gate
     and the verdict validator run in Python. Without `python3` on PATH, or without one of these files,
     the verdict hook prints "gates in this turn are NOT checked" on every Stop and the write gate denies
     writes under a marked asset folder, so a missing one is a **FAIL**, not an anomaly to note: report
     `FAIL: the verdict check cannot run (<what is missing>); gates are NOT checked`.
   - the core `plugin.json` does **NOT** declare a `"hooks"` key. On client 2.1.170+ `hooks/hooks.json`
     auto-loads by convention, so declaring it is a fatal "Duplicate hooks file detected" load failure —
     a **blocking** anomaly.
   Report the wiring status for all four hooks; a missing/non-executable hook means that rule won't
   auto-fire (for onboarding, the in-skill R3/R7 triggers still apply as the backstop) — note it,
   non-blocking.
   Stop-hook scope: the verdict hook checks verdict blocks that a gate dispatched in the turn returned,
   and verdict files written in that turn. It does not check a block the main session writes itself, and
   a turn that dispatched no gate shows no Stop-hook activity. Stop hooks do run in print mode
   (`claude -p`). This check covers wiring only; never report a quiet Stop hook on a turn with no gate
   as a defect.

5. **Client version.** Record `claude --version`. Note it in the report — hook-loading and
   marketplace behavior have varied across client versions.

6. **Context onboarding (per pack).** For each installed pack that uses a context file, resolve it
   per the documented order (current working / project root → an explicit path the user named) and
   report one of three states:
   - **ONBOARDED** — a filled context file is present, has **no** `<!-- TEMPLATE — not onboarded -->`
     first-line marker, and carries a date stamp. Also **count and report the remaining UNKNOWN
     markers** in it (`UNKNOWN — user to provide` / `[unknown]`): a file with unknowns is still
     ONBOARDED, but report e.g. "ONBOARDED (3 UNKNOWN left)" so the gaps stay visible (R12e).
   - **TEMPLATE** — the template marker is present (onboarding has not been run).
   - **MISSING** — no context file found at the resolved location.
   Expected file names at the project root: `BUSINESS-CONTEXT.md` (council), `MARKETING-CONTEXT.md`
   (marketing), `PROGRAM-CONTEXT-<program>.md` (hardware); engineering uses the project's existing
   convention. This check is **non-blocking / cosmetic**: report the state and, for TEMPLATE or
   MISSING, recommend running `context-onboarding` — **never fail the install for it**. In a Cowork
   session, check the connected project folder; if no project folder is connected, say so rather
   than reporting MISSING.

7. **State-file staleness (optional, report-only).** In the working project, look for
   `<slug>-state.md` files (state-file v2). Any file with `status: active` whose `updated <date>` is
   more than **30 days** old is flagged — "stale active state: finish it, pause it, or supersede it."
   Non-blocking / cosmetic, like check 6; it keeps the state index honest without any scheduler. If no
   state files exist, skip silently.

8. **Repo copies behind the packs (report-only).** Two cases; skip silently if neither applies.
   - **Copy mode.** If `.claude/workforce-installed.json` exists and its `"mode"` is `"copy"`, read its
     `"packs"` object (the pack versions the repo copies were made from) and compare each with the
     installed version of the same pack (check 1), as version numbers (2.8.0 < 2.8.1 < 2.10.0). If any
     recorded version is **older**, report a **WARNING** per pack: "repo copies are `<found>`, packs are
     `<installed>`: run `/workforce-init --upgrade`". Otherwise report "repo copies current" with the
     versions. Quote the file and the values you compared. Also report a **WARNING**, "copy mode: verdict
     Stop hook not installed": copy mode installs the agents, skills and the Tier-3 hook only; the Stop
     hook, draft gate, onboarding hook and the five slash commands come from the core plugin, so they
     run only in a session that also has the core plugin installed (say whether check 1 found it here;
     a cloud session usually does not). Fix: use plugin mode, or run the validator by hand.
   - **Older vendored install.** If `.claude/.blackraptor-core-version` exists, read it and compare it
     with the installed core version. If it is older, report a **WARNING**: "older vendored install:
     core `<found>` in the repo, `<installed>` installed. Fix: run `/workforce-init --mode copy` to
     replace it."
   Never an anomaly and never a FAIL.

9. **Engineering repo files (only when `blackraptor-engineering` is installed).** The Tier-3 hook and
   the Change Record CI check run from your repo, not from the pack, so these five files must exist under
   the directory the session was launched from:
   `.claude/hooks/protect-tier3.py`, `.claude/settings.json`,
   `.github/workflows/change-record-required.yml`,
   `.claude/skills/gate-verdict-format/validate_verdict.py` and
   `.claude/skills/gate-verdict-format/verdict-schema.json`.
   Check each with `test -f` and quote the result. Any missing file is an **ANOMALY (blocking)**: name
   it and say the fix is `/workforce-init` (the engineering pack's `CUSTOMIZATION.md`, step 1). A session
   launched from a parent folder of the repo shows all five missing; say so, since relaunching from the
   repo root is the fix. Exception: if `.claude/workforce-installed.json` says `"mode": "user"`, the user
   chose not to put these files in the repo; report them as a **WARNING** (the Tier-3 hook and the Change
   Record CI check are not running here), not an anomaly.
   **Then compare each enforcement file with the pack's (D-191).** Present does not mean intact: a repo copy
   that differs from the pack's can switch a check off while it still exists. Read `core_root` and
   `engineering_root` from `.claude/workforce-installed.json`, and run `shasum -a 256` on each pair:
   `.claude/hooks/protect-tier3.py` with `<engineering_root>/claude/hooks/protect-tier3.py`;
   `.claude/skills/gate-verdict-format/validate_verdict.py` and `verdict-schema.json` with the same names
   under `<core_root>/skills/gate-verdict-format/`; and, only if the repo holds them,
   `.claude/hooks/validate-verdicts.py` and `.claude/hooks/enforce-draft-gate.py` with
   `<core_root>/hooks/`. Quote both hashes. A mismatch is an **ANOMALY (blocking)**; its first line reads
   `FAIL: <file> differs from the pack's copy` (that word, so a script can find it). Name the file and say
   the fix is `/workforce-init --replace-enforcement` (it keeps the repo's copy as
   `<name>.bak`). If a root is not recorded (a repo set up before 2.8.2), use that pack's `installPath`
   from `~/.claude/plugins/installed_plugins.json` (the entry for this project, else the user-scope one).
   In copy mode (`core_root` is `.claude`), or when no pack copy is found, there is nothing to compare
   with: report a **WARNING** naming the files not compared.

10. **Project context file.** The launch directory must hold the project context file the agents read
   their project values from: `BUSINESS-CONTEXT.md` (or, for an engineering repo, a root `CLAUDE.md`
   with a "Project values" table). If neither exists there, report an **ANOMALY (blocking)**: gates
   return COULD NOT ASSESS on any gate-critical value they cannot read. Fix: relaunch from the project
   root, or run `context-onboarding` to create the file. (Check 6 still reports per-pack state.)

11. **Sandbox (D-223).** Read `sandbox.enabled` from `.claude/settings.local.json`, then
   `.claude/settings.json`, then `~/.claude/settings.json` (the first file that sets it wins; quote the
   file and the value). Unset or `false` is an **ANOMALY (blocking)** whose first line reads
   `FAIL: sandbox off: enforcement files are not protected without the sandbox; hooks still run, but an agent with a shell can edit them`;
   the fix is `/workforce-init --upgrade` (from your own terminal) or `sandbox.enabled: true`. `true`: the
   setting alone does not prove the sandbox runs, so probe it. On Linux, run `command -v bwrap socat` and
   quote the output: if either is missing, the sandbox is unavailable, and that is the same **FAIL** with
   "(missing: <the missing names>)" added. On macOS, run `command -v sandbox-exec` and quote it; missing is
   the same FAIL. Then quote `sandbox.failIfUnavailable`, `sandbox.allowUnsandboxedCommands` and
   `sandbox.filesystem.denyWrite`: report a **WARNING** for `failIfUnavailable` not `true` ("Claude Code may
   run without the sandbox"), for `allowUnsandboxedCommands` not `false` ("an agent can ask to run a command
   outside the sandbox"), and for each file in `.claude/workforce-installed.json`'s install that is missing
   from `denyWrite` (`.claude/gates-allow.txt`, `.claude/test-summary-patterns.txt`,
   `.claude/live-commands-allow.txt`, `.claude/workforce-installed.json`, `.claude/review-copies.sha256`,
   `.github/workflows/change-record-required.yml`). In user mode the repo holds no settings: report the FAIL
   line and say the sandbox must be turned on per user (`/sandbox`). The sandbox covers shell commands only;
   hooks run outside it.

12. **Test command, tamper baseline and runner config (D-222, D-231, D-233, D-239, D-245, D-246).** Read
   `test_cmd` (one command, or a list of commands that must each pass) and `test_timeout` from
   `.claude/workforce-installed.json` and quote them. In plugin mode, no `test_cmd` is an
   **ANOMALY (blocking)** whose first line reads
   `FAIL: no test command recorded: every PASS from the test-quality review or the completion audit is blocked`, with the fix
   `/workforce-init --upgrade --test-cmd "<your test command>"` (from your own terminal); in copy mode the same
   text is a **WARNING**. If a recorded command is not a direct runner the hook reads a report from (pytest,
   jest, vitest, go test, node --test, mocha, bun, dotnet, maven, or `npm`/`pnpm`/`yarn test` whose
   `package.json` test script is one of those, alone; `uv run`, `poetry run`, `pipenv run`, `hatch run`,
   `pdm run` or `rye run` in front of one of those counts), report a **WARNING** naming that command: "the hook
   cannot read a report from this test command, so a PASS is blocked; record the runner itself (see "Direct
   test commands" in UPDATING-YOUR-WORKFORCE.md)". In plugin mode, read `tamper-baseline.json` in
   the core plugin's data folder (`~/.claude/plugins/data/blackraptor-core-<marketplace>/`, the marketplace
   from `.claude/workforce-installed.json`) and quote whether it has an entry for this repo's path and
   whether that entry has `runner_config`: either missing is an **ANOMALY (blocking)**,
   `FAIL: no tamper baseline: run /workforce-init --upgrade from your own terminal`. When the entry's
   `runner_config_by` says the Stop hook recorded it, quote `runner_config_date` in the line "runner config
   first recorded by the Stop hook on <date>; review it, and run /workforce-init --accept-runner-config from
   your own terminal if it is what you expect" (a note, not a WARNING). When check 11 found the
   sandbox off, report a **WARNING**: "the tamper check can also be edited without the sandbox, so it no
   longer protects you". In copy mode report two **WARNING**s: "tamper detection needs plugin mode" and
   "copy mode checks the test runner config against the base branch, not a protected baseline; this is
   weaker, because an agent can rewrite git refs".

13. **CI judge and merge protection (D-251 to D-254, D-260; engineering pack, plugin or copy mode).** Run
   `python3 <core_root>/hooks/validate-verdicts.py --ci-status <repo>` (`core_root` from
   `.claude/workforce-installed.json`; in copy mode the core plugin's own folder) and quote its JSON. It
   reads the workflow file against the recorded hash and, through `gh`, the default branch's required checks
   and, with an admin login, its review settings.
   - `ci_judge` false: a **WARNING**, "No CI judge: test passes are checked only on this machine, where an
     agent can fake them. Use CI for real proof." Skip the rest of this check.
   - `workflow` "missing": an **ANOMALY (blocking)**,
     `FAIL: the CI judge workflow .github/workflows/workforce-proof.yml is missing: run /workforce-init --upgrade from your own terminal`.
   - `workflow` "differs": an **ANOMALY (blocking)**,
     `FAIL: the CI judge workflow differs from the one /workforce-init recorded: a person reviews it, then runs /workforce-init --upgrade to restore it or --accept-changes to keep it`.
   - `workflow` "not recorded": an **ANOMALY (blocking)**,
     `FAIL: the CI judge workflow was never recorded for this repo: run /workforce-init --upgrade from your own terminal`.
   - `repo` null (no GitHub remote): a **WARNING**, "no CI judge for this repo: a PASS from the test-quality
     review or the completion audit stays INCOMPLETE until the repo is on GitHub with Actions on, or
     /workforce-init --upgrade --no-ci-judge".
   - `branch_protection.requires_both` false: an **ANOMALY (blocking)**,
     `FAIL: branch protection on <branch> does not require head-suite and base-suite: run /workforce-init --setup-branch-protection from your own terminal`.
     A `branch_protection.error` (gh missing, not signed in, offline) is a **WARNING** naming it. Inside Claude
     Code's sandbox on macOS, gh cannot verify GitHub's certificate (measured), so the error says "run it from
     your own terminal": give the user the exact command, `python3 <core_root>/hooks/validate-verdicts.py
     --ci-status <repo>`, and report branch protection as not checked, never as passing.
   - `branch_protection.reviews_readable` true and `required_approving_review_count` below 1 or
     `dismiss_stale_reviews` false: an **ANOMALY (blocking)** (D-260),
     `FAIL: branch protection on <branch> does not require one approving review with stale approvals dismissed: run /workforce-init --setup-branch-protection from your own terminal`.
     Workforce uses no code-owners file and does not ask about one. The approval is the owner's only while write access stays with the
     owner and one agent account (see `writers` and `actions_approve` below).
   - `branch_protection.strict` false (read, so an admin login or a ruleset): an **ANOMALY (blocking)** (D-276; audit 9V W11),
     `FAIL: branch protection on <branch> does not require branches to be up to date before merging: run /workforce-init --setup-branch-protection from your own terminal`.
     Without it a pull request can merge after the base moved, on checks that ran against an older base.
   - `branch_protection.require_last_push_approval` false (read): a **WARNING**,
     "branch protection on <branch> does not require approval of the most recent push: run /workforce-init --setup-branch-protection from your own terminal".
   - `branch_protection.reviews_readable` false: a **WARNING**, "the review settings on <branch> need an admin
     GitHub login to read; run `python3 <core_root>/hooks/validate-verdicts.py --ci-status <repo>` from your
     own terminal". Report them as not checked, never as passing.
   - `branch_protection.enforce_admins` (when read): an **INFO** line, "enforce_admins is <value>: false lets an
     admin (the owner) merge their own pull request by an override GitHub shows as a bypass; true makes every
     admin wait for an approval too." Quote `strict` the same way (true: the branch must be up to date first).
   - `writers` (D-273). GitHub counts one approval from anyone with write access, so the approval is the owner's only
     while write, maintain and admin access stay with the owner and the one agent or build account the install recorded
     (`owner_login`, `agent_accounts` in `.claude/workforce-installed.json`):
     - `writers.readable` false: a **WARNING**, "who has write access to <repo> cannot be read with this GitHub login
       (listing collaborators needs push access); run `python3 <core_root>/hooks/validate-verdicts.py --ci-status <repo>`
       from your own terminal". Report it as not checked, never as passing.
     - `writers.readable` true and `owner_recorded` false: a **WARNING**, "no owner login is recorded, so write access
       cannot be checked: run /workforce-init --upgrade --owner-login <your GitHub login> --agent-account <build account>.
       Write access today: <logins>."
     - `writers.unexpected` not empty: an **ANOMALY (blocking)**,
       `FAIL: <logins> have write, maintain or admin access to <repo> and are not the recorded owner or agent accounts: GitHub counts one approval from anyone with write access, so remove them or record them with /workforce-init --upgrade --agent-account`.
     - otherwise an **INFO**: "write access: <logins>; all are the recorded owner or agent accounts." When `truncated`
       is true add "(100 collaborators or more: only the first 100 were read)".
     - `writers.multiple_agents` true (D-283): a **WARNING**, "more than one account besides the owner has write access
       (<logins>): one agent can approve another's pull request, so the approval is no longer only the owner's; keep one agent account".
   - `actions_approve` (D-283; reading it needs an admin login):
     - `can_approve` true: an **ANOMALY (blocking)**,
       `FAIL: GitHub Actions can approve pull requests on <repo>: turn off "Allow GitHub Actions to create and approve pull requests" (Settings, Actions, General, Workflow permissions); a workflow's approval would count as the one approval`.
     - `readable` false: a **WARNING**, "whether GitHub Actions can approve pull requests on <repo> needs an admin GitHub login to read;
       run `python3 <core_root>/hooks/validate-verdicts.py --ci-status <repo>` from your own terminal". Never report it as passing.
   - `disk_check.skipped` true (D-279): a **WARNING**, "the disk check would be skipped on this repo (<reason>): verdict files and
     marked assets written outside the Write tool are not checked; the verdict hook says so on every turn it skips". `skipped`
     false: nothing to report.
   - Quote `judge.msg` for HEAD as a note (CI passed, waiting, failed, or why it was not read).
   Agents never merge, and the doctor changes nothing here: every fix above is the user's, from their own
   terminal or GitHub's settings.

## Report format

Emit one of:

- **PASS** — list the packs and versions you confirmed, the client version, (in a Cowork
  session) the snapshot timestamp, each pack's context state from check 6
  (ONBOARDED / TEMPLATE / MISSING), the sandbox state from check 11, and the test command and
  baseline state from check 12, and the CI judge state from check 13. One line each. A
  WARNING does not downgrade a PASS. A TEMPLATE or MISSING context state is a
  cosmetic note with a "run context-onboarding" recommendation — it does NOT downgrade a PASS.
- **STALE SNAPSHOT — CANNOT CERTIFY** — the snapshot predates the change under test (check 0).
  State the snapshot timestamp and tell the user to start a fresh session and re-run. Do not
  report pack presence/absence as fact from a stale snapshot.
- **ANOMALIES FOUND** — a numbered list. For each: what you checked, what you expected, what you
  found, and whether it is **blocking** (the pack won't load / work) or **cosmetic**. End with the
  single most likely fix (e.g. "reinstall `blackraptor-marketing`", "run `/plugin enable …`").

Keep it short and literal — this output is meant to be pasted straight into a defect report. Do not
guess at causes you did not observe; if a check could not be run (e.g. a path was not found), say so
rather than assuming PASS.
