---
name: workforce-doctor
description: >-
  Diagnose an installed BlackRaptor Workforce — confirm the packs are present, versioned consistently, and structurally intact (dependencies resolve; the core hooks are wired for the current client). Read-only. Run when something seems off, or before filing a defect.
---

# Workforce Doctor

A read-only health check for an installed BlackRaptor Workforce. It reads local files and the
plugin list only — **no network, no writes, no hashing**. Use it to catch a broken or partial
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
   - `command -v python3` succeeds. The write gate and the verdict validator run in Python; without
     `python3` on PATH both fail open and check nothing, so a missing `python3` is an anomaly.
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

11. **Sandbox (report-only).** Read `sandbox.enabled` from `.claude/settings.local.json`, then
   `.claude/settings.json`, then `~/.claude/settings.json` (the first file that sets it wins; quote the
   file and the value). `true`: the setting alone does not prove the sandbox runs, so probe it. On Linux,
   run `command -v bwrap socat` and quote the output: if either is missing, report a **WARNING**,
   "sandbox configured but inactive (missing: <the missing names>)", since Claude Code turns the sandbox
   off without them; if both are present, report **sandbox on**. On macOS, report "sandbox configured;
   active state not probed". Unset or `false`: report a
   **WARNING**, "sandbox off: shell commands can write outside the repo; set `sandbox.enabled` to `true`
   in `.claude/settings.json` (or run `/workforce-init`, or `/sandbox`)". Never an anomaly and never a
   FAIL: the sandbox is the user's choice. The sandbox covers shell commands only; hooks run outside it.

## Report format

Emit one of:

- **PASS** — list the packs and versions you confirmed, the client version, (in a Cowork
  session) the snapshot timestamp, each pack's context state from check 6
  (ONBOARDED / TEMPLATE / MISSING), and the sandbox state from check 11. One line each. A
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
