---
description: Run the applicable gate agents on the current diff and produce a Change-Record-ready verdict block
---

Run gate reviews for the current branch's changes.

1. Get the diff: `git diff main...HEAD` plus the list of changed files
   (`git diff main...HEAD --name-only`).
2. Map changed files to gates (see docs/gate-enforcement-map.md):
   - every change → code-reviewer
   - any test file added or changed → test-auditor
   - auth/RBAC/tenant/remote-access/firmware paths → security-architect
   - personal data, LLM data-flow, cross-border → privacy-counsel
   - audit-trail, access-control, retention, change-mgmt → compliance-officer
   - regulated data of record → domain-compliance
   - your schema or migration paths → schema-reviewer
   - automated/AI-driven/irreversible consequential actions (remote commands,
     auto-remediation, bulk operations) → operational-readiness
3. Invoke each applicable gate agent as a subagent with the diff and ask for
   its Change-Record-ready verdict (PASS / CONCERNS / FAIL with analysis).
   Run independent gates in parallel. Dispatch gates only, never a producer:
   the agent that authored the work cannot judge it.
4. Output:
   - The risk tier of this change (Tier 1/2/3) with the deciding paths.
   - A gate table matching §2 of the Change Record template, verdicts filled,
     "My decision" column left blank for the human.
   - Each agent's full analysis in a §3-ready block.
   - If Tier 2/3: remind me to create the CR file (use the change-record skill)
     and, if Tier 3, that {{SECOND_APPROVER}}'s approval is required.

Do not fill in human decisions or signatures. If no gate beyond
code-reviewer (and test-auditor, for a test change) applies, say the change
is Tier 1 and no CR file is needed, IN PROSE — emit no fenced ```verdict
block of your own on this path. The v3 verdict schema has no "no gate ran"
shape, so a block improvised here is invalid by construction and will be
rejected; the Tier-1/no-CR statement is the complete output for this case.

$ARGUMENTS
