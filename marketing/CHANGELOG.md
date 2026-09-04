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
- **Qualified: "Marketing context is now update-proof."** The mechanism is real — your filled
  context lives at the project root and the pack ships only the template, so an update cannot
  overwrite it. "-proof" claims more than the mechanism delivers; read it as "an update does not
  overwrite your filled context".
- **Corrected: the specialist list in the pack manifest.** It named 14 domains (15 in the
  marketplace entry) while the pack ships **11** agents — market research, competitive intel and
  pricing moved to Core at the rename. The list now matches what ships.

## 2.0.0 — 2026-09-02 — The claims register becomes data

**BREAKING: the gate verdict block changed shape** (see the Core changelog for the full v3 diff).

- **The retired-claims list moved out of the `claims-gate` body and into the Marketing Intelligence
  Core, §4b**, with a real schema: the claim, why it was retired, the proof standard that would be
  needed to revive it, the date, and an owner. The gate reads the register and quotes the row in its
  verdict instead of carrying a hardcoded list. §4a gains the same shape for cleared claims.
- If the Core file is unreachable, the gate returns `COULD NOT ASSESS` for the retired-claims check
  rather than guessing the list.
- `copywriter`, `creative-director` and `video-creative-producer` previously pointed at
  `content-craft` references through the Marketing plugin root, where they could never resolve —
  `content-craft` ships in Core. They now name the Core skill.
- `social-community-manager`'s human-approval rule no longer cites a Core section number that does
  not exist; it states the rule.

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
- **Plugin id:** `blackraptor-marketing` (unchanged). Dependency `blackraptor-bridge` → **`blackraptor-core`**.
- **Repo:** moved from `BlackRaptorAI/BlackRaptor_Agents_Marketing` into the consolidated **`BlackRaptorAI/blackraptor`** (`marketing/`). Product line: **BlackRaptor Workforce**.
- Marketplace description cleaned (removed non-measurable superlatives + the open-source-comparison claim); agents/skills/claims-gate unchanged in substance.

# Changelog — BlackRaptor Agents Marketing Team

## 1.1.7 — 2026-08-21

- Core consolidation (Release 3). The shared core-doctrine skills are no longer duplicated into this pack; they install with the `blackraptor-core` dependency. The **claims gate** (skill + agent + hook), **content-craft**, and the three **producer analysts** (market-research / pricing-strategy / competitive-intel) moved to Core — the claims gate now protects every install by construction, and marketing keeps its proof-standards / claims ledger in its register. Marketing roster is now **11 agents + 7 marketing skills**. Adds this pack's `seat-list.md`. No user-facing strings changed.

## 1.1.6 — 2026-08-20

- First-run welcome & interview experience (R7–R14) via the shared `context-onboarding` skill: welcome → path → shared core interview → marketing extension (brand/personas/GTM/voice/competitors/proof standards, reorganized to never re-ask core) → friendly settings round → closing summary → offer to start. The marketing question set is now an extension set that deepens core answers. Seven-dimension preference wire-up (R13) via the shared Core contract; §6 hard gates preserved.

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
  - **Who you are** — 20+-year senior practitioner identity per role
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
