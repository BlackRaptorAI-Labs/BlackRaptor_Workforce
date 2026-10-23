---
description: Run the applicable gate agents on the current diff and produce a Change-Record-ready verdict block
---

Run gate reviews for the current branch's changes.

0. **Check ladder first (the same rungs and rules as `dev-team` wave 2b).** Before any other
   subagent, dispatch `completion-auditor` to run the check ladder on this branch, with the exact line
   `MODE: ladder-only (no verdict)` as the first line of its prompt (the Stop hook then owes no verdict
   from it and ignores any it returns), in order, stopping
   at the first red rung: lint (`{{LINT_CMD}}`), typecheck (`{{TYPECHECK_CMD}}`), the tests for the
   changed files (`{{TEST_CMD}}` scoped to the diff where the runner supports it, else "not
   scopable"), the full suite (`{{TEST_CMD}}`). It returns the ladder table defined in
   `${CLAUDE_PLUGIN_ROOT}/skills/dev-team/references/facts-pack.md`: one MEASURED row per rung
   (command, exit status, output path); an unset command is "not configured", never red. **While a
   configured rung is red, dispatch no gate:** stop, show completion-auditor's table, and name the
   red rung and its command; write no verdict block of your own for the ladder. Otherwise pass the
   table to every gate you dispatch (`test-auditor` cites it as CITED: the output path and the backticked command).
   **Then push the branch** (`git push -u origin HEAD`; never `--force`, never the default branch) before any
   `test-auditor` or `completion-auditor` dispatch: CI is the judge of whether the tests pass (D-252), and it
   runs on the pushed commit. Commit first if the tree has changes. If the push fails, say so and go on: the
   Stop hook will report those gates INCOMPLETE ("commit and push; CI decides"), not PASS.
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
   - infrastructure-as-code, CI/CD workflow or deploy-pipeline paths → infra-reviewer
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
   - The CI state for each test-auditor or completion-auditor verdict, as the Stop hook reported it: passed,
     waiting (with the run URL), or failed (with the job URL). A waiting gate is not passed; run this command
     again in a later turn and the hook re-reads CI. Never poll in a loop.

Do not fill in human decisions or signatures, and never merge: a person merges once CI and the gates pass. If no gate beyond
code-reviewer (and test-auditor, for a test change) applies, say the change
is Tier 1 and no CR file is needed, IN PROSE — emit no fenced ```verdict
block of your own on this path. The v3 verdict schema has no "no gate ran"
shape, so a block improvised here is invalid by construction and will be
rejected; the Tier-1/no-CR statement is the complete output for this case.

$ARGUMENTS
