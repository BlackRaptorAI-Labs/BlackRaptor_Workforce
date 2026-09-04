# BlackRaptor Workforce — Hardware Engineering Team — Roster, Gates, and Process

The eight-seat hardware engineering team, conducted by the main-session `hw-program` skill. Product-agnostic: each agent carries discipline expertise only; everything program-specific (device, locked decisions, current state, document paths) lives in the program's `PROGRAM-CONTEXT.md` — see `${CLAUDE_PLUGIN_ROOT}/templates/program-context.md`. One team, any device.

The team designs by the physics and doctrine in `${CLAUDE_PLUGIN_ROOT}/docs/engineering-principles.md` — the binding canon of laws, reliability models, and cost levers — under the design philosophy in CLAUDE.md: the least expensive device that functions in its conditions for its design life (nominally 3–5 years, then replaced). Cost-vs-target is an exit criterion at every gate; over-design is a reviewable defect alongside under-design.

## The roster

| # | Seat | Agent | Model | Outcome the seat drives |
|---|------|-------|-------|------------------------|
| 1 | Power Electronics | `power-electronics` | Opus | Every rail proven with margin at temperature; input survives surges; no field brownout-resets |
| 2 | Thermal/Mechanical | `thermal-mechanical` | Opus | Junction temps in-margin at worst-case ambient + full sun, fanless; an enclosure manufacturable at volume that seals to its ingress target |
| 3 | RF/Connectivity | `rf-connectivity` | Opus | Closed link budgets at worst-case sites; certification-preserving antenna config; an emergent link that works when everything else is down |
| 4 | Embedded/Firmware | `embedded-firmware` | Sonnet | Device recovers from any power cut or bad update without a truck roll; factory provisioning flow defined |
| 5 | Reliability/Quality (DfR) | `reliability-dfr` | Opus | Predicted failure rates the warranty reserve can stand on; every single-point failure mitigated or accepted knowingly |
| 6 | Compliance/Certification | `compliance-cert` | Opus | A cert plan with no surprises — every design choice pre-checked against the rules before tooling money is spent |
| 7 | Manufacturing/DFM | `manufacturing-dfm` | Sonnet | Buildable at target volume — no hand-tuned steps, no unobtainable parts, yield targets defined |
| 8 | Cost Engineering | `cost-engineer` | Sonnet | An honest per-unit number the financial model can stand on |

**Program conduction is the `hw-program` skill (main session), not an agent.** It dispatches the discipline seats with written briefs, keeps the decision register and interface control, tracks requirement traceability, assesses gate readiness (PDR/CDR/MRR), and authors the handoffs. It is process only — no seat, no gate, no content authority — and holds no model tier of its own; in subagent context the `Agent` and Task tools are stripped (P1/P2), so orchestration lives in the main session that runs the skill. (The `systems-integration` agent was retired at 5.9, 2026-08-10; its conduction duties moved to this skill.)

Cross-cutting: **`hw-design-reviewer`** (Opus) — the adversarial reviewer. Not a seat; the second set of eyes every seat's gate-bound work must pass. Producer → `hw-design-reviewer` → revise is mandatory before anything that gates a board spin, tooling commitment, purchase, or external commitment.

## Market grounding and research validation (the shared bridge)

The team depends on the **`blackraptor-core`** plugin (auto-installed with it) for the two checks engineering cannot referee for itself:

- **`blackraptor-core:product-manager`** — the market-side owner of *what the device should be*. Convened by the `hw-program` skill at **requirement intake and PDR** (and for any post-PDR scope addition) to validate that the device's makeup — feature set, design life, cost target, tier positioning — traces to customer need and willingness-to-pay, not engineering preference. The team's over-design doctrine polices gold-plating *against the requirements*; product-manager polices the *requirements themselves*. Engineers do not author market requirements.
- **`blackraptor-core:evidence-auditor`** + the **`research-integrity`** skill — the heavy-tier gate for load-bearing *external research claims*: component pricing and lead times, lifecycle/EOL status, standards applicability and market-access rules, vendor claims. Used by `cost-engineer`, `compliance-cert`, and the `hw-program` skill (component-selection decisions) before such a claim hardens into a purchase, a cert plan, or the financial model.

