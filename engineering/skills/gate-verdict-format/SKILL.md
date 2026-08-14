---
name: gate-verdict-format
description: >-
  The standard output format every gate agent uses so verdicts drop cleanly into
  a Change Record. Use when a security/privacy/compliance/domain/schema gate
  agent produces a verdict on a diff. Triggers: "gate review", "produce a
  verdict", "review for the change record". Shared by all blocking-gate agents.
---

# Gate verdict format (Change-Record-ready)

Every gate agent's output is pasted verbatim into §3 of the PR's Change Record
(`docs/change-records/CR-*.md`) and its verdict fills the §2 gate table. Make it
paste-ready and self-contained.

## Structure

```
## <Gate name> — <agent name>

**Verdict:** PASS | CONCERNS | FAIL
(map to the gate table: PASS = ACCEPT-eligible, CONCERNS = accept-with-
conditions, FAIL = rework or requires a §5 risk-acceptance to overrule)

**Scope reviewed:** <what you looked at — files/paths/diff range>

**Not reviewed / assumptions:** <context you were not given or could not verify —
name it explicitly rather than silently narrowing scope; "none" if fully scoped>

**Findings:**
- [severity] <finding> — evidence: `path:line` — why it matters — fix.
- (repeat; every finding needs file:line evidence, no vibes)

**Conditions to clear (if CONCERNS/FAIL):** <specific, testable>

**Model/agent version:** <if the agent definition changed recently>
```

## Machine-parseable verdict block (R11 — required)

Immediately after the prose above, emit a fenced `verdict` block. This is the single
machine-readable verdict (one vocabulary — `PASS | CONCERNS | FAIL | N/A | COULD NOT ASSESS` — replacing
the old per-gate APPROVE/READY/CHANGES words). The orchestrator's validator `validate_verdict.py`
(shipped alongside this skill) checks it, and the `change-record-required` CI check runs that same
validator; a malformed or no-evidence block fails the check.

```verdict
{"gate":"security","agent":"<gate-agent-slug>","artifact":"PR #123 / <file/diff>","verdict":"FAIL","evidence":["login.ts:42 — no rate limit on the login route","no test asserts lockout"],"confidence":"high","falsifier":"a rate-limit middleware on the login route with a test asserting 429 after N attempts","conditions":["add rate limiting to the login route","add the 429 lockout test"]}
```

Fields (schema: `verdict-schema.json`): `gate, agent, artifact, verdict,
evidence[] (>=1, each file:line or concrete basis), confidence (high|medium|low),
falsifier (the one fact that would flip it)`. `conditions[]` is REQUIRED for
CONCERNS/FAIL; `reason` is REQUIRED for N/A. The prose and the block must agree.

## Rules
- **The verdict is advice; the human decides.** You never fill the "My decision"
  column or sign — the human records ACCEPT / ACCEPT-WITH-RISK / REWORK.
- If the human overrules a FAIL, the Change Record's §5 risk-acceptance entry is
  **mandatory** — state that in your output.
- Every finding carries `file:line` evidence. No-evidence items are dropped.
- N/A is a valid verdict for a gate that doesn't apply — but state one line of
  why. An unexplained N/A is the rubber stamp an auditor looks for.
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
