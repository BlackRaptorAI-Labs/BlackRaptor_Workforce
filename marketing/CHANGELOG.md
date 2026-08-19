## 2026-08-13 — Renamed & consolidated
- **Plugin id:** `blackraptor-marketing` (unchanged). Dependency `blackraptor-bridge` → **`blackraptor-core`**.
- **Repo:** moved from `BlackRaptorAI/BlackRaptor_Agents_Marketing` into the consolidated **`BlackRaptorAI/blackraptor`** (`marketing/`). Product line: **BlackRaptor Workforce**.
- Marketplace description cleaned (removed non-measurable superlatives + the open-source-comparison claim); agents/skills/claims-gate unchanged in substance.

# Changelog — BlackRaptor Agents Marketing Team

## 1.1.5 — 2026-08-19

- **Marketing context is now update-proof.** The filled context lives at your **project root** as `MARKETING-CONTEXT.md`; the in-pack `context/marketing-context.md` is a blank **template** only (now marked `<!-- TEMPLATE — not onboarded -->`), so a pack update can no longer overwrite your filled context (R1/R2). `marketing-core` resolves the project-root file per the standardized resolution order and, when it is missing or still the template, invokes the shared `context-onboarding` skill (R3) — which uses the new marketing question set (`marketing-core/references/context-questions.md`) and preserves the §6 hard-gate rules. Context updates now propose a diff rather than silently rewriting.

## 1.1.4 — 2026-08-18

- `workforce-doctor` no longer certifies pack presence/absence from a stale Cowork snapshot. A Cowork cloud session copies the account plugin cache to `.claude/plugins/synced/` once at session start and never re-syncs, so a run could report a pack PRESENT that was uninstalled after the session began. Adds **check 0 (snapshot freshness)**: in a Cowork session the doctor records and reports the snapshot timestamp and returns **STALE SNAPSHOT — CANNOT CERTIFY** when the snapshot predates the pack add/remove under test. Adds a check-1 caveat that an empty `claude plugin list` under Cowork is inert by design, not an anomaly. No-op in local CLI sessions.

## 1.1.3 — 2026-08-17

- Ships `workforce-doctor` to existing installs (prior release omitted the version bump). The skill was already committed to the pack, but the plugin version wasn’t bumped, so `claude plugin update` treated installs as current and never delivered it — this patch re-releases with a bumped version. Tracked in BlackRaptorAI/blackraptor#1.

## 1.1.0 — 2026-07-23

- **Pre-launch hygiene (2026-08-01):** all bundled skills carry `metadata.version: "1.1.0"`
  (aligned with the plugin); the `compliance-claims-gate` verdict vocabulary now uses the
  shared `PASS | CONCERNS | FAIL` words; `install.sh` ships LICENSE + NOTICE into the target.

- **Research rigor wired to the bridge:** plugin now declares
  `dependencies: ["blackraptor-bridge"]` (evidence-auditor adversarial research
  gate + research-integrity skill + product-manager). Installing from the main
  `blackraptor-ai` marketplace (where this plugin is also listed) auto-installs
  the bridge; this repo's own marketplace allowlists `blackraptor-ai` for
  cross-marketplace dependency resolution.
- Submission-grade plugin metadata (displayName, homepage, repository, license)
  and explicit `skills` path.

## 1.0.0 — 2026-07-23

First public release.

- 15 agents + 9 skills, extracted from the validated marketing-team packet
  (claude plugin validate: 0 errors) and uplifted to the BlackRaptor operating
  standard:
  - **Team banner** on every charter (Marketing Team, golden-source pointer).
  - **Who you are** — 20+-year world-class practitioner identity per role
    (voice, not evidence).
  - **Customer-experience north star** — binding, shared with every BlackRaptor
    team (need/want → ease → works-as-expected → trust, loyalty,
    willingness-to-spend).
  - **Output-quality discipline** — the excellence-pass five checks as an
    explicit final pass; never ship a first draft.
- Added the `excellence-pass` skill (9th skill) so the discipline is
  self-contained.
- `context/marketing-context.md` ships as a **blank onboarding template**
  (the packet's configured worked example was company-specific and is not
  published; run the marketing-core onboarding to configure for your product).
- Marketplace manifest (`.claude-plugin/marketplace.json`) for Claude Code CLI
  install; vendoring `install.sh`. Cowork uses the plugin catalog, or manual
  `SKILL.md` upload from `marketing/skills/` where plugins aren't available.
