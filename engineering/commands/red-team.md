---
description: Run an adversarial pre-pentest review on a target surface — threat model, OWASP/abuse-case review, proof-of-vulnerability tests, readiness report
---

Run a red-team review of: $ARGUMENTS
(If no target given, ask me to scope one — e.g. "auth", "sessions", "the whole platform pre-launch".)

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

Use the red-team-reviewer subagent. It must:

1. Threat-model the target: enumerate trust boundaries and, per boundary, attacker goals (forge/replay creds, tenant escape, cross-account resource access, data/secret exfiltration, privilege escalation, injection incl. prompt injection, remote-execution abuse).
2. Enumerate abuse cases and review for vulnerability classes (OWASP web + LLM Top 10, authz bypass, IDOR/tenant-scoping, injection, SSRF, weak crypto, secrets exposure, missing rate limits). Cite file:line for every finding.
3. For credible findings, specify a failing proof-of-vulnerability test against your own code in the test environment (never against live/production or any third party). Do not write the fix.

   Then, for each specified proof test: dispatch the qa-test-engineer subagent to write it, and then the completion-auditor subagent to run it and report the MEASURED result (red as expected, or not). red-team-reviewer stays read-only and never writes or runs the test itself.
4. Produce a ranked findings list (P0–P3) with evidence + proof-test specs, and a pentest-readiness report with a coverage map.

Hard limits (enforced): defensive review of YOUR code only; no weaponized exploits or attack tooling; no live/production or third-party targets; this pass COMPLEMENTS, never replaces, an independent human penetration test — say so in the report.

Stop and show me the ranked findings + readiness report. I decide what to file and fix (through the normal governed workflow) and when to engage the human pentest firm.
