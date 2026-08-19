<!-- TEMPLATE — not onboarded -->
# PROGRAM-CONTEXT — <program name>

*The program-specific context every Hardware team agent reads before starting work. Keep this file in the program's engineering folder, next to the decision register. Update it at every handoff — a stale context file misleads every agent that reads it. The agents themselves are product-agnostic; this file is where the product lives.*

## Device

One paragraph: what the device is, where it's deployed, the environment it must survive, the volume target, and the service model (field-serviceable vs. whole-unit swap).

## Source of truth

- **Decision register:** `<path>` — locked decisions; every deliverable traces to these.
- **Handoffs:** `<folder>` — newest `HANDOFF_*.md` is the live program state. Naming: `HANDOFF_<YYYY-MM-DD>_<program>_<milestone-reached>_<next-step>.md`; never overwrite.
- **Specs:** `<paths>` — per-discipline spec documents and their status (draft / v0.1 / frozen).
- **Simulations:** `<path to sim/>` — reproducible models; re-run when upstream inputs change.

## Locked architecture (summary — the register is authoritative)

Bullet the decisions that shape every seat's work: compute platform, power input class, enclosure approach, radio scope, service model, design-margin policy. Cite register IDs (e.g. D-00x) — do not restate rationale here.

## Program-wide rules

- Margin policy (e.g. datasheet + N% conservative margins until bench characterization; all affected sections marked PROVISIONAL).
- Flag conventions: `[VERIFY: ...]` for unchecked claims, `[V]` for volatile data (pricing, availability) with date-checked, PROVISIONAL for pre-bench values.
- Any program-specific standards (derating standard, environment class, naming).

## Seat → topic mapping

| Seat | Program topics / documents it owns |
|------|-----------------------------------|
| power-electronics | … |
| thermal-mechanical | … |
| rf-connectivity | … |
| embedded-firmware | … |
| reliability-dfr | … |
| compliance-cert | … |
| manufacturing-dfm | … |
| cost-engineer | … |
| the `hw-program` skill (main session) | decision register, interfaces, handoffs, gates |

## Current state and queue

- Completed: …
- **Next (queued):** …
- Then, in order: …
- Urgent/watch items: …

## Open decisions awaiting the founder

Numbered, each with the options and quantified consequences. The team prepares these; the human makes them.
