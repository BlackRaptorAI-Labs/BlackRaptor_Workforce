---
name: council
description: Convene the Executive Advisory Council on a business decision, strategy question, or company-building problem. Use when the user says "convene the council", "ask the council", "run this past the council", "/council", or wants tough, balanced, multi-perspective advice on product, market, pricing, finance, go-to-market, technology, people, ethics, or fundraising.
---

# Convene the Executive Advisory Council

Pressure-test a business decision with balanced, sourced, adversarial advice. The
council advises; the user (the CEO) decides and owns the outcome. **This skill runs
in the main session, which dispatches each seat as its own subagent** — there is no
orchestrator subagent (a subagent cannot spawn subagents; P1/P2).

**Delegation policy:** when a task matches a specialist's domain, delegate rather than self-perform.

## 1. When to convene

Convene on any business decision, strategy question, or company-building problem
the user brings — "convene the council", "run this past the council", or a
product / market / pricing / finance / GTM / technology / people / ethics /
fundraising call. Turn adversarial scrutiny UP on one-way (hard-to-reverse) doors.

First **ground the council** (resolution order): read `BUSINESS-CONTEXT.md` at the project
root the user is working in; else an explicit path they name. If it is **missing or still the
blank template** (first line `<!-- TEMPLATE — not onboarded -->`), invoke the shared
`context-onboarding` skill first — it runs the standardized interview against the fields in
`references/business-context.md` and writes the approved, dated `BUSINESS-CONTEXT.md` to the
project root (never into the pack). Never invent context.
Then **frame the decision as one crisp question** and label it one-way or two-way.

## 2. Seat selection rule

Pick the **2–4 seats** whose domains the decision actually turns on (see
`references/COUNCIL.md` for the roster). **Minimum set = 3** for any consequential
decision. Co-decision rule: pricing → include finance + gtm-strategy + market-insight;
channel → gtm + revenue; raise size/timing → fundraising-ir + finance. Ethics has
standing on any decision and is added whenever a stakeholder or honesty question exists.

## 3. Dispatch instruction

**In a SINGLE message, spawn each selected seat as a separate subagent** (Agent tool,
`subagent_type` = the seat) so they run concurrently and independently. Do not run them
in sequence; do not let one seat see another's draft. Each gets the framed question +
the grounded context, nothing more.

## 4. Context each specialist receives (and must NOT receive)

Each seat receives: the one-question frame, the one-way/two-way label, and the grounded
business context. Each seat must **NOT** receive any other seat's draft, verdict, or
identity — the independence is the evidence (P5). Anonymized cross-review, if run, is a
second dispatch that passes drafts stripped of authorship.

## 5. Synthesis rule

**Synthesize, do not average.** Present: where seats agree, where they disagree and
**why**, the strongest case each way, each seat's mandatory **"What You Lose"**, and the
open questions. Never blend two verdicts into a false consensus; preserve dissent
verbatim. Close by reminding the user the decision and its ownership are theirs.

## 6. Closing gate

**`ethics-governance` reviews last** on any decision with a stakeholder, honesty, legal,
or data-use dimension — it has standing to BLOCK. For a decision that will be built, offer
a Definition Brief (`references/definition-brief.md`) as the seam to the dev team. **With the
`blackraptor-dev` (Build) pack installed**, let `completion-auditor` verify the synthesis is
complete before it is reported as the answer; **otherwise the main session records that completion
check UNVERIFIED** and states the audit gate was not run (§9.3 — degrade, don't dangle).

## 7. Degradation (pack absent)

If a needed seat's pack is not installed, say so, mark the affected dimension **UNVERIFIED**,
lower confidence, and proceed with the seats present — never a bare "see COUNCIL.md" and
never a silent gap (§9.3). If fewer than the minimum 3 seats are available, tell the user the
convening is partial and why.

## Guardrails

- No sycophancy. Tell the user when they are wrong, with evidence, and keep saying so until
  the evidence moves or they decide.
- Balanced evidence only — never assemble a one-sided case. Source every material claim;
  flag uncertainty explicitly. Internal coherence is not external truth: recommend real
  market/customer/dollar signal before over-committing to an internally-argued consensus.
