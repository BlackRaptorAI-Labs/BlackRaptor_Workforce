## 2026-08-13 — Renamed & consolidated
- **Plugin id:** `blackraptor-bridge` → **`blackraptor-core`**. Now the auto-installed dependency of all four packs (Engineering, Executive Council, Marketing, Hardware Engineering).
- **Repo:** moved from `BlackRaptorAI/BlackRaptor_Agents` (`bridge/`) into the consolidated **`BlackRaptorAI/blackraptor`** (`core/`). Product line: **BlackRaptor Workforce**.
- `product-manager`, `evidence-auditor`, and the `research-integrity` skill unchanged in substance; identifiers/display/paths only.

# Changelog — BlackRaptor Bridge

All notable changes to the `blackraptor-bridge` plugin are recorded here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

The bridge is the shared dependency auto-installed with the dev-team, council,
marketing, and HW-engineering plugins — it holds the cross-cutting agents and
skills those teams share.

## [1.0.1] — 2026-08-17

### Fixed
- Ships `workforce-doctor` to existing installs (prior release omitted the version bump). The skill was already committed to the pack, but the plugin version wasn’t bumped, so `claude plugin update` treated installs as current and never delivered it — this patch re-releases with a bumped version. Tracked in BlackRaptorAI/blackraptor#1.

## [1.0.0] — 2026-07-22

### Added
- **`product-manager`** — the end-to-end product owner (requirement intake →
  buildable definition: outcome thesis, target customer, jobs-to-be-done,
  problem statement, user stories, acceptance criteria, success metrics). Merges
  the former council `product-strategy` seat and the dev `product-manager`.
- **`evidence-auditor`** — the HEAVY-tier adversarial gate for research,
  analysis, and evidence-based reporting (source grading, citation-chain
  collapse, root-veracity vs reachability, release gate). The research analog of
  `red-team-reviewer`.
- **`research-integrity`** skill — tiered LITE / STANDARD / HEAVY, with
  `evidence-auditor` as its HEAVY reviewer.
- Ships with LICENSE + NOTICE; auto-installed as a `dependencies` entry of the
  team plugins, namespaced `blackraptor-bridge:…`.
