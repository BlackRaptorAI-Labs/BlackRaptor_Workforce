<!-- TEMPLATE — not onboarded -->
# Handoff — <program name>

*Written by the `hw-program` skill at every milestone. Filename:
`HANDOFF_<YYYY-MM-DD>_<program>_<milestone-reached>_<next-step>.md` — never overwrite a prior
handoff; the newest file in the handoffs folder is the live program state.*

## What this handoff is

One worked row, as an example of the shape every handoff takes:

| Field | This handoff |
|---|---|
| Milestone reached | CDR passed, 2026-08-14 |
| What changed since the last handoff | Power tree finalized (D-014); enclosure sealing spec locked (D-017); one open interface (12V rail surge rating) resolved between power-electronics and embedded-firmware |
| Register rows closed this cycle | D-011, D-014, D-017 |
| Open items blocking the next gate (MRR) | Bench validation of brown-out recovery (embedded-firmware); AVL second-source for the enclosure gasket (manufacturing-dfm) |
| Next step | Bench validation pass, then MRR readiness review |
| Files to read first | `decision-register.md`, `interface-control.md`, `sim/power/rail-budget-v4.py` |

## Rule

A handoff that omits open items blocking the next gate is incomplete — the point of this file is
that the next person (or the next dispatch) does not have to reconstruct program state from memory
or from a chat transcript that may not exist.
