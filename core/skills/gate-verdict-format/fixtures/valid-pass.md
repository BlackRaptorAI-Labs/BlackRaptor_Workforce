# Fixture — a well-formed PASS

```verdict
{"gate":"security","agent":"security-architect","artifact":"PR #4127 — packages/api/src/routes/reports.ts","verdict":"PASS","confidence":8,"falsifier":"a code path that reaches deviceEvent without the tenant predicate","evidence":"reports.ts:27 — tenant_id taken from req.auth.tenantId, applied as a mandatory WHERE","standards":[{"designation":"ISO/IEC 27001","edition":"2022","clause":"A.8.3 Information access restriction","access":"full text","verified":"2026-08-14"}]}
```
