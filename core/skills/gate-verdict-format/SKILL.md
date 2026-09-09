---
name: gate-verdict-format
description: >-
  The standard output format every gate agent uses so verdicts drop cleanly into a Change Record. Use when a security/privacy/compliance/domain/schema gate agent produces a verdict on a diff. Shared by all blocking-gate agents.
---

# Gate verdict format (Change-Record-ready)

Every gate agent's output is pasted verbatim into §3 of the PR's Change Record
(`docs/change-records/CR-*.md`) and its verdict fills the §2 gate table. Make it
paste-ready and self-contained.

## Structure

```
## <Gate name> — <agent name>

**Verdict:** PASS | CONCERNS | FAIL | COULD NOT ASSESS
(map to the gate table: PASS = ACCEPT-eligible, CONCERNS = accept-with-
conditions, FAIL = rework or requires a §5 risk-acceptance to overrule,
COULD NOT ASSESS = the gate ran and could not finish — BLOCKING, never neutral)

**Confidence:** <n>/10

**Falsifier:** <the one observation that would flip this verdict>

**Standards:** <designation, edition, clause> — <access> — verified <date>
(or: no published standard governs; practice applied: <x>)

**Scope reviewed:** <what you looked at — files/paths/diff range>

**Not reviewed / assumptions:** <context you were not given or could not verify —
name it explicitly rather than silently narrowing scope; "none" if fully scoped>

**Findings:**
- [severity] <finding> — evidence: `path:line` — why it matters — fix.
- (repeat; every finding needs file:line evidence, no vibes)

**Conditions to clear (if CONCERNS/FAIL):** <specific, testable>

**Model/agent version:** <if the agent definition changed recently>
```

## Machine-parseable verdict block (schema v3 — required)

Immediately after the prose above, emit a fenced `verdict` block. One vocabulary,
replacing the old per-gate APPROVE/READY/CHANGES words. `validate_verdict.py`
(shipped alongside this skill) checks it; the `change-record-required` CI check runs
that same validator; and in a live session the core `Stop` hook runs it over every
gate result and **blocks the turn** on a missing or invalid block.

```verdict
{"gate":"security","agent":"<gate-agent-slug>","artifact":"PR #123 / <file/diff>","verdict":"FAIL","confidence":3,"falsifier":"a rate-limit middleware on the login route with a test asserting 429 after N attempts","evidence":"login.ts:42 — no rate limit on the login route, and no test asserts lockout","standards":[{"designation":"ISO/IEC 27001","edition":"2022","clause":"A.8.5 Secure authentication","access":"full text","verified":"2026-08-14"}],"conditions":["add rate limiting to the login route","add the 429 lockout test"]}
```

Fields (schema: `verdict-schema.json`, v3):

| Field | Shape | Note |
|---|---|---|
| `gate`, `agent`, `artifact` | non-blank strings | what role, who, what was reviewed |
| `verdict` | `PASS \| CONCERNS \| FAIL \| COULD_NOT_ASSESS` | `N/A` is **not** a verdict — see below |
| `confidence` | **integer 0-10** | a number, so a threshold can be written against it |
| `falsifier` | non-blank string | the one fact that would flip it |
| `evidence` | **a string** | file:line or the concrete basis (an array in v2) |
| `standards` | **required array** | each entry `{designation, edition, clause, access, verified}`, or the single literal `"none: practice applied: <x>"` |
| `conditions[]` | required, non-empty, on CONCERNS and FAIL | specific and testable |
| `reason` | **present only on `COULD NOT ASSESS`** | omit the key entirely on every other verdict; never emit it blank. What blocked it, and what would unblock it. A blank `reason` fails the schema (`pattern: "\S"`) and the `Stop` hook sends the block back. |

The prose and the block must agree. The canonical machine spelling is
`COULD_NOT_ASSESS`; the spaced `COULD NOT ASSESS` is accepted too, because the
`Stop` hook must never block a gate over a space.

**`standards` is not optional and not decorative.** If you invoked a designation, say
which edition and clause you relied on, how you reached the text, and the date you
checked it at the issuing body. If no published standard governs the review, the array
is `["none: practice applied: <the practice>"]`. A designation with no access route and
no verification date is a memory, not a citation.

**If you could not reach the primary text, do NOT emit it as a `standards[]` object.**
`verified` is required and must be a real `YYYY-MM-DD` on which you checked the
designation and clause AT THE ISSUING BODY — so a standard you never reached has no
valid value to put there, and inventing one is the first thing the operating contract
forbids. Take one of these three routes instead:

1. **You reached a secondary source.** Cite that: `access` is
   `"secondary source: <which>"` and `verified` is the date you checked **that source**.
2. **You reached nothing.** Leave the designation out of `standards[]`, name it in your
   prose or `evidence` as an unverified pointer, and carry the array as
   `["none: practice applied: <the practice you actually applied>"]`.
3. **The verdict genuinely rests on it.** Then you could not perform the review:
   the verdict is `COULD NOT ASSESS`, with `reason` naming the text you could not
   reach and what would unblock you.

A verdict never rests on a designation you did not read.

## Rules
- **The verdict is advice; the human decides.** You never fill the "My decision"
  column or sign — the human records ACCEPT / ACCEPT-WITH-RISK / REWORK.
- If the human overrules a FAIL, the Change Record's §5 risk-acceptance entry is
  **mandatory** — state that in your output.
- Every finding carries `file:line` evidence. No-evidence items are dropped.
- **`N/A` is not a verdict** (removed in v3). A gate that does not apply emits **no
  verdict block at all**; the Change Record's §2 row carries the N/A with one line of
  why. An unexplained N/A is the rubber stamp an auditor looks for, and `N/A` as a
  verdict value made "did not apply" and "reviewed and found nothing" the same string.
- **`COULD NOT ASSESS` is mandatory when it is true.** A gate that timed out, ran out
  of context on a large artifact, or was not given a required input says so, with a
  `reason`. It is BLOCKING, never neutral — the completion-verification pass treats it that way.
  Without it, a review you could not perform is indistinguishable from a pass.
- A verdict is only as good as its inputs: if you weren't given the spec, the
  full diff, or a file you needed, say so in "Not reviewed / assumptions" — the
  orchestrator must close the gap and re-invoke, not accept a narrowed review.

## Adversarial method

Two moves that separate a real review from style notes. Apply both to every
diff-shaped review:

1. **Attack the diff's named claims.** Enumerate what the author's report and
   the PR description CLAIM ("X can never override Y", "opting out clears
   pending events", "the nil path is byte-identical") and hunt for the inputs,
   interleavings, and states under which each claim is false. Author-written
   tests encode the author's mental model — they pass exactly where the mental
   model is wrong, so a green suite is not a rebuttal. The claims come from
   the completion report; that is why reports must state claims explicitly.
2. **Hunt phantom mechanisms.** Search for any place a comment, design doc, or
   spec promises a mechanism the code does not actually implement — the lock
   everyone builds on that was never written, the "verified against pinned
   hash" comment above a plain size check, the rate limiter the design assumes.
   Tests exercise paths that exist; per-diff review reads lines that changed;
   the absent mechanism appears in neither. It is found only by deliberately
   asking for it.

For every assumed safety invariant the diff relies on, demand the file:line
where it is enforced and the test that would fail if it weren't (see the
`enforcement-liveness` skill; the spec-side twin is the architect's invariant
ledger). "It's enforced by convention" and "the doc says so" are findings, not
answers.
