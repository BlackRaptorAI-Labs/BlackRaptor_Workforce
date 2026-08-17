## 2026-08-13 — Renamed & consolidated
- **Plugin id:** `blackraptor-council` (unchanged). Dependency `blackraptor-bridge` → **`blackraptor-core`**.
- **Repo:** moved from `BlackRaptorAI/BlackRaptor_Agents` (`council/`) into the consolidated **`BlackRaptorAI/blackraptor`** (`council/`). Product line: **BlackRaptor Workforce** (displayName "Executive Council").
- Seats/skill unchanged in substance; identifiers/display/paths only.

# Changelog — BlackRaptor Advisory Council

All notable changes to the `blackraptor-council` plugin are recorded here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

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
