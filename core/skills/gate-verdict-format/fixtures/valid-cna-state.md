# Fixture — aggregate state with the canonical COULD_NOT_ASSESS form (2.3.2, audit F8)

One PASS and one COULD_NOT_ASSESS (underscore form). The aggregate state must be HAS_COULD_NOT_ASSESS;
before the normalisation it read HAS_CONCERNS, which let a blocking verdict pass as a soft one.

```verdict
{"gate":"code-review","agent":"code-reviewer","artifact":"PR #4188 — migrations/20260901120000_rename_tenant_key.sql","verdict":"PASS","confidence":8,"falsifier":"a caller that still reads the old column name","evidence":"MEASURED `git grep -n tenant_key` returns no reader outside the migration","standards":["none: practice applied: conventional review checklist"]}
```

```verdict
{"gate":"schema","agent":"schema-reviewer","artifact":"PR #4188 — migrations/20260901120000_rename_tenant_key.sql","verdict":"COULD_NOT_ASSESS","confidence":2,"falsifier":"the table statistics, which would let me state the lock duration","evidence":"CITED the diff contains the migration but no row count or write rate for device_event","reason":"live row count and write rate were not supplied; a lock duration guessed from an assumed table size would be a fabricated number","standards":["none: practice applied: expand/contract migration ordering"]}
```
