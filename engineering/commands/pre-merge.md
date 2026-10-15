---
description: Pre-merge check — code review, Change Record completeness, slicing discipline, CI readiness
---

Run the pre-merge sequence on the current branch.

0. **Check ladder first (the same rungs and rules as `dev-team` wave 2b).** Before any other
   subagent, dispatch `completion-auditor` to run the check ladder on this branch, in order, stopping
   at the first red rung: lint (`{{LINT_CMD}}`), typecheck (`{{TYPECHECK_CMD}}`), the tests for the
   changed files (`{{TEST_CMD}}` scoped to the diff where the runner supports it, else "not
   scopable"), the full suite (`{{TEST_CMD}}`). It returns the ladder table defined in
   `${CLAUDE_PLUGIN_ROOT}/skills/dev-team/references/facts-pack.md`: one MEASURED row per rung
   (command, exit status, output path); an unset command is "not configured", never red. **While a
   configured rung is red, dispatch no gate:** stop, show completion-auditor's table, and name the
   red rung and its command; write no verdict block of your own for the ladder. Otherwise pass the
   table to every gate you dispatch (`test-auditor` takes it as its MEASURED input).
1. Use the code-reviewer subagent on `git diff main...HEAD`: conventional
   commits, PR hygiene, conventions (Zod, shared constants, AuditEvent writes,
   no secrets/PII in code or logs), slicing discipline (deployable on its own,
   flags on user-visible surfaces, no destructive migration with dependent
   code), and gate/CR completeness.
2. Verify mechanically:
   - Tests/lint/typecheck pass: quote the step 0 ladder table (green rungs, or "not configured").
   - If any gated path is touched: a docs/change-records/CR-*.md exists in this
     branch, every gate row is decided or explained-N/A, §5 filled where a
     verdict was overruled, signature block signed.
   - If Tier 3: flag that {{SECOND_APPROVER}}'s approval will be required on the PR.
3. Report: **READY TO OPEN PR** or a blocking list with file/line specifics.
   If gate reviews are missing, tell me to run /gate-review first.

Do not open the PR or merge anything yourself.

$ARGUMENTS
