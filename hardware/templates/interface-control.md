<!-- TEMPLATE — not onboarded -->
# Interface control — <program name>

*Every boundary that crosses two disciplines, so neither ships a contradictory assumption about the
other's side. The `hw-program` skill (main session) owns this file; a discipline proposing a change
to an interface it does not own routes the change through the owning discipline, recorded here.*

## Interfaces

| Interface | Owner | Consumer(s) | Spec (current) | Status |
|---|---|---|---|---|
| 12V input rail, connector J1 | power-electronics | thermal-mechanical (heat budget), embedded-firmware (brown-out threshold) | 12V ±10%, 3A max continuous, surge to 40V/10ms per the input-protection spec `sim/power/input-protection-v2.py` | Locked |

## Change rule

An interface row changes only with the owning discipline's sign-off recorded here (who, when, ref).
A consumer that needs a different value from an interface proposes the change to the owner through
`hw-program`; it does not silently design against a value it wishes were true. A locked interface
changing after CDR is a register-level decision (`decision-register.md`), not a quiet edit here.
