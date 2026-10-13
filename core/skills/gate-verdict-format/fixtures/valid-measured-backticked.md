# Fixture — MEASURED naming the backticked command that was run (schema v3.3 valid)

```verdict
{"gate": "security", "agent": "security-architect", "artifact": "PR #512 — src/access.js", "verdict": "PASS", "confidence": 8, "falsifier": "an admin path that skips the tenant check", "standards": ["none: practice applied: tenant-isolation review"], "evidence": "MEASURED `npm test` 7 passed, 0 failed, including the admin cross-tenant case at test/access.test.js:21"}
```
