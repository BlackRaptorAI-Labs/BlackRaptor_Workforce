# Fixture — a well-formed COULD_NOT_ASSESS

```verdict
{"gate":"schema","agent":"schema-reviewer","artifact":"PR #4188 — migrations/20260901120000_rename_tenant_key.sql","verdict":"COULD_NOT_ASSESS","confidence":2,"falsifier":"the table statistics, which would let me state the lock duration","evidence":"CITED the diff contains the migration but no row count or write rate for device_event","reason":"live row count and write rate were not supplied; a lock duration guessed from an assumed table size would be a fabricated number","standards":["none: practice applied: expand/contract migration ordering"]}
```
