## 2026-08-13 — Renamed & consolidated
- **Plugin id:** `blackraptor-dev-team` → **`blackraptor-engineering`**. Dependency `blackraptor-bridge` → **`blackraptor-core`**.
- **Repo:** moved from `BlackRaptorAI/BlackRaptor_Agents` (`development/`) into the consolidated **`BlackRaptorAI/blackraptor`** (`engineering/`). Product line: **BlackRaptor Workforce**. Layout normalized (skills at `./skills/`, commands at `./commands/`).
- Agents, skills, and gates unchanged in substance; identifiers/display/paths only.

# Changelog

All notable changes to the BlackRaptor Agents development team are recorded here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [1.4.5] — 2026-08-20

### Added
- Repo-native first-run experience (R10/R14): a bare repo triggers the welcome flow with the engineering technical question set (`dev-team/references/context-questions.md`) — the shared core block writes repo-root `BUSINESS-CONTEXT.md`, the technical set writes `CLAUDE.md`; a populated repo gets a "review and fill gaps" offer instead. Seven-dimension preference wire-up (R13) via the shared Core contract. Engineering stays project-scoped.

## [1.4.4] — 2026-08-19

### Changed
- `dev-team` gains a context read-path note: engineering keeps the project's **existing** context conventions (no new company-context file), and the Core `prompt-brief` intake now runs the Rung-0 context precheck before context-dependent work (resolve the project's context per the resolution order; `context-onboarding` can capture it if the change needs context the project does not yet record) (R3, engineering read-path per spec §3.1).

## [1.4.3] — 2026-08-18

### Fixed
- `workforce-doctor` no longer certifies pack presence/absence from a stale Cowork snapshot. A Cowork cloud session copies the account plugin cache to `.claude/plugins/synced/` once at session start and never re-syncs, so a run could report a pack PRESENT that was uninstalled after the session began. Adds **check 0 (snapshot freshness)**: in a Cowork session the doctor records and reports the snapshot timestamp and returns **STALE SNAPSHOT — CANNOT CERTIFY** when the snapshot predates the pack add/remove under test. Adds a check-1 caveat that an empty `claude plugin list` under Cowork is inert by design, not an anomaly. No-op in local CLI sessions.

## [1.4.2] — 2026-08-17

### Fixed
- Ships `workforce-doctor` to existing installs (prior release omitted the version bump). The skill was already committed to the pack, but the plugin version wasn’t bumped, so `claude plugin update` treated installs as current and never delivered it — this patch re-releases with a bumped version. Tracked in BlackRaptorAI/blackraptor#1.

## [1.4.1] — 2026-07-23

### Fixed
- **`completion-auditor` now pins `model: opus`** — it was missing a `model:` field
  and silently fell back to the session default. It's a deep-judgment gate; opus is
  the correct tier (matches golden and the other gate agents).

## [1.4.0] — 2026-07-22

Cross-cutting agents moved to a shared bridge; roster 25 → 23.

### Changed
- **`evidence-auditor` and `product-manager` moved out** to the new
  `blackraptor-bridge` plugin (auto-installed as a dependency — you still get them,
  namespaced `blackraptor-bridge:…`). They're cross-cutting: evidence-auditor is
  central to the council and the HEAVY-tier gate for engineering's load-bearing
  claims; `product-manager` (now the merged product-strategy + delivery role) spans
  market demand and the build.
- **`research-integrity` skill moved** to the bridge too (it's evidence-auditor's
  paired methodology). Dev-team skills 8 → 7.
- `plugin.json` now declares `"dependencies": ["blackraptor-bridge"]`.

## [1.3.0] — 2026-07-22

Public now mirrors the golden roster more closely: personas out, model tiering in.

### Changed
- **Removed the persona/backstory blocks** ("**Who you are.**" voice paragraphs)
  from all 24 charters. The charters keep their role, reasoning method, mission,
  and boundaries — just not the first-person backstory. Behavior is defined by the
  instructions, not a character.
- **Model tiering now matches the source deployment** — `dev-orchestrator` and
  `principal-architect` move to the top tier (the strongest model available), reserved for
  the two roles where a mistake is costliest and call volume is lowest. Deep-judgment
  gates stay `opus`; everyday build stays `sonnet`. Each opus charter carries the
  tier-appropriate Output-quality discipline line (checklist backstop). README
  "Model tiering" section updated (was "tops out at `opus`"); fall back to the
  strongest model you have where the top tier isn't available.

