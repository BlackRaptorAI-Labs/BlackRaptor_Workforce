---
name: prompt-brief
description: >-
  Use at the START of any non-trivial request to turn it into a buildable brief before work begins — ask 2-4 clarifying questions, write a short brief (goal/context/audience/constraints/done-criteria), confirm it, then route. Clear small asks pass straight through with zero friction.
---

# Prompt-brief — the intake ladder

Three rungs. Match the ask to the lightest rung that fits; never add friction a
small ask does not need.

## Rung 0 — context precheck (before substantive work)

Before doing substantive work for a pack, **resolve that pack's context file** per the
resolution order (current working / project root → an explicit path the user names). If it is
**missing or still a blank template** (first line `<!-- TEMPLATE — not onboarded -->`), invoke
the **`context-onboarding`** skill first, then proceed. Trivial or context-free asks (a typo fix,
a unit conversion, a one-off with no company/project dependency) skip this — it fires only when
the work actually depends on knowing the company or project. This is an instruction, not a hard
gate; `workforce-doctor` check 6 is the visibility backstop.

**Several asks in one message.** Open with one line naming asks two onward ("Also noted, after
this: X; Y."), then answer the first. That line is never a question.

## Rung 1 — pass-through (the DEFAULT; the intake must earn its turn)

**Redesign (order-11, measured): the intake is not free — asking costs a round-trip.
It only pays off when it prevents ≥2 rounds of rework.** So pass straight through —
no questions, no brief, do it directly — whenever you can **already state the
done-criteria yourself** from the ask (fix this typo, rename X, "add a filtered CSV
export", "size the 12V rail", and most concrete asks). Zero friction is the default,
not the exception. A measured experiment found that firing the intake on asks whose
done-criteria were already clear *added* turns without reducing rework — do not repeat it.

## Rung 2 — prompt-brief (only when the intake will REPAY its turn)

Run the intake **only when a clarification would materially change the deliverable
AND you cannot state the done-criteria without it** — genuine ambiguity (multiple
plausible scopes, an unstated format/constraint that flips the build, a decision
whose success bar you can't write). Then:

1. Ask the **fewest questions that resolve the ambiguity** (1–3, not a checklist) —
   only what changes the deliverable. Honor `question-style`: `assume-and-flag` → prefer
   making a labeled ASSUMED assumption over asking (ask ≤1); `ask` → stop and ask when unsure. An
   irreversible action (trigger (b) below) always asks first, whatever the preference.
2. **Author the improved prompt (R18).** Restate the user's ask as a tightened, unambiguous
   prompt that folds in their answers — one tight paragraph in the user's own intent, ready to
   run. Honor `verbosity: brief`: the restatement stays tight, never padded. Pair it with the
   short brief:
   ```
   ## Restated prompt
   <the tightened, unambiguous ask, ready to run>

   ## Brief
   - Goal:
   - Context:
   - Audience:       # who reads/executes the output; written to their register
   - Constraints:
   - Done-criteria:   # the testable bar; becomes the completion-audit ruler
   ```

   **Audience is part of the ask.** Every prose deliverable names who will read and act on it
   (owner, GM, CFO, engineer, regulator) and is written in that reader's register; the
   done-criteria inherit it ("executable by the named audience without further explanation").
   Infer the audience when the ask makes it obvious and label the inference ASSUMED; ask only
   when it is genuinely ambiguous AND the answer would change the writing — the standard Rung-2
   test. Never add an audience question to a Rung-1 pass-through ask (the order-11 friction
   finding stands).
3. **One approval step (questions → author → approve/tweak → run).** Show the restated prompt +
   brief and let the user **Approve or edit** in a single motion. Do not re-ask after they
   approve; if they tweak, take the tweak and run.
4. **Route** to the right specialist/skill and build from the approved restatement.

The **Done-criteria are the ruler**: the completion-audit gate audits the finished
work against each done-criterion and cites them in its verdict. A brief with a
blank or unstateable Done-criteria cannot be built — that is escalation trigger (c).

## Rung 3 — escalate to product-manager

Escalate (hand the ask to `product-manager` for a full problem statement +
acceptance criteria) when **any** of these WRITTEN, TESTABLE triggers fires:

- **(a) ≥2 specialists implied** — delivering it needs two or more distinct
  specialist domains (e.g. schema + UI + auth).
- **(b) irreversible action** — it deletes, migrates, deploys, publishes,
  sends, charges, or otherwise cannot be cleanly undone.
- **(c) no stateable done-criteria** — you cannot write a testable Done-criteria
  line even after the clarifying questions.

A near-miss (exactly one specialist, reversible, with a clear done-criteria)
stays on Rung 2 — do not over-escalate.

The trigger logic is scripted and unit-tested: `_eval/baseline/intake_triggers.py`
(`classify()` decides pass-through / brief / escalate, and asserts each trigger
fires on a positive case and holds on a near-miss).
