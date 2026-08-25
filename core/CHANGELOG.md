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

## [1.0.7] — 2026-08-24

### Added — audience is part of the ask
- `prompt-brief`: the Rung-2 brief template gains an **Audience** line ("who reads/executes the output; written to their register"), and the done-criteria inherit it: "executable by the named audience without further explanation". Audience is inferred and labeled ASSUMED when the ask makes it obvious; it is asked only when the audience is ambiguous and the answer would change the writing. Rung-1 pass-through asks gain no new question.
- `content-craft` (1.2.0 → **1.3.0**): §6 rule 2 now takes the audience from the brief's Audience line when one exists; when none exists, it infers the audience, states it in one line at the top of the draft, and writes every ratio, threshold, and instruction in that reader's working language (for an operator: dollars and daily actions, not basis points and NPV).

### Changed — product management holds the final pricing decision
- `product-manager` is now titled **Product Manager (CPO)** and holds the final pricing decision. Pricing strategy is *co-built*: the marketing/pricing capability brings willingness-to-pay, packaging, and competitive benchmarks; the economics capability brings margin floors and CAC/payback ceilings; product brings the value thesis and the customer job. Co-building the strategy does not mean co-deciding the price. The CPO decides, and records what went in, what was decided, and what would change it.
- Charter constraints are explicit: the CPO does not ship a price below a demonstrated margin floor, and does not overrule willingness-to-pay evidence without stating in writing what it is betting instead.

## [1.0.6] — 2026-08-21

### Added — Release 4 (writer agents + intake restate)
- **`product-docs-writer`** — a new Core agent (model Sonnet) for user-facing product documentation: user guides, getting-started walkthroughs, help and FAQ, feature explainers, general product information. External-facing, so it is **gate-wired**: every deliverable routes through the isolated `claims-gate` agent before delivery (it never gates its own copy) and follows the `content-craft` avoid-list (the TWO-GATE rule). Lives in Core because it is invoked across engineering, hardware, marketing, and product management. Tools: Read, Grep, Glob, Write, WebSearch, WebFetch.
- **`content-craft` avoid-list refresh** (`references/ai-tells.md`, §2.6): the false-candor / false-importance opener family now also catches the "one honest gap / note / thing / caveat" family, the "it's worth getting exact / getting this right" family, "worth noting", "to be clear", "the short version", and "the key thing" (owner catch from live oversight output). Refresh date bumped.

### Changed — Release 4
- **`prompt-brief` intake now authors the improved prompt.** On a non-trivial ask, after the clarifying questions the skill restates the request as a tightened, unambiguous prompt (a `## Restated prompt` block plus the short brief) and shows it for a single Approve-or-edit step before work begins (questions, then author, then approve or tweak, then run). Clear small asks still pass straight through with zero friction; honors `verbosity: brief`.
- **Onboarding copy refresh** (`context-onboarding`): gate-cleared setup-choice, path-choice (replaces the prior path-choice string), and documents-path strings; the connector clause is guarded by "if you've already connected one." The W1 welcome is unchanged.

## [1.0.5] — 2026-08-21

### Changed — core consolidation (Release 3)
- **Core-doctrine skills now live in Core only** and reach team packs via the `blackraptor-core` dependency (no more 5× duplicated copies; a core-skill edit no longer touches any team pack). The claims gate (skill + `claims-gate` agent + hook), `content-craft`, the BUSINESS-CONTEXT template, and the three producer analysts (`market-research-analyst`, `pricing-strategy-analyst`, `competitive-intel-analyst`) moved into Core — so every install is gated and has its producers by construction.

### Added
- **`clean-output`** — a new Core skill: keeps AI-attribution boilerplate and authoring-tool fingerprints out of delivered documents/commits. Hard boundary: it never removes the Claude text watermark or C2PA image credentials.
- **`content-craft` extended** (now Core): a human-voice avoid-list (`references/ai-tells.md`, on-demand), a structure menu that auto-selects by deliverable type (Minto for analytical), rhythm rules, match-length-to-ask, and a refresh rule.
- **state-file v2**: per-workstream `<slug>-state.md`, done-condition-first, ADR-disciplined decisions (immutable, supersede-not-edit), merge/tombstone rules, `STATE-INDEX.md`, and doctor staleness reporting.
- **R15 welcome/onboarding trigger hook** (Core `UserPromptSubmit`): fires the first-run welcome even on a bare "hello", silent once onboarded, fail-open. workforce-doctor gains the hook-wiring check.
- **Change-record template is roster-neutral** — it names gate ROLES; each team pack ships a `seat-list.md` (role→agent), guarded by a new `[SEAT]` check.

### Changed
- Interaction-preferences: verbosity now defaults to **brief** when unset (one contract line); the claims hook is a lean one-sentence pointer (full rule loads on demand). No user-facing strings changed.

## [1.0.4] — 2026-08-20

### Added
- **First-run welcome & interview experience (R7–R14).** `context-onboarding` now opens with a welcome (buttons "Set up now" / "Later"), runs a shared CORE interview block (seven topics) then the pack's extension set, states the effort up front, ends with a closing summary + an offer to start work, and can be deferred at any point with "Later" (partial save, resume later). Cross-pack reuse skips the core block when a business layer already exists.
- **Preferences wired up (R13).** The Core contract's interaction-preferences directive goes from four honored dimensions to **seven** (reading level, verbosity, question style, checkpoint frequency, decisions grouping, context-review cadence, units) plus optional `role`/`declined`/`offered`; adds the in-session context-review reminder (R13.2) and the observe-then-suggest tuning rules (R13.4). The `set-preferences` skill and `prefs_conformance.py` (new `validate` mode) cover all seven keys.
- `workforce-doctor` check 6 now reports the remaining UNKNOWN count for ONBOARDED files (R12e).

## [1.0.3] — 2026-08-19

### Added
- **`context-onboarding`** — a new shared Core skill (ships to all five packs): one standardized interview that teaches a pack your company/project before substantive work. Choice-first (questions / documents / mix), document-fed with per-entry provenance, clarifiers only for gaps and conflicts, approval before writing, and a dated file with a Sources section at your **project root** (never inside the pack, so pack updates cannot overwrite it). Opens with owner-ratified verbatim copy; later material produces proposed diffs, never silent rewrites (R5/R6).
- **`prompt-brief`** gains a Rung-0 context precheck: before context-dependent work, resolve the pack's context file per the resolution order; missing or still-template ⇒ run `context-onboarding` first (R3).
- **`workforce-doctor`** gains **check 6 — context onboarding**: reports each pack's context state ONBOARDED / TEMPLATE / MISSING. Non-blocking/cosmetic (R4).

## [1.0.2] — 2026-08-18

### Fixed
- `workforce-doctor` no longer certifies pack presence/absence from a stale Cowork snapshot. A Cowork cloud session copies the account plugin cache to `.claude/plugins/synced/` once at session start and never re-syncs, so a run could report a pack PRESENT that was uninstalled after the session began. Adds **check 0 (snapshot freshness)**: in a Cowork session the doctor records and reports the snapshot timestamp and returns **STALE SNAPSHOT — CANNOT CERTIFY** when the snapshot predates the pack add/remove under test. Adds a check-1 caveat that an empty `claude plugin list` under Cowork is inert by design, not an anomaly. No-op in local CLI sessions.

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
