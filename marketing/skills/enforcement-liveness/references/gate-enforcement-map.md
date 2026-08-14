# Gate enforcement map (step 3.5) — every gate's recorded enforcement category

> **Sanctioned Rule-3 registry (SPEC §9.2).** This is the one Core reference whose *subject* is the
> gate roster itself, so it names gate-agent slugs by necessity — a capability-vocabulary rewrite
> would destroy the map. It is the explicit exception the audit named ("mark the registry as the
> sanctioned exception"); `verify.sh`'s Rule-3 grep skips this file. The names here are a catalogue,
> not a dispatch instruction, and confer no cross-pack dependency.

Product-agnostic. For each GATE agent, record HOW it is actually enforced — never overclaim. Three
honest categories (from the `gate-enforcement-map` taxonomy):

- **Mechanical** — CODEOWNERS or a required CI check blocks the merge. Reliable.
- **Partial** — known paths are covered mechanically; the concern is broader than those paths (the
  Change Record covers the rest).
- **Checklist-only** — a data-flow or behavioral property no path expresses; only the discipline
  step / Change Record covers it.

The category **depends on the install's CODEOWNERS + CI**; the column below is the gate's *nature*
and the **recorded ruling where one has been made**. Keep it in sync with the actual paths — do not
claim Mechanical if the paths do not cover the concern.

| Gate agent | category (nature / ruling) | mechanism | gap covered by the discipline step |
|---|---|---|---|
| `claims-gate` | **Checklist-only** — *ruled order-8 (8 Aug); mechanism updated A1 (13 Aug)* | **Guaranteed** = the mandatory agent-dispatch step in the `marketing-campaign` skill. **Best-effort** for ad-hoc single assets = an always-on rule on LOADED surfaces (a plugin `UserPromptSubmit` hook + the `compliance-claims-gate` skill + producer descriptions) — NOT the plugin-root `CLAUDE.md` carrier, which does not load on a marketplace install (measured, SPEC §2 P11). Measured limit: single-asset isolated dispatch is not guaranteed (the model tends to self-review). Marketing assets have no stable CODEOWNERS/CI paths → not Mechanical. | every external claim's proof |
| `code-reviewer` | Mechanical (nature) | required CI review check on PRs | style/architecture judgment beyond CI |
| `qa-test-engineer` | Mechanical + Checklist | required coverage CI checks | test honesty (tautological/over-mocked) |
| `security-architect` | Partial (nature) | CODEOWNERS on auth/remote/tenant paths | new attack surfaces outside listed paths |
| `privacy-counsel` | Partial (nature) | CODEOWNERS on data-collection paths | PII-to-LLM / cross-border data-flow |
| `domain-compliance` | Checklist-only | — | regulated-output eligibility judgments |
| `compliance-officer` | Checklist-only | — | control continuity (behavioral) |
| `operational-readiness` | Checklist-only | — | HITL on consequential automated actions |
| `red-team-reviewer` | Checklist-only | — | adversarial abuse-cases (no path) |
| `completion-auditor` | Checklist-only | invoked as the closing step | ground-truth re-check of "done" |
| `ux-designer` | Checklist-only | — | design-system + a11y review |
| `ethics-governance` | Checklist-only | standing to BLOCK | stakeholder/honesty/data-use judgment |
| `evidence-auditor` | Checklist-only | — | citation-chain / root-veracity review |
| `compliance-cert` | Checklist-only | — | regulatory/cert applicability (opus gate; 5.8 disposition ratified opus 2026-08-12) |
| `hw-design-reviewer` | Checklist-only | — | adversarial design review before a board spin |

**Rule:** a gate whose category is Checklist-only must say so — an unenforced "Mechanical" claim is
the exact overclaim `enforcement-liveness` exists to catch. When an install adds CODEOWNERS/CI paths
that genuinely cover a gate's concern, upgrade its row (Checklist-only → Partial → Mechanical) with
the paths named.
