## 2026-08-13 — Renamed & consolidated
- **Plugin id:** `blackraptor-marketing` (unchanged). Dependency `blackraptor-bridge` → **`blackraptor-core`**.
- **Repo:** moved from `BlackRaptorAI/BlackRaptor_Agents_Marketing` into the consolidated **`BlackRaptorAI/blackraptor`** (`marketing/`). Product line: **BlackRaptor Workforce**.
- Marketplace description cleaned (removed non-measurable superlatives + the open-source-comparison claim); agents/skills/claims-gate unchanged in substance.

# Changelog — BlackRaptor Agents Marketing Team

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
