# Fixture — a re-review block that names only a short sha (D-187): rejected

```verdict
{"gate":"review","agent":"code-reviewer","artifact":"re-review of the tenant-check fix at 3f1c2a9","rereview_of":"9a8b7c6","verdict":"PASS","confidence":8,"falsifier":"a replayed bypass input that the new guard lets through","evidence":"MEASURED `npm test -- --grep tenant` 6 passed, 0 failed at the new head; CITED src/access.js:27 the guard","standards":["none: practice applied: delta re-review of a fix"]}
```
