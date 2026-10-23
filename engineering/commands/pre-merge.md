---
description: Pre-merge check — code review, Change Record completeness, slicing discipline, CI readiness
---

Run the pre-merge sequence on the current branch.

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
   - The CI state for each test-auditor or completion-auditor verdict, as the Stop hook reported it: passed,
     waiting (with the run URL), or failed (with the job URL). A waiting gate is not passed; run this command
     again in a later turn and the hook re-reads CI. Never poll in a loop.
   - CI for the pushed commit: workforce-proof's `head-suite` and `base-suite` must both have passed; if
     either is waiting or failed, the report is not READY.
3. Report: **READY TO OPEN PR** or a blocking list with file/line specifics.
   If gate reviews are missing, tell me to run /gate-review first.

Do not open the PR or merge anything yourself.

$ARGUMENTS
