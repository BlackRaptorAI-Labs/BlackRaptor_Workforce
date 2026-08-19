---
name: workforce-doctor
description: >-
  Diagnose an installed BlackRaptor Workforce — confirm the packs are present, versioned
  consistently, and structurally intact (dependencies resolve; the marketing claims-review hook
  is wired correctly for the current client). Read-only. Run when something seems off, or before
  filing a defect. Say "run workforce-doctor" (or /workforce-doctor).
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

4. **Marketing claims-review hook (only if `blackraptor-marketing` is installed).** Three checks:
   - `marketing/hooks/hooks.json` is present.
   - the injector script in `marketing/hooks/` is present **and executable** (`test -x`). A hook
     the client cannot execute is a silently disabled rule.
   - the marketing `plugin.json` does **NOT** declare `"hooks": "./hooks/hooks.json"`. On client
     2.1.170+ `hooks/hooks.json` auto-loads by convention, so declaring it is a fatal
     "Duplicate hooks file detected" load failure. If the key is present, that is a **blocking**
     anomaly — the marketing pack will not load.

5. **Client version.** Record `claude --version`. Note it in the report — hook-loading and
   marketplace behavior have varied across client versions.

6. **Context onboarding (per pack).** For each installed pack that uses a context file, resolve it
   per the documented order (current working / project root → an explicit path the user named) and
   report one of three states:
   - **ONBOARDED** — a filled context file is present, has **no** `<!-- TEMPLATE — not onboarded -->`
     first-line marker, and carries a date stamp.
   - **TEMPLATE** — the template marker is present (onboarding has not been run).
   - **MISSING** — no context file found at the resolved location.
   Expected file names at the project root: `BUSINESS-CONTEXT.md` (council), `MARKETING-CONTEXT.md`
   (marketing), `PROGRAM-CONTEXT-<program>.md` (hardware); engineering uses the project's existing
   convention. This check is **non-blocking / cosmetic**: report the state and, for TEMPLATE or
   MISSING, recommend running `context-onboarding` — **never fail the install for it**. In a Cowork
   session, check the connected project folder; if no project folder is connected, say so rather
   than reporting MISSING.

## Report format

Emit one of:

- **PASS** — list the packs and versions you confirmed, the client version, (in a Cowork
  session) the snapshot timestamp, and each pack's context state from check 6
  (ONBOARDED / TEMPLATE / MISSING). One line each. A TEMPLATE or MISSING context state is a
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
