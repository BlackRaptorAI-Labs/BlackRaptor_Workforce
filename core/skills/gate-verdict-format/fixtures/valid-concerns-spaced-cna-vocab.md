# Fixture — CONCERNS with conditions, and the spaced COULD NOT ASSESS spelling accepted elsewhere

```verdict
{"gate":"quality","agent":"test-auditor","artifact":"PR #908 — dedupe.test.ts","verdict":"CONCERNS","confidence":6,"falsifier":"a test that drives two tenants through the real de-dup store","evidence":"CITED dedupe.test.ts:1-40 — every case uses tenantId 't1'","conditions":["add a case asserting the same fingerprint from two tenants notifies both","replace the 5100 ms sleep with a clock the test controls"],"standards":["none: practice applied: acceptance-criteria-to-test traceability"]}
```

```verdict
{"gate":"ux","agent":"ux-designer","artifact":"Fleet Health spec","verdict":"COULD NOT ASSESS","confidence":1,"falsifier":"the rendered screen","evidence":"CITED only tokens.css and a prose spec were supplied","reason":"no rendered screen or component source was provided; contrast can be computed but focus order cannot be observed","standards":["none: practice applied: WCAG 2.2 AA review"]}
```
