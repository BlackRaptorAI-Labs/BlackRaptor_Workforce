# Eval set — data-engineer

Run when `data-engineer.md` is amended. This is the schema-gate agent; its misses
corrupt data or take prod down on a migration. Each case: give the agent the
`input`, check the response meets `expect` and avoids `anti`. Run 3–5×/case;
record pass-rate + regressions in the PR / Change Record.

---

## Case 1 — a destructive migration bundled with dependent code is blocked
**input:** "Review this migration PR: it renames `users.full_name` to
`users.name` in one migration and, in the same PR, ships the code that reads the
new column. Deploy is merge-to-prod."
**expect:**
- Verdict **FAIL** — this violates expand/contract; a rename + dependent code in
  one slice breaks queries running against the old shape during rollout.
- Requires the expand/contract sequence: additive column first (backfill,
  dual-write), cut over readers in a later PR, drop the old column last.
- Confirms the migration is reversible and reviewed for lock/scale on a hot table.
**anti:** PASS; approving the rename because "tests pass"; ignoring the
in-flight-query window.

## Case 2 — lock/scale impact on a large table
**input:** "Add a `NOT NULL` column with a default to a 400M-row table."
**expect:** flags the rewrite/lock risk at that scale; requires the safe pattern
(add nullable, backfill in batches, then set the constraint) and asks for the
row-count/lock budget; treats a naive `ALTER` as a production incident.
**anti:** "just add the column"; no mention of lock/rewrite at scale.

## Case 3 — query performance / N+1
**input:** "This new endpoint lists an org's devices and, per device, its latest
event — implemented as a loop of per-device queries, unpaginated."
**expect:** identifies the N+1 and the unbounded result set; requires a single
set-based query (join/lateral) and pagination by default.
**anti:** approves; misses either the N+1 or the missing pagination.

## Case 4 — audit-trail / retention integrity boundary
**input:** "To fix a bug we want to UPDATE historical rows in the immutable
event-archive table to the corrected values."
**expect:** refuses silent mutation of the historical record; requires a
correction/compensating record that preserves the original, coordinates with
domain-compliance where the data underpins regulated output.
**anti:** approves an in-place overwrite of historical/audit data.

---

**Recording template:**
```
agent: data-engineer · date: ____ · cases: 4 · runs/case: 5
pass-rate: __/20 · regressions vs previous: ____
```
