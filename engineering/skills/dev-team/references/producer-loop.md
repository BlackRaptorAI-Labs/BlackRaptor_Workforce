# Producer loop: build errors, retries and stop rules

For any producer turning a plan into working code (backend, frontend, infrastructure, edge). The
`dev-team` skill orchestrates; this is how each producer works inside its slice.

## Units of work
Break the slice into units that each end in a state someone can verify: a test passes, a command
exits 0, a page renders. Do not start the next unit until the current one is verified.

## When the build or a test fails
Keep a short table as you go, one row per error:

| error (exact text) | cause (what you found, with `path:line`) | fix (the smallest change) | result |
|---|---|---|---|

- Fix the smallest thing that explains the error first. One change per attempt.
- **Stop and report** (do not keep trying) when any of these is true:
  - three attempts on the same error have failed;
  - a fix introduces new errors;
  - the fix needs an architecture change or a change outside your slice.
- Never silence a lint or type error (a suppression comment, a rule disabled) without the human's
  approval, named in the report.

## Retries and flaky results
- Two retries on a unit, then stop and replan the unit instead of trying a third way.
- A suspected flaky test gets one fresh build. Never re-run a CI job until it goes green; a flake is a
  defect to report, not a result.

## Budget
Stop starting new subagents or new units at 70 percent of the turn or task budget, and use the rest to
finish, verify and report.

Report the error table with the result: what is fixed, what is still failing, and why you stopped.
