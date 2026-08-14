# BlackRaptor Workforce — Hardware Engineering Team

The eight-seat **hardware engineering department** for Claude, plus an
adversarial design-review gate — built by
[BlackRaptor AI](https://github.com/BlackRaptorAI) as the hardware sibling of
[blackraptor](https://github.com/BlackRaptorAI/blackraptor) (the
development team + executive advisory council) and
[blackraptor](https://github.com/BlackRaptorAI/blackraptor),
held to the same operating standard: **agents design and analyze — humans make
the irreversible calls.**

Product-agnostic: each program supplies its own `PROGRAM-CONTEXT.md` (template
included). The design doctrine is baked into every seat: **the least expensive
device that functions in its conditions for its design life** — cost is a
requirement with the same standing as performance, over-design is a reviewable
defect, datasheets are ground truth, worst-case not typical. Built on the
**Agent Operating Standard v2** (the Excellence Pass), with the full standard
behind every rule included in `hw-engineering/docs/`.

## Install

| Where | How | Status |
|---|---|---|
| **Claude Code — recommended** | `claude plugin marketplace add BlackRaptorAI/blackraptor` then `claude plugin install blackraptor-hardware@blackraptor-ai` — auto-pulls **blackraptor-core** (product-manager + evidence-auditor + research-integrity) | ✅ Available now |
| **Claude Code — this repo directly** | `claude plugin marketplace add BlackRaptorAI/blackraptor` then `claude plugin install blackraptor-hardware` (bridge auto-installs only if the `blackraptor-ai` marketplace is also added) | ✅ Available now |
| **Claude Desktop** (no terminal) | **+** next to the prompt box → **Plugins** → **Manage plugins** → **+ Add marketplace** → GitHub repository `BlackRaptorAI/blackraptor` → install **blackraptor-hardware** → restart the session | ✅ Available now |
| **Any program workspace, vendored** | copy `hw-engineering/agents/` into the workspace's `.claude/agents/` and `hw-engineering/CLAUDE.md` + `TEAM.md` + `docs/` + `templates/` into the workspace root | ✅ Available now |

## What's here

- **`hw-engineering/`** — the plugin:
  - **`agents/`** — the team:
    - the `hw-program` skill (main session) — the conductor: decision register, interfaces, dispatch, gates, handoffs; absorbs the system-architect role. It is a skill run by the human's main session, not an agent — it holds no seat, no gate, and no content authority
    - `power-electronics` (Opus) — power tree, protection, ride-through, rail margins
    - `thermal-mechanical` (Opus) — enclosure, fins, thermal simulation, sealing, materials
    - `rf-connectivity` (Opus) — antennas, modems, link budgets, cert-preserving RF config
    - `embedded-firmware` (Sonnet) — boot/secure boot, OTA/rollback, watchdog, storage, provisioning; checklist discipline
    - `reliability-dfr` (Opus) — DFMEA, derating audit, MTBF, failure economics
    - `compliance-cert` (Sonnet) — standards mapping, cert plan, design pre-checks; checklist discipline
    - `manufacturing-dfm` (Sonnet) — assembly, tolerances, test points, AVL, yield; checklist discipline
    - `cost-engineer` (Sonnet) — should-cost, landed cost, driver ranking, RFQ program; checklist discipline
    - `hw-design-reviewer` (Opus) — cross-cutting adversarial reviewer; not a seat, a gate
  - **`CLAUDE.md`** — the always-on operating standard, adapted for HW/firmware work (program workspaces copy or reference it)
  - **`skills/hw-operating-standard/`** — the same standard as an invocable skill, so plugin installs (Claude Code and Desktop) carry it too
  - **`TEAM.md`** — the roster, model tiers, cross-review matrix, review gates (PDR → bench characterization → CDR → MRR), and the Manufacturing Data Package the program ultimately delivers
  - **`templates/program-context.md`** — template for a program's `PROGRAM-CONTEXT.md`
  - **`docs/`** — the engineering-principles canon and the full general v2 standard behind every rule
- **`archive/superseded-agents/`** — retired definitions (`hw-architect`, `firmware-engineer`) absorbed into the seats above; kept outside the plugin path so they never load

## The core pattern

For anything that gates a board spin, tooling commitment, purchase, or external
commitment: **producer → hw-design-reviewer → revise**. Testing showed this
pairing outperforms any single agent, because self-review can't catch the
producer's own blind spots.

## Market grounding (the shared bridge)

The team auto-installs
[**blackraptor-core**](https://github.com/BlackRaptorAI/blackraptor/tree/main/core)
for the two checks engineering cannot referee for itself:
**`product-manager`** validates at requirement intake and PDR that the device's
makeup — feature set, design life, cost target — traces to market need and
willingness-to-pay, not engineering preference (the team's over-design doctrine
polices gold-plating against the requirements; product-manager polices the
requirements themselves), and **`evidence-auditor`** + the
**`research-integrity`** skill gate load-bearing external research claims
(component pricing, lead times, lifecycle/EOL, standards applicability) before
they harden into purchases or plans. Math and engineering verification stay
with `hw-design-reviewer` — the bridge validates market fit and research
claims, never physics.

Program flow: the `hw-program` skill (main session) reads the program's decision register +
newest handoff, dispatches the next seat with a brief, the seat delivers, the
register and interfaces are updated, and a HANDOFF file marks every pause
point. Gates sequence the program: PDR when all v0.1 drafts exist → bench
characterization clears PROVISIONAL flags → CDR freezes v1.0 → MRR signs it
buildable.

## Model tiering

Follows the rule: **Opus** for judgment-heavy
design and review seats — its failure mode is narrow under-verification, so the
verification loop stays mandatory; **Sonnet** for well-scoped seats with the
Excellence Pass items written as explicit, visibly-completed checklist steps —
it performs them at top-tier level when named, and skips them when not.

## Using it on a program

Each device program keeps its specifics (device, locked decisions, current
state, document paths) in a `PROGRAM-CONTEXT.md` in the program's engineering
folder — start from `hw-engineering/templates/program-context.md`. Every agent
reads the program context and decision register before starting work. One team,
any device.

## Extending

Add new agents in `hw-engineering/agents/<name>.md`. Each should: reference
CLAUDE.md, carry only the domain rules it needs, declare its model tier, and —
if Sonnet — list its Excellence Pass items as mandatory, visibly-completed
steps. Treat CLAUDE.md as living: when an agent produces a failure the standard
should have prevented, add the rule; when a rule proves dead weight, cut it.

## License

Apache-2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).
