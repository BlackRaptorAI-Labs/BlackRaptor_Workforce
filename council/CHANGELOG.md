## 2026-08-13 — Renamed & consolidated
- **Plugin id:** `blackraptor-council` (unchanged). Dependency `blackraptor-bridge` → **`blackraptor-core`**.
- **Repo:** moved from `BlackRaptorAI/BlackRaptor_Agents` (`council/`) into the consolidated **`BlackRaptorAI/blackraptor`** (`council/`). Product line: **BlackRaptor Workforce** (displayName "Executive Council").
- Seats/skill unchanged in substance; identifiers/display/paths only.

# Changelog — BlackRaptor Advisory Council

All notable changes to the `blackraptor-council` plugin are recorded here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [1.2.6] — 2026-08-21

### Changed — core consolidation (Release 3)
- The shared core-doctrine skills (contract, gates, onboarding, change-record, state-file v2, content-craft, the claims gate, etc.) are no longer duplicated into this pack — they install with the `blackraptor-core` dependency. A council-only install now also has its producer analysts (market-research / pricing / competitive-intel), which moved to Core. Adds a roster-neutral change-record template + this pack's `seat-list.md`. No user-facing strings changed.

## [1.2.5] — 2026-08-20

### Added
- First-run welcome & interview experience (R7–R14, via the shared `context-onboarding` skill): welcome → path choice → shared core interview → council extension (remaining business-context fields, never re-asking core) → friendly settings round → closing summary → offer to start. The seven-dimension preference wire-up (R13) rides the shared Core contract.

## [1.2.4] — 2026-08-19

### Changed
- The council now grounds on `BUSINESS-CONTEXT.md` at your **project root** via the standardized resolution order; if it is missing or still the blank template, the council invokes the shared `context-onboarding` skill first (interviewing against the business-context template fields) and writes the approved, dated file to the project root — never into the pack (R1–R3). The in-pack `business-context` template now carries a `<!-- TEMPLATE — not onboarded -->` marker so "still template" is machine-checkable.

## [1.2.3] — 2026-08-18

### Fixed
- `workforce-doctor` no longer certifies pack presence/absence from a stale Cowork snapshot. A Cowork cloud session copies the account plugin cache to `.claude/plugins/synced/` once at session start and never re-syncs, so a run could report a pack PRESENT that was uninstalled after the session began. Adds **check 0 (snapshot freshness)**: in a Cowork session the doctor records and reports the snapshot timestamp and returns **STALE SNAPSHOT — CANNOT CERTIFY** when the snapshot predates the pack add/remove under test. Adds a check-1 caveat that an empty `claude plugin list` under Cowork is inert by design, not an anomaly. No-op in local CLI sessions.

## [1.2.2] — 2026-08-17

### Fixed
- Ships `workforce-doctor` to existing installs (prior release omitted the version bump). The skill was already committed to the pack, but the plugin version wasn’t bumped, so `claude plugin update` treated installs as current and never delivered it — this patch re-releases with a bumped version. Tracked in BlackRaptorAI/blackraptor#1.

## [1.2.1] — 2026-08-01

### Fixed
- Pre-launch scrub: removed the last private-instance attribution residue (the
  private operating-company name and its private agent-repo name) from `NOTICE`,
  `COUNCIL.md`, and `skills/council/references/COUNCIL.md` — now generalized to
  "a real operating company" / "the BlackRaptor Agents development team", matching
  the already-scrubbed `README.md` and `VISION.md`.
- Corrected stale "twelve seats" copy in `README.md` and `VISION.md` to
  **eleven** (the 12 → 11 seat change shipped in 1.2.0; the prose lagged).

## [1.2.0] — 2026-07-22

### Changed
- **`product-strategy` merged into the shared `product-manager`** and moved to the
  new `blackraptor-bridge` plugin (auto-installed as a dependency). The
  `council-orchestrator` still convenes it as the product/strategy anchor — every
  cross-reference in the seats, `COUNCIL.md`, and the Definition Brief now points to
  `product-manager`. Council seats 12 → 11.
- `plugin.json` now declares `"dependencies": ["blackraptor-bridge"]`; the bridge
  also brings the council its `evidence-auditor` gate.

## [1.1.0] — 2026-07-22

### Added — skills
- **`council`** — the plugin now ships a skill, not just agents. Say "convene the
  council" (or `/council`) to run the full challenge protocol: it grounds itself in
  `BUSINESS-CONTEXT.md`, frames the decision as a one-way/two-way door, delegates to
  the `council-orchestrator` sub-agent for independent parallel seat drafts +
  anonymized cross-review, enforces the output contract (steelman FOR/AGAINST,
  confidence-tagged evidence, mandatory "What You Lose"), and synthesizes without
  averaging. Self-contained under `skills/council/` with its `references/` bundle
  (`COUNCIL.md`, `business-context.md`, `definition-brief.md`). Brings the public
  port to full 9-skill parity with the golden source.

### Changed
- Plugin manifest declares `"skills": "./skills/"`.

## [1.0.0] — 2026-07-21

Initial public release of the Executive Advisory Council as a Claude Code plugin:
12 seats coordinated by the `council-orchestrator` under the challenge protocol.
