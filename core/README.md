# BlackRaptor Workforce — Shared Bridge

**`blackraptor-core`** holds the **cross-cutting** agents and skills that belong to
*both* the development team and the executive council — the roles where the work
spans the market/strategy side and the build/delivery side. It is **auto-installed
as a dependency** of `blackraptor-engineering` and `blackraptor-council`, so you never
install it directly: adopt either team and the bridge comes with it. (`claude plugin
prune` removes it if you later uninstall both teams.)

## What's in it

| Component | Kind | Why it's shared |
|---|---|---|
| **`product-manager`** | agent (`sonnet`) | The end-to-end product owner — from *what to build and why it wins* (outcome thesis, JTBD, target customer, scope) through *the buildable definition* (user stories, acceptance criteria, success metrics, sequencing). It sits across the council (market demand) and engineering (delivery) and exists to keep the build matched to the market. |
| **`evidence-auditor`** | agent (`opus`) | The adversarial gate for research, analysis, and evidence-based reporting. Central to the council (every recommendation rests on evidence) and the HEAVY-tier escalation for engineering's load-bearing claims (root-cause, perf/scale, vendor/tech selection). |
| **`research-integrity`** | skill | The three-mode research methodology `evidence-auditor` reviews the output of — tiered LITE / STANDARD / HEAVY, so light engineering research and heavy council research use the same engine at the right depth. |

## Why a bridge, not duplication
`red-team-reviewer` is genuinely engineering-only; council seats are genuinely
council-only. These three are not — forcing them into one team would either deny the
other team a capability it needs or duplicate a file that then drifts. A shared
dependency keeps **one** source of truth that both teams pull in.
