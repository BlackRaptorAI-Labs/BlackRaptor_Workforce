## 2.3.3 — 2026-10-09 — Verdicts must be signed by the gate that gave them

### Changed
- **A PASS needs evidence someone can re-check.** Verdict schema 3.2: a PASS opens with MEASURED,
  CITED, COMPUTED or ESTIMATED (never ASSUMED) and names at least one `path:line` or a command in
  backticks. A test-quality or completion gate's PASS opens with MEASURED. A bare label such as
  `MEASURED` no longer carries a PASS.
- **A verdict file must come from the gate.** Any `.verdict.md` written during a turn, by the main
  session or by a subagent, must carry the same agent and verdict that a gate returned in that turn,
  or the `Stop` hook sends the turn back.
- **Only a PASS promotes a marketing asset.** A CONCERNS verdict now holds the asset until it is fixed
  and gated again.
- **The `Stop` hook says why it blocked:** no verdict block, or the validator's first error. After a
  clean turn that ran gates it prints one line: gates checked and verdicts valid.

### Fixed
- `workforce-doctor` no longer says Stop hooks may not run in print mode. They do; the doctor now
  states what the verdict check covers.

## 2.3.2 — 2026-10-07 — The verdict check sees every gate in the turn

### Fixed
- **The `Stop` hook now checks every gate dispatched in the turn.** Claude Code stores a tool result
  the same way as a user message, so the hook used to start the turn after the last tool result and
  could miss a gate's verdict entirely. It now starts the turn at your last real message.
- **A verdict block must name the agent that returned it.** A block signed by a different agent
  than the one dispatched sends the turn back.
- **A COULD NOT ASSESS verdict written with underscores now counts as blocking** in the overall
  result, the same as the spaced form.
- **`workforce-doctor` counts agents from the installed folders** and does not report a quiet `Stop`
  hook in print mode (`claude -p`) as a fault.

### Removed
- A leftover hook script from 2.2.0 that was no longer wired to anything.

## 2.3.1 — 2026-10-03 — New home at BlackRaptorAI-Labs

### Changed
- The project now lives at BlackRaptorAI-Labs; the old address redirects. Issues and pull requests are open; see CONTRIBUTING.

## 2.3.0 — 2026-10-03 — Findings you can act on; hooks that are tested and can be switched off

### Changed
- **Every verdict's evidence now starts with how it was obtained.** The `evidence` line opens with
  MEASURED (it was run), CITED (a file line or fetched page, quoted), COMPUTED (traced or
  calculated), ESTIMATED or ASSUMED. The verdict schema is now 3.1 and rejects an unlabelled line, so
  the `Stop` hook sends such a verdict back. Nothing else in the verdict block changed.
- **Findings are one claim per row.** Each row lists which sibling entry points were checked
  (create, update, delete and every caller kind), a severity on a defined scale (Critical, High,
  Medium, Low), the smallest fix, and the check that proves it closed. Rows that cannot cite the
  exact line, the failure, the trigger and why existing guards miss it are not written, and a clean
  review with no findings is a valid result.
- **Claims about how a vendor service or framework behaves are cited from its documentation, or
  marked as assumptions.** An assumed claim is capped at Medium and cannot block on its own.
- **Re-reviews mark each earlier finding CLOSED, PARTIAL or OPEN** at the new commit.
- **The enforcement map names the real gates.** `test-auditor` and `schema-reviewer` are listed;
  `qa-test-engineer`, which writes tests, is no longer treated as a gate by the `Stop` hook.

### Added
- **One switch turns every Core hook off:** set `BR_HOOKS=off` before starting Claude Code.
  `BR_VERDICT_HOOK=off` and `BR_CLAIMS_HOOK=off` still turn off one hook each. A hook that is off
  says so in one line.
- **Each hook now has a timeout** (10 seconds at session start and before a write, 45 seconds at the
  end of a turn), and a short `hooks/README.md` explains what fires, when, and what it needs.
- **`workforce-doctor` now checks that `python3` is on your PATH**; without it two of the hooks
  check nothing.

### Fixed
- **The claims-gate instructions no longer mention a prompt hook that was removed in 2.2.0.** The
  rule is carried by the `compliance-claims-gate` skill and each producer's instructions. The skill
  also now states that the marketing write gate trusts any verdict file on disk, so a verdict a
  producer wrote itself is caught only by the end-of-turn check.

