## 2026-08-13 — Renamed & consolidated
- **Plugin id:** `blackraptor-hw-engineering` → **`blackraptor-hardware`** ("HW" → "Hardware"). Dependency `blackraptor-bridge` → **`blackraptor-core`**.
- **Repo:** moved from `BlackRaptorAI/BlackRaptor_Agents_HW_Engineering` into the consolidated **`BlackRaptorAI/blackraptor`** (`hardware/`). Product line: **BlackRaptor Workforce**.
- Seats/skills/design doctrine unchanged in substance; identifiers/display/paths only.

# Changelog — BlackRaptor Agents, HW Engineering Team

## 1.2.1 — 2026-08-17

- Ships `workforce-doctor` to existing installs (prior release omitted the version bump). The skill was already committed to the pack, but the plugin version wasn’t bumped, so `claude plugin update` treated installs as current and never delivered it — this patch re-releases with a bumped version. Tracked in BlackRaptorAI/blackraptor#1.

## 1.2.0 — 2026-08-01

Pre-launch hardening (packaging + first-run correctness). No agent-capability changes.

- **First run defined.** The nine program seats opened with "read the program's
  `PROGRAM-CONTEXT.md` and decision register" but had no behavior when it is
  absent — which is every first run. They now read those inputs if present and,
  if absent, ask the user for the essentials inline and never invent context
  (the council-skill pattern).
- **Plugin-root path resolution.** `hw-operating-standard/SKILL.md` referenced
  `TEAM.md`, `docs/…`, and `templates/program-context.md` by bare relative path,
  which resolves against the user's project root under a marketplace install.
  All are now `${CLAUDE_PLUGIN_ROOT}/…` so they resolve to the plugin. The
  vendored `CLAUDE.md` keeps bare paths (correct for its load context).
- **Removed dangling references** to the deleted 4-task × 3-model gap-test report
  (it correctly did not ship) across `README.md`, this changelog, and the skill;
  softened the "empirically-tested" claim to match the standard's own hedge.
- **Synced the bundled Agent Operating Standard v2 copy** with the corrected text
  — adds the "treat the five behaviors as a hypothesis, not a measured result"
  hedge and fixes the model-tier wording (a leftover find/replace).

## 1.1.0 — 2026-07-24

Market grounding + research validation via the shared bridge.

- **`blackraptor-bridge` is now a dependency** (auto-installs with the plugin
  from the `blackraptor-ai` marketplace; this repo's own marketplace allowlists
  it via `allowCrossMarketplaceDependenciesOn`). Rationale: the team's
  design-to-cost doctrine polices over-design *against the requirements*, but
  nothing validated the requirements themselves against market need.
- **`systems-integration`**: new *requirement provenance* duty — every
  `PROGRAM-CONTEXT.md` requirement traces to customer need or an explicit
  founder decision; `blackraptor-bridge:product-manager` is convened at
  requirement intake, at PDR, and for post-PDR scope additions.
- **`cost-engineer`** and **`compliance-cert`**: research-validation rule —
  load-bearing external research claims (pricing, lead times, lifecycle/EOL,
  standards applicability, market access) get research-integrity discipline and
  `blackraptor-bridge:evidence-auditor` adversarial validation before they
  harden into purchases, cert plans, or the financial model.
- **TEAM.md / CLAUDE.md / hw-operating-standard skill**: new "Market grounding
  and research validation" doctrine; division of labor stated — the bridge
  validates market fit and research claims, `hw-design-reviewer` keeps math and
  engineering verification.
- Existing installs: `claude plugin update` does **not** pull a newly-declared
  dependency — add the bridge once with
  `claude plugin install blackraptor-bridge@blackraptor-ai` (fresh installs get
  it automatically).

## 1.0.0 — 2026-07-24

Initial public release.

- **10 agents** in `hw-engineering/agents/`: the nine seats — `systems-integration`
  (Opus, conductor), `power-electronics` (Opus), `thermal-mechanical` (Opus),
  `rf-connectivity` (Opus), `embedded-firmware` (Sonnet), `reliability-dfr` (Opus),
  `compliance-cert` (Sonnet), `manufacturing-dfm` (Sonnet), `cost-engineer`
  (Sonnet) — plus the cross-cutting `hw-design-reviewer` (Opus) gate.
- **Operating standard**: `hw-engineering/CLAUDE.md` (HW/firmware adaptation of the
  Agent Operating Standard v2, incl. the Excellence Pass), with the full general
  standard behind it in
  `hw-engineering/docs/`. Also shipped as the `hw-operating-standard` **skill**
  (`hw-engineering/skills/`) so plugin installs load it too — plugin-root
  CLAUDE.md files are not loaded as project context.
- **Process**: `hw-engineering/TEAM.md` — roster, model tiers, cross-review matrix,
  PDR → bench characterization → CDR → MRR gates, and the Manufacturing Data
  Package definition.
- **Program template**: `hw-engineering/templates/program-context.md` — every
  program supplies its own `PROGRAM-CONTEXT.md`; the agents are product-agnostic.
- Packaged as the `blackraptor-hw-engineering` plugin; listed in this repo's own
  marketplace and in the main `blackraptor-ai` marketplace
  (`BlackRaptorAI/BlackRaptor_Agents`).
- Retired definitions (`hw-architect`, `firmware-engineer` — absorbed into
  `systems-integration` and `embedded-firmware`) preserved in
  `archive/superseded-agents/`, outside the plugin path so they never load.
