# Blast radius — what a change is safe because of

Before certifying a change as safe, name the **single fact** it is safe because of, and prove that
fact by running code: a test, a query, a command whose output you quote with the MEASURED label.
"It is safe because nothing else uses this" is a fact; prove it. "It looks contained" is not.

## Where grep stops

A caller search finds callers that name the symbol in the same language. It does not find these,
and each needs its own check before "nothing else depends on this" is written:

1. **Wire formats.** JSON, protobuf, queue messages, webhook payloads and file formats that other
   services parse. Renaming a field breaks a reader that never imports your code.
2. **Database columns.** Other services, reports, views, triggers and ad-hoc jobs that read the same
   table. Check the schema's dependents, not only this repository.
3. **Other languages reading the same bytes.** A Python job, a SQL report or a shell script that
   reads what this TypeScript writes.
4. **Feature flags.** Code paths that are off today and will be on tomorrow. A flag-guarded caller
   is still a caller.
5. **Three hops downstream.** The consumer of the consumer of the consumer. Follow the data at least
   three hops, or say where you stopped and why.

State in `evidence` which of the five you checked, with the command for each, and which you did not.
