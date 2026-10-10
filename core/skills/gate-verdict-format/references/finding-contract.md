# Finding contract (gate-verdict-format v3.2, long form)

The SKILL states the rules. This file holds the detail a gate needs while writing a row.

## The row

One claim per row. Ten columns, in this order:

| Column | What goes in it |
|---|---|
| `id` | `F1`, `F2`, ... Stable across re-reviews: a delta re-review refers back to these. |
| `claim` | One defect, stated so it can be false. Two defects are two rows. |
| `class coverage` | The kind of entry point, then each one marked: `affected: path:line, ...; clean: path:line, ...`. |
| `evidence` | Label first (`MEASURED`, `CITED`, `COMPUTED`, `ESTIMATED`, `ASSUMED`), then `path:line@sha` and the exact quote, or the command and its output. |
| `severity` | Critical, High, Medium or Low (scale below). |
| `confidence` | `n/10`, the same scale as the verdict block. |
| `falsifier` | The one observation that would show this row is wrong. |
| `minimum fix` | The smallest change that closes the defect. Not a redesign. |
| `proof of closure` | The check that fails today and passes once fixed: a test, a command, a grep with its expected output. |
| `disposition` | Act on, Consider, Noted or Dismissed. |

A row missing class coverage, minimum fix or proof of closure is incomplete. The orchestrator sends
it back; it is not merged into the report.

## Class coverage

A defect found at one entry point is usually present at its siblings. Before writing the row,
enumerate every entry point of the same kind and mark each one:

- data paths: create, update, delete, bulk and import paths for the same record;
- protocol paths: every challenge type, message type or channel that reaches the same handler;
- callers: every caller kind (user, service, scheduled job, webhook, admin tool).

Write `class: <kind> → affected: a:12, c:88; clean: b:40, d:9`. "Clean" needs a `path:line` too:
an unmarked sibling has not been checked.

## The finding brake

Before any row is written, answer four questions. If one has no answer, do not write the row.

1. Can I cite the exact line?
2. Can I describe the concrete failure (the wrong output, the leak, the crash)?
3. Can I name the trigger (the input, state or sequence that causes it)?
4. Why do the existing guards not catch it? Name the guard you checked.

A clean verdict with zero findings is a valid result. Class coverage pushes recall up and the brake
pushes precision up; they pull in opposite directions on purpose, and neither replaces the other.

## Calibration

- Quote the exact line you rely on, not a paraphrase.
- "No", "never", "every", "all" and "none" are search results. Put the search command and its output
  in `evidence`.
- Before writing "none exists", search for partial controls (a check in a different layer, a
  framework default, a wrapper) and name what you found.
- Every count carries the command that produced it.

## Vendor and framework claims

A claim about how a vendor service or framework behaves is CITED with the fetched URL and the
quoted sentence. Without that it is ASSUMED, its severity is at most Medium, and it cannot be the
basis of a blocking verdict.

## Severity

| Level | Meaning |
|---|---|
| Critical | Exploitable or data-loss now, in production. |
| High | Exploitable with a precondition, or a control that is absent on a live path. |
| Medium | A defect with a compensating control. |
| Low | Hygiene. |

## Delta re-review: closure lines

On a re-review, list every prior finding first, one line each, judged at the new commit:

```
F1 CLOSED  — MEASURED `npm test -- auth.spec.ts` 14/14 at 9e1b0c2; the recorded proof of closure now passes
F2 PARTIAL — CITED `api/users.ts:88@9e1b0c2` "if (!isAdmin) ..." fixes update; delete at `api/users.ts:131` still open
F3 OPEN    — CITED `db/migrate/0042.sql:3@9e1b0c2` unchanged since the prior review
```

CLOSED needs the recorded proof of closure, run or quoted at the new commit. PARTIAL names what is
still open. New findings follow, limited to changed text plus any Critical anywhere.

## PASS evidence (schema v3.2)

A PASS must be re-checkable by someone who was not there. The validator rejects:

- a bare label: `MEASURED`, `CITED`;
- an ASSUMED PASS: `ASSUMED I hand-traced the handler`;
- a label with nothing to re-check: `MEASURED hand-traced, nothing was run`, `COMPUTED by eye`.

It accepts, for example, `CITED reports.ts:27 tenant_id taken from req.auth` or
``MEASURED `npm test -- dedupe` 14 passed, 0 failed``. For the test-quality and completion gates the
PASS opens with `MEASURED`: a quality gate's PASS rests on a run. If you cannot meet this, the honest
verdict is CONCERNS (with the run as a condition) or COULD NOT ASSESS (with a `reason`).

