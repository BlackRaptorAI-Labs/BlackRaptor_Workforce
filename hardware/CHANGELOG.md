## 2.3.0 — 2026-10-03 — Hardware gates inherit the Core verdict rules

### Changed
- **`compliance-cert` and `hw-design-reviewer` follow the Core 2.3.0 verdict rules:** the evidence
  line starts with how it was obtained. See the Core pack's changelog.

## 2.2.1 — 2026-09-09 — Shorter descriptions for the hw-operating-standard and hw-program skills

### Changed
- **The `hw-operating-standard` and `hw-program` skill descriptions are shorter.** Same scope and
  behaviour — `hw-operating-standard` still loads before any hardware or firmware task, and
  `hw-program` still owns the decision register and interfaces, not the discipline work itself.

## 2.2.0 — 2026-09-09 — Seat descriptions rewritten; onboarding no longer eats your first turn

### Changed
- **Seat descriptions in this pack were rewritten** to state scope more directly when you describe
  a problem in your own words.
- **Onboarding now fires at session start, not on your first prompt** — see the Core pack's 2.2.0
  entry for the mechanism; this pack's seats are covered by the same change.

## 2.1.0 — 2026-09-06 — `hw-program` is executable from its own text

### Added
- **`hw-program` skill made executable**: a decision-register template, an interface-control
  template and a handoff template, each with one worked example row; PDR, CDR and MRR exit criteria
  per seat; a tie-break rule for cross-domain disagreement.
- **`hw-seat-rules`**: a shared include (at most 40 lines) build-included into all nine hardware
  bodies, replacing nine separate copies of the same rules. `hw-operating-standard` is cut down to
  its hardware-specific sections now that the shared material lives in one place.
- `PROGRAM-CONTEXT.md` rewritten with explicit fields and one filename. The cross-domain
  hardware review matrix is unchanged.

### Measured, not fixed
- `compliance-cert` emitted one malformed verdict block during Phase 2 calibration testing
  (D-53): a missing closing bracket in its `standards[]` array, a JSON-syntax defect in the model's
  own emission, not a hook or schema bug. Tracked as a measured contract-compliance rate (32/33
  verdict blocks schema-valid across the calibration batch), not a shipped fix. Ref:
  `docs/TEST-BATTERY-DOSSIER.md` §6(c) calibration read.

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
- **Retracted: "Testing showed this pairing outperforms any single agent."** The hardware README
  said this of the producer → `hw-design-reviewer` → revise loop. No such test exists. The loop is
  kept because self-review cannot catch the producer's own blind spots, which is an argument from
  design, not from measurement.
- **Removed: the pointer to `docs/model-gap-test-report.md`.** The hardware operating standard and
  the pack's `CLAUDE.md` cited that report; **the file has never existed** in this pack or any
  other.

## 2.0.0 — 2026-09-02 — The analysis seats can run their own analysis

**BREAKING: the gate verdict block changed shape** (see the Core changelog for the full v3 diff).

- **`power-electronics`, `thermal-mechanical`, `reliability-dfr` and `cost-engineer` gain `Bash` and
  `Write`**, restricted by charter to the program's `sim/` directory as the only write target. Each
  was previously told to "run all arithmetic programmatically" and to "keep or extend the program's
  `sim/` scripts" while holding `Read, Grep, Glob` — an instruction the grant could not obey.
- **`hw-design-reviewer` gains `Bash`** to re-execute a seat's `sim/` script on its stated inputs.
  It never authors one: it is the reviewer, and per D2a its job is to re-run the producer's number
  and record match or mismatch. A mismatch goes back to the producing seat and is never averaged.
- Every computed figure now ships with its script and inputs and is marked pending re-execution
  until a context that did not produce it re-runs it.
- `compliance-cert` and `hw-design-reviewer` now emit the machine verdict block, with a falsifier and
  `COULD NOT ASSESS`. For `compliance-cert`, `standards[]` is load-bearing: a conformance claim with
  no test record is a FAIL, not a CONCERNS.
- `compliance-cert`'s description drops an internal build-history note that had no meaning outside
  the maintainers' repository.
- `cost-engineer` drops an uncited "~80% of change-cost" figure; the substantive point stands
  without a number nobody could source.

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
- **Plugin id:** `blackraptor-hw-engineering` → **`blackraptor-hardware`** ("HW" → "Hardware"). Dependency `blackraptor-bridge` → **`blackraptor-core`**.
- **Repo:** moved from `BlackRaptorAI/BlackRaptor_Agents_HW_Engineering` into the consolidated **`BlackRaptorAI/blackraptor`** (`hardware/`). Product line: **BlackRaptor Workforce**.
- Seats/skills/design doctrine unchanged in substance; identifiers/display/paths only.

# Changelog — BlackRaptor Agents, HW Engineering Team

## 1.2.5 — 2026-08-21

- Core consolidation (Release 3): the shared core-doctrine skills are no longer duplicated into this pack; they install with the `blackraptor-core` dependency. Adds a roster-neutral change-record template + this pack's `seat-list.md` (hardware gate roles → agents: hw-design-reviewer, compliance-cert, reliability-dfr, manufacturing-dfm). No user-facing strings changed.

## 1.2.4 — 2026-08-20

- First-run welcome & interview experience (R7–R14) via the shared `context-onboarding` skill. Adds the units display preference (R13.3): `hw-operating-standard` reads the `units` USER-PREFS key and presents quantities as metric / imperial / both (default) — display only, dimension checks unaffected. Seven-dimension preference wire-up (R13) via the shared Core contract.

## 1.2.3 — 2026-08-19

- `hw-operating-standard` gains the standardized context trigger: before substantive work on a program, resolve its `PROGRAM-CONTEXT-<program>.md` at the **project root** per the resolution order; if missing or still the template, invoke the shared `context-onboarding` skill first (interviewing against the program-context template fields) and write the approved, dated file to the project root — never into the pack (R1–R3). The in-pack `templates/program-context.md` now carries a `<!-- TEMPLATE — not onboarded -->` marker.

## 1.2.2 — 2026-08-18

- `workforce-doctor` no longer certifies pack presence/absence from a stale Cowork snapshot. A Cowork cloud session copies the account plugin cache to `.claude/plugins/synced/` once at session start and never re-syncs, so a run could report a pack PRESENT that was uninstalled after the session began. Adds **check 0 (snapshot freshness)**: in a Cowork session the doctor records and reports the snapshot timestamp and returns **STALE SNAPSHOT — CANNOT CERTIFY** when the snapshot predates the pack add/remove under test. Adds a check-1 caveat that an empty `claude plugin list` under Cowork is inert by design, not an anomaly. No-op in local CLI sessions.

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
