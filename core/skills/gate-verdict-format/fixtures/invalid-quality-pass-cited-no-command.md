# Fixture — test-auditor PASS citing an output path but no command (schema v3.4 must reject; D-201)

A cited quality PASS names completion-auditor's output path AND the backticked command that run
executed, so the Stop hook can check the command ran in this session. A path alone is not enough.

```verdict
{"gate": "quality", "agent": "test-auditor", "artifact": "PR #908 — dedupe.test.ts", "verdict": "PASS", "confidence": 8, "falsifier": "a dedupe case with two tenants that the suite does not cover", "standards": ["none: practice applied: tenant-isolation review"], "evidence": "CITED .claude/audit/ladder.txt 14 passed, 0 failed, including the two-tenant case at dedupe.test.ts:41"}
```
