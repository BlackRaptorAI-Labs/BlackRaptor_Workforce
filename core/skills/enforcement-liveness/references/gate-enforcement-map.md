# Gate enforcement map (step 3.5) — every gate's recorded enforcement category

> **Sanctioned Rule-3 registry (SPEC §9.2).** This is the one Core reference whose *subject* is the
> gate roster itself, so it names gate-agent slugs by necessity — a capability-vocabulary rewrite
> would destroy the map. It is the explicit exception the audit named ("mark the registry as the
> sanctioned exception"); `verify.sh`'s Rule-3 grep skips this file. The names here are a catalogue,
> not a dispatch instruction, and confer no cross-pack dependency.

Product-agnostic. For each GATE agent, record HOW it is actually enforced — never overclaim. Three
honest categories (from the `gate-enforcement-map` taxonomy):

- **Mechanical** — a required CI check blocks the merge. Reliable.
- **Partial** — known paths are covered mechanically; the concern is broader than those paths (the
  Change Record covers the rest).
- **Checklist-only** — a data-flow or behavioral property no path expresses; only the discipline
  step / Change Record covers it.

The category **depends on the install's CI and branch protection**; the column below is the gate's *nature*
and the **recorded ruling where one has been made**. Keep it in sync with the actual paths — do not
claim Mechanical if the paths do not cover the concern.

| Gate agent | category (nature / ruling) | mechanism | gap covered by the discipline step | model | effort |
|---|---|---|---|---|---|
| `claims-gate` | **Checklist-only** — *ruled order-8 (8 Aug); mechanism updated A1 (13 Aug)* | **Guaranteed** = the mandatory agent-dispatch step in the `marketing-campaign` skill. **Best-effort** for ad-hoc single assets = an always-on rule on LOADED surfaces (the `compliance-claims-gate` skill + producer descriptions; no hook carries it — the core `SessionStart` hook does onboarding only, and the `UserPromptSubmit` claims hook was removed in 2.2.0) — NOT the plugin-root `CLAUDE.md` carrier, which does not load on a marketplace install (measured, SPEC §2 P11). Known limit: single-asset isolated dispatch is not guaranteed (the model tends to self-review). Marketing assets have no stable CI paths → not Mechanical. | every external claim's proof | `opus` | `high` |
| `code-reviewer` | Mechanical (nature) | required CI review check on PRs | style/architecture judgment beyond CI | `opus` | `high` |
| `test-auditor` | Checklist-only (quality) | — (read-only; `completion-auditor` supplies the MEASURED runs) | test honesty (tautological/over-mocked) | `opus` | `high` |
| `schema-reviewer` | Partial (schema) | the Tier-3 hook on migration paths, and the owner's approval | migration safety (expand/contract, lock impact, rollback) | `opus` | `high` |
| `infra-reviewer` | Partial (infrastructure) | the Tier-3 hook on infrastructure and `.github/` paths, and the owner's approval | rollback path, blast radius, least privilege, required checks still gating the deploying branch | `opus` | `high` |
| `security-architect` | Partial (nature) | the Tier-3 hook on auth/remote/tenant paths, and the owner's approval | new attack surfaces outside listed paths | `opus` | `high` |
| `privacy-counsel` | Partial (nature) | the owner's approval on data-collection changes | PII-to-LLM / cross-border data-flow | `opus` | `high` |
| `domain-compliance` | Checklist-only | — | regulated-output eligibility judgments | `opus` | `high` |
| `compliance-officer` | Checklist-only | — | control continuity (behavioral) | `opus` | `high` |
| `operational-readiness` | Checklist-only | — | HITL on consequential automated actions | `opus` | `high` |
| `red-team-reviewer` | Checklist-only | — | adversarial abuse-cases (no path) | `opus` | `high` |
| `completion-auditor` | Checklist-only | invoked as the closing step | ground-truth re-check of "done" | `opus` | `high` |
| `ux-designer` | Checklist-only | — | design-system + a11y review | `opus` | `high` |
| `ethics-governance` | Checklist-only | standing to BLOCK | stakeholder/honesty/data-use judgment | `opus` | `high` |
| `evidence-auditor` | Checklist-only | — | citation-chain / root-veracity review | `opus` | `high` |
| `compliance-cert` | Checklist-only | — | regulatory/cert applicability (opus gate; 5.8 disposition ratified opus 2026-08-12) | `opus` | `high` |
| `hw-design-reviewer` | Checklist-only | — | adversarial design review before a board spin | `opus` | `high` |

**Model and effort:** the last two columns mirror each gate's agent file (`governance/check_model_tiers.py` fails the build if they drift): every gate is `opus` with `effort: high`.

**Rule:** a gate whose category is Checklist-only must say so — an unenforced "Mechanical" claim is
the exact overclaim `enforcement-liveness` exists to catch. When an install adds CI paths
that genuinely cover a gate's concern, upgrade its row (Checklist-only → Partial → Mechanical) with
the paths named.