## 2.2.1 — 2026-09-09 — A blocked turn no longer names the same gate twice

### Fixed
- **When the Stop hook blocks a turn and the same gate is retried without a valid verdict, its name
  no longer appears twice in the block message.** Each distinct problem is now listed once, in the
  order it was found; a retry that is still invalid no longer reads as two separate failures.

### Changed
- **The `claims-gate` agent's description is shorter.** Same scope and behaviour — it still judges
  every external-facing marketing asset before it ships, blind to the author's reasoning, and never
  edits what it judges.

## 2.2.0 — 2026-09-09 — Onboarding no longer eats your first turn; every description rewritten

### Changed
- **Agent and skill descriptions across the roster were rewritten** to state scope more directly.
  The router matches your request against this description text, not against agent names — if you
  have muscle memory for a specific name, it still works.
- **Onboarding and the verdict-format reminder now fire at session start, not on your first prompt.**
  Both previously ran as a `UserPromptSubmit` hook, which meant the first thing you typed in a fresh
  session got intercepted for setup. They now run once at `SessionStart` instead, so your first turn
  is your first turn.
- **The one-shot claims-gate prompt-reminder hook is removed.** Its job — telling a producer agent
  about the DRAFT/GATED convention — is now carried directly in each producer's own instructions, so
  a separate hook nagging about it on every relevant prompt was redundant and is gone.
- **The shared operating-contract text agents carry was split into two files under the hood**
  (the always-on commitments, and a separate session/preference layer). No visible change to what an
  agent tells you it follows; this is an internal reorganization to keep the always-on part smaller.

## 2.1.0 — 2026-09-06 — The verdict Stop hook closes two gaps found live in testing

### Fixed
- **The Stop hook now finds a council seat's or the claims gate's verdict when it was written to a
  file instead of echoed inline (D-57).** The hook could previously tell a standalone gate dispatch
  from a seat in a council convening only by name, and a seat's `council/<slug>.verdict.md` write
  did not satisfy it — a false block. It now checks, in order: an inline fenced verdict block; a
  council seat's `.verdict.md` file; for `claims-gate` only, a `.verdict.md` beside its `.DRAFT.md`.
  `verdict-schema.json` and `validate_verdict.py` are unchanged — only where the hook looks changed.
- **A directional ordering bug in that same fix, caught live in the first re-test (D-60).** The
  file-lookup branch required the DRAFT write to happen at or after the gate's own dispatch, but the
  real workflow writes the draft BEFORE the gate ever runs, so the branch could never pass. Fixed by
  dropping the ordering constraint on the DRAFT write while keeping it on the verdict file itself.
- **The hook now reads a gate seat's result from its background-task notification, and waits for a
  seat still running instead of treating it as missing (D-65).** Claude Code can dispatch a subagent
  in the background and deliver its result later as a notification; the hook previously saw only the
  dispatch's immediate placeholder result and blocked every backgrounded seat. It now reads the
  notification's completed text, and if a seat has not finished when the turn is about to end, it
  blocks with a plain "gate seat still running; wait for its result" reason instead of a false "no
  verdict found." See `UPDATING-YOUR-WORKFORCE.md` for the plain-language version. Ref:
  `docs/workforce-state.md` D-65. The fixture proving this (`run_fixture_d65.py`) lives in this
  repository's `_eval/` tree, which does not ship; a live empirical re-run against a real council
  convening is still open (tracked in `docs/workforce-state.md`, condition (iii)) and has no
  dossier section yet.

### Added
- **The DRAFT/GATED convention for external-facing marketing copy is now mechanical**, not just
  documented. A PreToolUse hook refuses an ungated `*.md` write in a `.br-assets`-marked directory
  unless the file is a `*.DRAFT.md`, a `*.verdict.md`, or a `*.md` with a validating `*.verdict.md`
  sibling; the existing Stop hook additionally blocks a turn that wrote a `*.DRAFT.md` in a marked
  directory and never dispatched `claims-gate` afterward. Both are inert outside a marked directory.
  Two enforcement-liveness fixtures prove it (block ungated, permit gated, inert unmarked). New kill
  switch: `BR_CLAIMS_HOOK=off`. See `UPDATING-YOUR-WORKFORCE.md`.

