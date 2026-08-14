# Eval-driven development

Tests prove a code path does what its author expected. **Evals** prove a
*judgment-shaped* system — an LLM feature, a detector, a scorer, an agent
definition — still does what it should after you change the prompt, the model,
the retrieval, or the persona. A prompt change with no eval run is the LLM
equivalent of an untested code change: it might be fine, and you have no way to
know.

This doc is the doctrine. It pairs with the proactive `agent-evals/` convention
(evals for the *agent definitions* themselves) and with the reactive
`docs/AGENT-RETROS.md` loop (which fires after a miss ships). Evals prevent;
retros correct.

## When it applies

Reach for an eval, not just a unit test, whenever the thing under change
produces a judgment rather than a deterministic value:

- An LLM feature (summaries, classification, extraction, natural-language
  interfaces, RAG answers, diagnostic/advisory output).
- A detector or scorer (anomaly detection, risk scoring, ranking) whose
  quality is precision/recall, not pass/fail.
- An agent definition — the personas in `agents/`. Changing a charter can
  regress its behavior invisibly; the `agent-evals/` set is how you catch it.

Deterministic code still gets ordinary tests. Evals are the tool for the parts
where "correct" is a distribution, not a constant.

## The rules

### 1. Golden sets

Maintain a fixed set of representative inputs with expected-output criteria for
each judgment-shaped feature. The set is chosen to cover the real distribution —
the easy cases, the known-hard cases, the adversarial cases, and the past
failures. Run it on every prompt / model / retrieval / persona change and
compare before merging. The golden set is an asset: it grows every time
something breaks in production (add the case that broke), and it is version-
controlled alongside the code it guards.

Expected-output criteria are a **checklist against intent**, not an exact
string match — a good response can be phrased many ways. Score against the
properties a correct answer must have (right verdict, specific evidence cited,
boundary honored, structured output parses) and the failure signals it must
avoid (unevidenced confidence, scope creep, asserting the unverifiable as
fact).

### 2. Never-drop gates

An eval score is a ratchet. **A change may not lower the pass rate on the
golden set** — the gate is "no regressions," not "still pretty good." If a
change genuinely obsoletes a case (the behavior it checked was intentionally
removed), you delete the case *deliberately and on the record*, not by letting
it silently start failing. A quietly dropped case is how coverage rots.

For stochastic systems, measure the pass *rate* over multiple runs, not a
single sample — variance matters more than one lucky pass. A gate-shaped
judgment that passes 3/5 is not reliable, and reporting only the good run is a
form of the dishonesty rule below.

### 3. Byte-identical for refactors

When a change is *supposed* to be behavior-preserving — a refactor, a prompt
cleanup that shouldn't move outputs, a model-plumbing change — the bar is
**byte-identical output on the golden set**, not merely "still passes." Diff the
outputs. A refactor that changes what the system emits is not a refactor; it is
an unreviewed behavior change wearing a refactor's label, and it goes back for
a real spec. This is the single cheapest way to catch an accidental change of
meaning.

### 4. Frozen fixtures

Eval fixtures must be **self-contained and frozen**: the input, the retrieved
context, and the expected criteria all live in the case, inline, not fetched
from a live system or a repo path that may not exist at run time. Two reasons:

- A grounded agent will (correctly) refuse to review an artifact it cannot see,
  and that refusal scores as a false failure — noise that trains you to ignore
  red.
- An eval whose inputs drift under it is measuring the fixture, not the change.
  If the case tests behavior on "a change," the case *carries* the change.

Freeze the model version and generation parameters in the eval record too, so a
score is reproducible and a regression can be attributed to the diff rather
than to a silent upstream model update.

### 5. Honesty rules

Evals are worthless if the scoring lies to you. Non-negotiable:

- **Report the real pass rate**, including the runs that failed. Never cherry-
  pick the good sample.
- **A skipped or deleted case is a recorded decision**, with a reason — never a
  silent omission.
- **Claims about output are re-run, not remembered.** "It still works" is not
  evidence; the eval run is. This is the same challenge discipline the rest of
  the team runs on: a claim a machine can check gets checked.
- **A green eval suite is not a rebuttal to a specific doubt.** The suite
  encodes the cases you thought of; it passes exactly where your mental model
  is right. When a reviewer names a failure mode the set doesn't cover, the
  answer is a new case, not "the evals pass."

## How it plugs into the workflow

- `principal-architect` names the eval strategy for any judgment-shaped feature
  in the spec, alongside the test strategy.
- The responsible engineer (often `ai-ml-engineer`) maintains the golden set
  and runs it on every relevant change; `qa-test-engineer` treats "eval run
  recorded, no regressions" as part of definition-of-done for these features.
- For Tier-2+ changes, the eval result — pass rate, runs per case, regressions
  vs. last — is recorded in the Change Record like any other gate evidence.
- When an agent definition itself changes, its `agent-evals/` set runs and the
  result is recorded in the PR (see `agent-evals/README.md`).

The throughline: for anything that produces a judgment, the eval *is* the
specification made runnable, and the golden set is the memory that keeps the
system from silently getting worse.
