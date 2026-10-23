# Gate enforcement map (template)

For each review gate, record HOW it is enforced. Three honest categories:

- **Mechanical** — a required CI check blocks the merge. Reliable.
- **Partial** — known paths are covered mechanically, but the concern is
  broader than those paths; the Change Record covers the rest.
- **Checklist-only** — a data-flow or behavioral property no path expresses
  (e.g. "does this send PII to the LLM"); only the Change Record covers it.

| Gate | Agent | Enforcement | Mechanism / paths | Gap covered by CR |
|---|---|---|---|---|
| Security — auth/authz | security-architect | Partial | {{AUTH_PATHS}} in the Tier-3 hook + the owner's approval | New auth surfaces outside listed paths |
| Schema | schema-reviewer (data-engineer authors) | Partial | {{SCHEMA_PATH}} in the Tier-3 hook + the owner's approval | Migration safety (expand/contract, lock impact, rollback) |
| CI/CD + enforcement config | infra-reviewer (devops-sre authors) | Partial | `.github/`, `.claude/hooks/` in the Tier-3 hook + `change-record-required` when you make it a required check + the owner's approval | Rollback path, blast radius, least privilege, required checks still gating the deploying branch |
| Privacy — PII at rest | privacy-counsel | Partial | {{PII_PATHS}} | New PII fields elsewhere |
| Privacy — PII to LLM / cross-border | privacy-counsel | Checklist-only | — | Data-flow property |
| Domain ({{REGULATED_DOMAIN}}) | domain-compliance | Checklist-only until the module exists | (future {{DOMAIN_PATHS}}) | Eligibility/behavioral judgments |
| Compliance — control continuity | compliance-officer | Checklist-only | — | Behavior, not paths |
| Human oversight — HITL on consequential automated actions | operational-readiness | Checklist-only | — | Behavioral property: designed human checkpoint, fail-safe default, audited override |
| Quality — tests/coverage | qa-test-engineer | Mechanical | required CI checks | Test honesty (CR + review) |

Two structural limits that make the Change Record mandatory, not optional:
Branch protection sees checks and approvals, not behavior. The owner approves every pull request, while write access stays with the owner and one agent account (the branch-protection checklist says how); required checks and the owner's approval gate the merge.
Keep this map in sync with the hook and the CI
GATED list whenever any of them changes.
