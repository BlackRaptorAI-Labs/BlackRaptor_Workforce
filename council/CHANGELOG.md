## 2.3.1 — 2026-10-03 — New home at BlackRaptorAI-Labs

### Changed
- The project now lives at BlackRaptorAI-Labs; the old address redirects. Issues and pull requests are open; see CONTRIBUTING.

## 2.3.0 — 2026-10-03 — Seats inherit the Core verdict rules

### Changed
- **Seat verdicts follow the Core 2.3.0 verdict rules:** the evidence line starts with how it was
  obtained (MEASURED, CITED, COMPUTED, ESTIMATED or ASSUMED). See the Core pack's changelog.

## 2.2.1 — 2026-09-09 — Shorter descriptions for the pricing-strategy seat and the council skill

### Changed
- **The `pricing-strategy` seat's description and the `council` skill's description are shorter.**
  Same scope and behaviour — `pricing-strategy` still builds the pricing strategy and leaves the
  final call to `product-manager`; `/council` still convenes the same eight seats and the chair
  still closes with one decision.

## 2.2.0 — 2026-09-09 — Seat descriptions rewritten; onboarding no longer eats your first turn

### Changed
- **Seat descriptions in this pack were rewritten** to state scope more directly when you describe
  a convening or a question in your own words.
- **Onboarding now fires at session start, not on your first prompt** — see the Core pack's 2.2.0
  entry for the mechanism; this pack's seats are covered by the same change.

## 2.1.0 — 2026-09-06 — The orchestrator review step replaces the cross-review mandate; seats echo their verdict inline

### Changed
- **The seat-to-seat cross-review mandate is deleted (owner ruling D4).** The main-session `council`
  skill orchestrator is the reviewer instead: before the chair wave it reads every seat's verdict
  file, re-runs each numbers seat's model per D2a, and hands the chair the verdicts verbatim.
  Cross-review between seats is logged as a candidate feature, not built. `COUNCIL.md` §2 and §6, and
  the SKILL.md dispatch instructions, are rewritten accordingly.
- **Every seat now echoes its verdict block inline in its returned text, in addition to writing
  `council/<slug>.verdict.md` (D-64).** Seats are commonly dispatched in the background, where only
  the returned text — not a file write — reliably reaches the Stop hook before the turn ends;
  `run_in_background` is now explicitly banned for a seat dispatch, and **the chair is dispatched
  only after every seat's result has arrived (D-65).**
- The Stop hook shipped in the Core pack now also reads a seat's `council/<slug>.verdict.md` file
  when no inline block is present (D-57), and a backgrounded seat's completed background-task result
  rather than only its immediate placeholder result (D-65) — see the Core changelog.

### Measured, not fixed
- `ethics-governance` emitted one malformed verdict block during the Phase 2 regression guard
  (D-54): a fully blank fourth `standards[]` entry, a JSON-syntax defect in the model's own emission.
  17/18 verdict blocks were schema-valid across that batch; tracked as a measured contract-compliance
  rate, not a shipped fix. Ref: `docs/TEST-BATTERY-DOSSIER.md` §6(d) result — regression guard.

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
- **Corrected: hand-typed seat counts removed from the pack manifests.** The council manifests said
  "12 seats, eight of them answering to C-suite names". The seats and their names are unchanged;
  the counts are gone, and `verify.sh [MAN]` now fails the build if one reappears in a manifest.

## 2.0.0 — 2026-09-02 — Seat verdicts join the workforce vocabulary

**BREAKING: the gate verdict block changed shape** (see the Core changelog for the full v3 diff).

- **COUNCIL.md gains §3a, "Seat verdict".** Every seat now closes with `PASS | CONCERNS | BLOCK |
  COULD NOT ASSESS`, a confidence as an **integer n/10**, and a named falsifier. `BLOCK` maps to
  `FAIL` wherever a machine reads the verdict. `COULD NOT ASSESS` is blocking, never a polite
  abstention, and the chair may not resolve a convening by averaging it away.
- **The four numbers seats — `finance`, `pricing-strategy`, `coo`, `revenue` — gain `Bash`** for
  arithmetic and model computation (no file output). Their figures carry the script and inputs and
  are re-executed by a context that did not produce them before they are used.