Division of labor stays clean: **math and engineering verification remain with `hw-design-reviewer`** and the Excellence Pass (independent-method re-derivation) — the bridge validates market fit and research claims, never physics.

Model tiers follow the rule in CLAUDE.md: Opus for judgment-heavy design and review (its failure mode is narrow under-verification, so the verification loop stays mandatory); Sonnet for well-scoped seats with the Excellence Pass items written as explicit, visibly-completed checklist steps (it performs them at top-tier level when named, skips them when not). Program conduction is the main-session `hw-program` skill and carries no agent tier of its own.

## Cross-review matrix (who audits whom)

Every seat reviews the others' assumptions in its own domain at each gate:

- `power-electronics` audits everyone's power assumptions (thermal's dissipation inputs, RF's transmit bursts, firmware's power states)
- `thermal-mechanical` audits everyone's thermal/mechanical assumptions (power dissipation placement, RF penetrations, DFM's effect on thermal joints)
- `rf-connectivity` audits enclosure material/finish near radiators, pad geometry, modem control contracts
- `reliability-dfr` audits every seat's derating and margins — standing to challenge any number in the program
- `compliance-cert` pre-checks every design choice against the rules before it hardens
- `manufacturing-dfm` audits buildability of everything fabricated or assembled
- `cost-engineer` re-derives the cost consequence of every choice
- the `hw-program` skill (main session) runs the matrix, resolves conflicts against the decision register, and owns the interfaces

## The review gates

**PDR — Preliminary Design Review.** Entry: every seat's v0.1 spec exists. Exercise: full cross-review matrix; conflicts resolved against the decision register; open-item queues consolidated with owners. Exit: no unresolved cross-domain contradiction; PROVISIONAL flags inventoried.

**Bench characterization.** The one physical step: real hardware measured (compute module, radios, transient behavior, thermal mule as applicable). Every PROVISIONAL flag in every spec is replaced with a measured value or explicitly carried with rationale.

**CDR — Critical Design Review.** Entry: bench data in hand. Exercise: every simulation re-run with measured inputs; DFMEA closed; the "requires bench verification" lists consolidated into the validation test plan. Exit: v1.0 specs frozen. After CDR, changes require a formal decision-register entry.

**MRR — Manufacturing Readiness Review.** Exit: `manufacturing-dfm` signs the design as buildable; acceptance-test spec exists; AVL has second sources where possible; the Manufacturing Data Package is assembled.

## The end product: Manufacturing Data Package

What the program delivers so a manufacturer or design house can quote and build without guessing: master product specification (every requirement traceable to the decision register); structured BOM (manufacturer part numbers, spec, rationale, alternates, target cost); subsystem specs with simulation evidence and tolerances; enclosure definition to tooling-intent level; acceptance-test specification and provisioning flow; quality package (DFMEA, derating audit, inspection criteria); compliance plan (certifications, order, lab scope).

What the manufacturer does with it: schematic capture and layout, 3D CAD and tooling, prototype builds, and the physical lab validation simulation can't replace (EMC chamber, thermal chamber, HALT, certification testing). The package's completeness is what keeps their NRE low and prevents silent design decisions.

## Operating rhythm

1. The `hw-program` skill reads the program state (register + newest HANDOFF) and dispatches the next seat with a written brief.
2. The seat produces; for gate-bound work, `hw-design-reviewer` reviews adversarially; the seat revises.
3. The `hw-program` skill updates the register, interfaces, and open-item queues, and authors the HANDOFF at every pause point:
   `HANDOFF_<YYYY-MM-DD>_<program>_<milestone-reached>_<next-step>.md` — never overwrite a prior handoff; the newest is the live one.
4. Founder decisions are queued explicitly with options quantified — prepared by the team, made by the human.

Simulation and analysis are code: models live in the program's `sim/` directory, reproducible, seeds fixed, outputs reproduced in the docs they support.

---

Validated against `claude-opus-4-8` as of 2026-09-02.