### Measured, not fixed
- Two isolated malformed verdict-block emissions surfaced live during Phase 2 testing, in agents
  shipped by other packs: `compliance-cert` (hardware pack, D-53) and `ethics-governance` (council
  pack, D-54). Both are single JSON-syntax defects in the model's own output — a missing array
  bracket and a blank `standards[]` entry — not hook or schema bugs. Tracked as measured,
  self-measured contract-compliance rates internal to this test programme, not an independent or
  audited figure: 32/33 verdict blocks schema-valid and 17/18, not treated as shipped fixes. The raw
  `runs.jsonl` records live in this repository's `_eval/` tree, which does not ship; the figures are
  reproduced in `docs/TEST-BATTERY-DOSSIER.md` §6(c) result (32/33) and §6(d) result (17/18).

### Build-process notes (not shipped)
- **D-71: a metered test run breached the foreground-only rule a third time and was killed mid-run
  by the session's own background-task timeout, losing uncommitted records.** Not a product defect —
  the loop runner (`_eval/loop/br-build-loop.sh`) and every metered-run script in this repository's
  `_eval/baseline/` tree now print "FOREGROUND ONLY" as their first line and write a `.heartbeat`
  file every 30s while running; the runner also exports `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` as
  a safety net so a breach does not lose records again (not a licence — the foreground rule still
  stands). None of this ships; it governs how this release's own tests are run. Ref:
  `docs/workforce-state.md` D-71.
- **D-72: the string-gate test tool had the same class of blind spot as D-65, in its own code
  rather than the shipped hook.** `run_string_gate.py` (also `_eval/baseline/`, not shipped) read
  only a dispatch's final result text for the verdict block; a run whose gate seat completed in the
  background left the real verdict only in the task notification, and the tool reported `verdict:
  null` even though the dispatch had genuinely finished. Fixed the same way as D-65: read the
  notification summary first, falling back to the final result text. Ref: `docs/workforce-state.md`
  D-72.

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
- **Corrected: the verdict-hook kill switch.** The upgrade guide said the hook "prints one line to
  stderr when disabled, so you can always tell whether it is on". Measured behaviour: interactive
  sessions show that line, `claude -p` does not surface hook stderr. On that path, check the
  `BR_VERDICT_HOOK` variable instead.
- **Corrected: hand-typed roster counts removed from the pack manifests.** A manifest described the
  Core pack as "seven cross-cutting agents". Counts now come from the built tree only, and
  `verify.sh [MAN]` fails the build if one reappears in a manifest.

## 2.0.0 — 2026-09-02 — One verdict contract, live enforcement

**BREAKING: the gate verdict block changed shape.** `verdict-schema.json` moves to v3 and any
existing Change Record carrying a v2 block will fail validation until its blocks are re-emitted.

- `confidence` is an **integer 0-10**, replacing `high|medium|low`. A threshold can be written
  against a number; it could not be written against a word.
- `standards[]` is **new and required**. Each entry carries the designation, edition, clause, how
  the text was reached, and the date it was verified at the issuing body — or the single literal
  `"none: practice applied: <x>"`. The specification asked for a Standards line for a year and the
  schema had no field for it, so nothing enforced it.
- **`N/A` is removed** from the verdict vocabulary. A gate that does not apply now emits no block;
  the Change Record row carries the N/A and its reason.
- `evidence` is a string (it was an array). The validator names the v2 shape explicitly rather than
  failing on a bare type error.

**NEW: the validator now runs on the live path.** A `Stop` hook ships in Core: when a turn dispatched
a gate agent, the turn does not end until that gate's verdict block validates. Previously
`validate_verdict.py` ran only in a CI template a user had to install into their own repository, so
on a marketplace install nothing enforced the contract at all. Kill switch: set `BR_VERDICT_HOOK=off`
to disable it for a session — it prints one line to stderr when disabled, so it is never silently
off. It fails OPEN on its own errors and never blocks a turn twice.

- `validate_verdict.py --self-test` runs a 10-fixture suite covering each failure mode.
- `claims-gate` no longer carries the retired-claims list in its body; it reads §4b of the Marketing
  Intelligence Core, which now has a real schema (claim, why retired, proof standard, date, owner).
- `compliance-claims-gate`, `gate-verdict-format` and the `change-record` template updated to v3.
- The three cross-pack analysts now guard every Marketing-pack path: with the pack installed they
  read it, without it they proceed from `BUSINESS-CONTEXT.md` and label the method ASSUMED. On a
  Core-only install those paths previously dangled.

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