- `chair` drops `WebSearch` and `WebFetch`, which it never used. A grant nobody exercises is a false
  capability claim.
- `ethics-governance` now emits the machine verdict block, with `COULD NOT ASSESS`.
- Spreadsheet and chart tooling references are guarded: where the helper skill is not present in the
  session, the underlying rule is stated and applied directly.

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
- **Plugin id:** `blackraptor-council` (unchanged). Dependency `blackraptor-bridge` → **`blackraptor-core`**.
- **Repo:** moved from `BlackRaptorAI/BlackRaptor_Agents` (`council/`) into the consolidated **`BlackRaptorAI/blackraptor`** (`council/`). Product line: **BlackRaptor Workforce** (displayName "Executive Council").
- Seats/skill unchanged in substance; identifiers/display/paths only.

# Changelog — BlackRaptor Advisory Council

All notable changes to the `blackraptor-council` plugin are recorded here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [1.3.0] — 2026-08-24

### Added — two new seats (roster 10 → 12)
- **`coo` — Chief Operating Officer.** Added a COO (Chief Operating Officer) seat to the Executive Council. The council lacked an operations role, so we added one. Execution sequencing, operating cadence, unit-level P&L discipline, who-does-what-by-when. Function-defined; industry comes from the context file or the prompt like every other seat. The `council` skill names ops-heavy asks (turnarounds, operating cadence, unit economics, fix-vs-close calls) as explicit COO triggers.
- **`chair` — Chair / Chief of Staff.** Runs the convening, forces the disagreement onto the table, synthesizes without averaging, and hands the human **one decision at a time** with each branch's trade-off named. Carries no domain vote. The `council` skill routes final synthesis through it as a second dispatch, after the domain seats report.
- **Both seats are advisory only.** Neither may execute. `growth-engine` remains the sole executing seat, under human-in-the-loop approval; `ethics-governance` retains standing to BLOCK, and the chair surfaces a block unresolved rather than balancing it away.

### Changed — C-suite titles (display names; slugs unchanged)
Eight council seats now answer to conventional C-suite display names and a ninth, the chair,
runs the convening; three seats
(`pricing-strategy`, `fundraising-ir`, `growth-engine`) keep slug-only naming. **No slug
changed.** Slugs remain the load-bearing identifiers (`COUNCIL.md` §7) and every existing
reference keeps working. Titles are carried in `COUNCIL.md` §5, the pack and skill
descriptions, and docs; a request naming a title resolves to its slug. The individual seat
descriptions keep their slug wording.

The nine named council seats (eight C-suite titles plus the Chair), then the Core-pack CPO
anchor, which is not one of the 12:

| Title | Seat (slug) |
|---|---|
| CFO — Chief Financial Officer | `finance` |
| CRO — Chief Revenue Officer | `revenue` |
| CHRO — Chief HR Officer | `people-org` |
| CTO — Chief Technology Officer | `technology-strategy` |
| General Counsel | `ethics-governance` |
| CMO — Market Truth | `market-insight` |
| CMO — GTM Strategy | `gtm-strategy` |
| COO — Chief Operating Officer | `coo` *(new)* |
| Chair / Chief of Staff | `chair` *(new)* |
| CPO — Chief Product Officer | `product-manager` *(Core pack)* |

- Two seats cover the CMO function: `market-insight` (what is true of the market) and `gtm-strategy` (how we go at it). Asking for "the CMO" convenes both unless the ask names one.
- **No CEO seat:** the user is the CEO. There is no CIO seat and no CSO seat. Asking for a CEO says so and convenes `chair` instead.

### Changed — pricing authority moves to the CPO
- `pricing-strategy` no longer claims to be "the only seat that owns the price metric" or to "make the pricing decision". It **authors the pricing strategy and analysis** with `gtm-strategy`, `finance`, and `market-insight`; the **final pricing decision belongs to `product-manager` (CPO)**. The seat states its recommendation as a recommendation, names the margin floor and willingness-to-pay evidence it rests on, and records the delta if the CPO decides otherwise.
- `COUNCIL.md` §4 (co-decisions) updated to match: pricing is co-built, then decided by the CPO.

### Migration
No action required. Slugs, `subagent_type` values, and existing references are unchanged; this
release is additive plus display-name and authority-text changes. Installs that pinned seat
slugs keep working as-is.

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