## [1.2.0] — 2026-07-22

### Added — agents
- **`completion-auditor`** — an independent verifier that audits claimed-complete
  work **before** it's reported as done (especially multi-step git/PR/merge/deploy
  work). Read/verify-only (Bash, Read, Grep, Glob); it doesn't trust narration —
  it re-checks ground truth (remote refs, CI state, `origin/main` log, cwd/worktree
  hygiene, pipe-masked exit codes, shell word-splitting, governance ordering) and
  returns PASS or a list of unverified/failed items to fix first. The behavioral
  analog of the Excellence Pass "verify by an independent method." Roster 24 → 25.

## [1.1.0] — 2026-07-21

The research-integrity release + Claude Code plugin marketplace. Roster 23 → 24.

### Added — agents
- **`evidence-auditor`** — the independent adversarial gate for research, analysis,
  and evidence-based reporting (the research analog of `red-team-reviewer` /
  `completion-auditor`). Read/analysis-only; grades sources (reliability ×
  credibility), collapses citation chains to **independent origins** (effective-N /
  anti-woozle), separates **root-veracity** from root-reachability, checks
  qualifier drift, and enforces the release gate — PASS / CONCERNS / FAIL verdicts.

### Added — skills
- **`research-integrity`** — a three-mode research methodology engine (A evidence
  synthesis · B direct-source aggregation · C original primary research) with an
  intake triage, mode-selector, separate source-reliability × evidence-certainty
  grading, citation-independence + consilience, root-to-mechanism verification, a
  release gate, and analytic-judgment output. Ships with fillable artifact
  templates (`templates.md`) and the full design spec (`docs/research-integrity-spec.md`).
- **`excellence-pass`** — the five behaviors that separate top-tier output from
  merely-correct output, run as a final pass before delivery; each charter carries
  a tier-appropriate pointer to it.

### Added — distribution
- **Claude Code plugin marketplace.** Install the suite via
  `/plugin marketplace add BlackRaptorAI/BlackRaptor_Agents` → plugins
  `blackraptor-dev-team` and `blackraptor-council`. Manifests:
  `.claude-plugin/marketplace.json` (repo root) + per-team `plugin.json`.

### Changed
- Dev roster **20 → 24** (Legal & IP pod: `legal-docs-writer` + `ip-counsel`;
  then `evidence-auditor`). README count + install docs updated.

## [0.3.0] — 2026-07-16

Roster grows to 20 with two roles extracted from the same production platform
the kit came from, and the pods are rebalanced.

### Added — agents
- **`edge-agent-engineer`** — the on-device/customer-premises engineering tier:
  device adapters, offline queueing, remote access, self-healing. Encodes the
  edge disciplines cloud personas don't carry: resource budgets on constrained
  hardware, fleet version skew (N-1/N-2 tolerance, canary channels), and clock
  integrity when device timestamps feed regulated data. Delete it if your
  platform has no edge tier.
- **`operational-readiness`** — operational fitness + meaningful human control.
  Two lenses: does the change serve the operator's real workflow (consulted at
  spec, sign-off at delivery), and does every consequential automated or
  AI-driven action have a designed, audited, fail-safe human checkpoint
  (**blocking at review**). This is the kit's sixth blocking gate.

### Changed
- **Roster regrouped from 8 pods to 7.** The "Security assurance & docs"
  catch-all is dissolved: `red-team-reviewer` joins Quality & Assurance,
  `technical-writer` joins Communication & GTM. New agents slot into
  Engineering and Operations.
