<!-- TEMPLATE — not onboarded -->
# Decision register — <program name>

*Every locked decision the program's disciplines must not silently diverge from. The `hw-program`
skill (main session) owns this file: it records a decision when a discipline's dispatch produces
one, and every deliverable traces to a row here or flags the conflict rather than diverging quietly.*

## Register

| ID | Decision | Why | Who | Ref (spec / sim / bench data) | Status |
|---|---|---|---|---|---|
| D-001 | Enclosure sealed to IP66, natural convection only (no fan) | Field-deployed outdoor unit; a fan is the highest field-failure part class in this duty cycle, and the thermal budget closes fanless at the P90 ambient | thermal-mechanical, ratified by hw-program 2026-06-02 | `sim/thermal/enclosure-v3.py`, run 2026-06-01 | Locked |

## Tie-break rule

When two disciplines' recommendations conflict and neither can be reconciled by more analysis
(e.g. thermal wants more enclosure mass, cost wants less): the discipline whose domain the design
philosophy names as the harder constraint for THIS decision wins the tie — safety and regulatory
compliance outrank cost every time (`hw-operating-standard`'s "where cheapness must not win"); absent
a safety/compliance dimension, the decision escalates to the human with both positions and their
quantified trade-off stated, never silently resolved by whichever discipline argued longer. Record
the tie-break itself as a register row, with both original positions preserved.

## Gate exit criteria per seat (PDR / CDR / MRR)

| Seat | PDR exit | CDR exit | MRR exit |
|---|---|---|---|
| power-electronics | Rail budget closes at worst-case load with stated margin | Full power tree simulated at temperature extremes, protection circuits specified | Bench-validated at temperature; no open protection-circuit findings |
| thermal-mechanical | Enclosure architecture and cooling approach selected | Thermal model closes at P90 ambient + full sun with stated margin | Bench-validated junction/case temperatures at worst case |
| rf-connectivity | Link budget closes at the worst-case site requirement | Antenna placement and module certification path locked | Field or chamber-validated link margin |
| embedded-firmware | Boot/recovery architecture and OTA strategy selected | Register-level driver code reviewed against the reference manual | Bench-validated recovery from power-cut and bad-update scenarios |
| reliability-dfr | DFMEA started, single-point failures identified | Wear-out life models computed for every mechanism at P90 | No un-mitigated or unaccepted single-point failure remains |
| compliance-cert | Applicable standards and cert plan identified | Design pre-checked against the cert plan, lab scoped | Cert testing scheduled or complete with no blocking finding |
| manufacturing-dfm | Assembly sequence sketched, no unobtainable parts flagged | Tolerance analysis and AVL second-sourcing complete | Yield targets defined, test-point/fixture plan complete |
| cost-engineer | Should-cost model within target at the concept level | BOM should-cost locked, cost-driver ranking complete | Landed cost validated against actual quotes |
| the `hw-program` skill | Register + interfaces opened for the program | Every cross-discipline conflict in the register resolved or explicitly escalated | No open register row blocks the handoff |

A gate does not pass with an open row in this table for a seat the gate's exit criteria name.
