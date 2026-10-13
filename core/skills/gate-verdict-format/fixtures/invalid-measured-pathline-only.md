# Fixture — MEASURED with only a path:line (schema v3.3 must reject; D-146: that is CITED)

```verdict
{"gate": "security", "agent": "security-architect", "artifact": "PR #512 — src/access.js", "verdict": "PASS", "confidence": 8, "falsifier": "an admin path that skips the tenant check", "standards": ["none: practice applied: tenant-isolation review"], "evidence": "MEASURED test/access.test.js:21 admin cross-tenant read returns false"}
```
