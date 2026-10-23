# Fixture — test-auditor PASS citing completion-auditor's run (schema v3.4 valid; D-201)

test-auditor holds no Bash, so it cannot produce MEASURED. It cites the run completion-auditor made:
CITED, then completion-auditor's output path, then the backticked command that run executed.

```verdict
{"gate": "quality", "agent": "test-auditor", "artifact": "PR #908 — dedupe.test.ts", "verdict": "PASS", "confidence": 8, "falsifier": "a dedupe case with two tenants that the suite does not cover", "standards": ["none: practice applied: tenant-isolation review"], "evidence": "CITED .claude/audit/ladder.txt `npm test -- dedupe` 14 passed, 0 failed, including the two-tenant case at dedupe.test.ts:41"}
```
