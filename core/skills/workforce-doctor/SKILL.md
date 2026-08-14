---
name: workforce-doctor
description: >-
  Diagnose an installed BlackRaptor Workforce — confirm the packs are present, versioned
  consistently, and structurally intact (dependencies resolve; the marketing claims-gate hook
  is wired correctly for the current client). Read-only. Run when something seems off, or before
  filing a defect. Say "run workforce-doctor" (or /workforce-doctor).
---

# Workforce Doctor

A read-only health check for an installed BlackRaptor Workforce. It reads local files and the
plugin list only — **no network, no writes, no hashing**. Use it to catch a broken or partial
install before it wastes your time, and to attach a clean diagnosis to a defect report.

## What to check

Work through these and collect anomalies as you go. Report **PASS** only if every check passes.

1. **Installed packs + versions.** Run `claude plugin list`. Note each installed BlackRaptor pack
   (`blackraptor-engineering`, `blackraptor-council`, `blackraptor-marketing`, `blackraptor-hardware`,
   `blackraptor-core`) and its version and enabled/disabled state. Anomaly: a pack shows `disabled`,
   or a pack the user believes they installed is absent.

2. **Core dependency resolves.** Any team pack (`engineering`, `council`, `marketing`, `hardware`)
   must pull in **`blackraptor-core`**. If any team pack is installed but `blackraptor-core` is not
   listed, that is an anomaly (dependency did not resolve).

3. **Per-pack file inventory + manifest version.** For each installed pack, read its
   `.claude-plugin/plugin.json` from the install location (`claude plugin list` / the marketplace
   directory shows it). Confirm the manifest exists and its `"name"` matches the pack id above, its
   `"version"` matches what `claude plugin list` reports, and the pack ships its expected top-level
   dirs (`agents/`, `skills/`, and for a team pack a `CLAUDE.md`, `LICENSE`, `NOTICE`). Anomaly: a
   missing manifest, a name/version mismatch, or an empty `agents/` or `skills/`.

4. **Marketing claims-gate hook (only if `blackraptor-marketing` is installed).** Three checks:
   - `marketing/hooks/hooks.json` is present.
   - `marketing/hooks/inject-claims-gate-rule.sh` is present **and executable** (`test -x`). A hook
     the client cannot execute is a silently disabled rule.
   - the marketing `plugin.json` does **NOT** declare `"hooks": "./hooks/hooks.json"`. On client
     2.1.170+ `hooks/hooks.json` auto-loads by convention, so declaring it is a fatal
     "Duplicate hooks file detected" load failure. If the key is present, that is a **blocking**
     anomaly — the marketing pack will not load.

5. **Client version.** Record `claude --version`. Note it in the report — hook-loading and
   marketplace behavior have varied across client versions.

## Report format

Emit one of:

- **PASS** — list the packs and versions you confirmed, and the client version. One line each.
- **ANOMALIES FOUND** — a numbered list. For each: what you checked, what you expected, what you
  found, and whether it is **blocking** (the pack won't load / work) or **cosmetic**. End with the
  single most likely fix (e.g. "reinstall `blackraptor-marketing`", "run `/plugin enable …`").

Keep it short and literal — this output is meant to be pasted straight into a defect report. Do not
guess at causes you did not observe; if a check could not be run (e.g. a path was not found), say so
rather than assuming PASS.