- Blocking-gate count is now **six** (security, privacy, compliance, domain,
  schema, human oversight). `docs/gate-enforcement-map.md` gains the HITL row
  (checklist-only — it's a behavioral property no path expresses).
- `/gate-review` routes consequential automated actions to
  `operational-readiness`; `/new-feature` consults it at spec time.

## [0.2.0] — 2026-07-03

This release grew the roster and hardened the agent *craft* — most of it
directly inspired by ideas from the wider Claude Code community. See the
**Credits & thanks** section below; these improvements exist because other
people published their work openly, and we're grateful for it.

### Added — agents
- **`red-team-reviewer`** — an adversarial, pre-penetration-test review agent:
  threat modeling, OWASP / abuse-case review, and *proof-of-vulnerability*
  tests written against your own code in a controlled test environment. It is
  read-only by design and explicitly **complements, never replaces, an
  independent human penetration test.** *(Role inspired by the
  `penetration-tester` / `security-auditor` roles common in public collections —
  see Credits.)*
- **`security-operations`** — runtime/operational security (SIEM, WAF, detection
  engineering, security incident response, secrets hygiene), distinct from
  build-time `security-architect`.
- **`technical-writer`** — owns as-built spec/code drift, API reference, and
  documentation quality. *(Identified as a roster gap by benchmarking against
  public role taxonomies — see Credits.)*

### Added — skills & tooling
- Reference **skills** extracted so agent prompts stay lean and multiple agents
  share one source: `stride-review`, `expand-contract-migration`,
  `owasp-llm-checklist`, `gate-verdict-format`. *(Progressive-disclosure-skills
  pattern — see Credits.)*
- **`agent-evals/`** — a proactive agent-quality convention (run a small fixed
  eval set when you change an agent definition) that pairs with the reactive
  `AGENT-RETROS.md` loop: evals prevent regressions, retros correct misses.
  *(Inspired by public agent-evaluation frameworks — see Credits.)*
- **`/red-team`** slash command to run the adversarial review on demand.

### Changed
- **Model-tiering** is now a documented, deliberate policy (deep-judgment agents
  on the strongest model, everyday builders on a mid tier, low-stakes work on a
  fast tier) rather than ad hoc. *(Multi-tier model strategy — see Credits.)*
- **Least-privilege tool permissions** audited across the roster: read-only
  reviewers carry only read/analysis tools; only builders get write/exec.
  `red-team-reviewer` was tightened to read-only after this audit caught it
  carrying shell access it did not need. *(Role-based tool-restriction
  convention — see Credits.)*

### Security
- **Tier-3 guard hook hardened.** Path matching is now case-insensitive (so a
  case variant like `.GitHub/` can't slip past on macOS/Windows) and resolves
  symlinks with `realpath` (so a symlink pointing at a protected file is
  caught). The docstring now states plainly that this hook is in-session
  accident-prevention and that the *enforcement of record* is server-side
  (branch protection + CODEOWNERS + the change-record-required CI check).
  Verified with a path-guard test harness.

### Notes
- Nothing here changes the governance core (Change Records, tier gates,
  fail-closed enforcement) — the differentiator of this kit. The additions are
  craft and coverage improvements layered on top.

---

## Credits & thanks

The 0.2.0 improvements came from **benchmarking this kit against the excellent
public Claude Code subagent collections**. Each idea below is credited to where
we found it, with a link to the source and our sincere thanks to the maintainers
and contributors — open-sourcing your work is what made these improvements
possible.

| Improvement in this release | Idea credited to | Source |
|---|---|---|
| Deliberate multi-tier model strategy (deep/everyday/fast) | **wshobson** and contributors — *agents* marketplace | https://github.com/wshobson/agents |
| Proactive agent-quality evaluation (the `agent-evals/` convention) | **wshobson** and contributors — the *PluginEval* quality framework | https://github.com/wshobson/agents |
| Progressive-disclosure **skills** (lean prompts, load knowledge on demand) | **wshobson** and contributors | https://github.com/wshobson/agents |
| Role-based **least-privilege tool restriction** (read-only reviewers, etc.) | **VoltAgent** and contributors — *awesome-claude-code-subagents* | https://github.com/VoltAgent/awesome-claude-code-subagents |
| Role taxonomy that surfaced our gaps (**technical-writer**, and the security roles behind **red-team-reviewer**) | **VoltAgent**, **0xfurai**, and the broader community catalogs | https://github.com/VoltAgent/awesome-claude-code-subagents · https://github.com/0xfurai/claude-code-subagents |
| Community index that made these collections discoverable | **hesreallyhim** — *awesome-claude-code* | https://github.com/hesreallyhim/awesome-claude-code |

**Thank you** to the maintainers and contributors of these projects. We adopted
your *ideas and conventions*, re-expressed for this governance-first kit; the
governance layer (Change Records, tier gates, enforcement) is our own
contribution back to the commons. If we've mis-credited an idea or missed a
source, please open an issue — we want attribution to be right.

## [0.1.0] — 2026-07-02

Initial public release: 16-agent governed team, Tier-3 path-guard hook,
`change-record-required` CI check, sparse CODEOWNERS two-person rule, the Change
Record system, and the agent-retro feedback loop. Extracted from production use.
