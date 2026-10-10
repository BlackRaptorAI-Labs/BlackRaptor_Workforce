# Fixture — test-auditor PASS without a run (schema v3.2 must reject)

A cited line is re-checkable, but a quality gate's PASS must rest on a run: evidence opens with MEASURED.

```verdict
{"gate": "quality", "agent": "test-auditor", "artifact": "PR #908 — dedupe.test.ts", "verdict": "PASS", "confidence": 8, "falsifier": "a dedupe case with two tenants that the suite does not cover", "standards": ["none: practice applied: tenant-isolation review"], "evidence": "CITED dedupe.test.ts:12-40 covers both tenant ids"}
```
