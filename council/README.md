# The Executive Advisory Council

**A tough, evidence-driven team of AI advisor agents that helps you build
the right company.**

Created by [Tom Hanks](https://tomhanks.pro) (BlackRaptor AI) ·
Battle-tested building a real operating company · Contact: **GitHub issues and
discussions only**

Ten advisor seats — market insight, pricing, finance,
go-to-market, revenue, growth, technology & data, people, ethics & legal,
fundraising — convened by the main-session `council` skill that challenges every input
before it reaches you. The Council argues in front of you and hands you
decision-ready views with the disagreement preserved. **You decide; it
advises.** Read [VISION.md](VISION.md) for why this exists and what makes
it different.

## What's in the box

```
council/
├── COUNCIL.md              # The charter — binding rules for every seat
├── VISION.md               # Why this exists, strengths, intended use
├── agents/                 # 10 advisor seats (the product anchor now ships in the shared bridge)
│   │                       # The convener + challenge protocol is the main-session `council` skill — start there (no orchestrator agent)
│   ├── market-insight.md         # Market truth + customer ground truth
│   ├── pricing-strategy.md       # Packaging, pricing, offer economics
│   ├── finance.md                # Unit economics, capital, "is it worth it"
│   ├── ethics-governance.md      # Ethics, governance & legal counsel (can BLOCK)
│   ├── gtm-strategy.md           # Positioning, story, channels, sales motion
│   ├── revenue.md                # GTM execution, the number (CRO)
│   ├── growth-engine.md          # Demand execution (the only executor; HITL-gated)
│   ├── technology-strategy.md    # Business tech + data truth-finding
│   ├── people-org.md             # Hiring, org design, culture
│   └── fundraising-ir.md         # Raising capital + investor relations
├── templates/
│   ├── definition-brief.md       # The handoff artifact to your dev team
│   └── business-context.md       # REQUIRED grounding — fill this in first
├── skills/
│   └── council/SKILL.md    # The /council skill — "convene the council" runs the whole protocol
└── docs/
    └── PORTING.md          # Running the Council outside Claude Code
```

> **The product anchor + evidence gate ship in the shared bridge.** `product-manager`
> (the merged product-strategy + delivery role) and `evidence-auditor` (the council's
> evidence gate) live in the **`blackraptor-core`** plugin, which is **auto-installed**
> alongside this council. The main-session `council` skill convenes `product-manager` as the
> product/strategy anchor exactly as before — it just isn't a council-only file.

## Quickstart (Claude Code / Cowork)

1. Copy `agents/*.md` into your project's `.claude/agents/` directory.
2. Copy `COUNCIL.md` and `templates/` into your project root.
3. **Fill in `BUSINESS-CONTEXT.md`** from `templates/business-context.md`.
   This is not optional — a council that doesn't know your company gives
   conventional wisdom, and the `council` skill refuses to convene without it.
4. Ask: *"Convene the council on ..."* — the main-session `council` skill selects seats,
   enforces the challenge protocol, and returns a decision-ready view.

> **Installed via the plugin marketplace?** The `council` skill ships with it, so
> you can just say *"convene the council"* — the reliable trigger (skills activate
> from their description, so no exact command is needed). Where your Claude Code
> surfaces plugin skills as slash commands, `/council` works too (use the namespaced
> `blackraptor-council:council` if a bare `/council` ever collides). It grounds itself
> in `BUSINESS-CONTEXT.md` and runs steps 3–4 for you. Manual copy (above) still works
> if you're not using the plugin.

## Start lean — don't activate all ten

Add seats as your company earns them (`COUNCIL.md` §5). Start with the
core four (product, market, pricing, finance) and
ethics-governance — the main-session `council` skill convenes them. A council of ten consulted on "do ten customers want
this?" is theater. Copy only the agent files for active seats if you want
the discipline enforced by absence.

## What makes this different

- **No sycophancy, structurally.** Independent parallel drafts, anonymized
  cross-review, a challenge protocol every input must survive, and
  adversarial mode for consequential calls. Not "be critical" as a vibe —
  mechanisms.
- **Balanced evidence, always.** Confidence labels on claims, steelman
  for/against, a mandatory "What You Lose" cost in every recommendation,
  and dissent preserved on the record.
- **Customer-focused by charter.** Every seat optimizes for customer experience and loyalty — checked against real voice-of-customer
  evidence, never an imagined customer.
- **A human decides.** Consequential calls carry a human signature. The
  one executing seat (growth-engine) runs behind human-in-the-loop
  approval and ethics review.

## Model assignments (tiered by decision stakes)

Each agent's frontmatter assigns the Claude model best suited to its seat.
The council tiers by **decision stakes** — how expensive a subtle
reasoning failure is, and how reversible the resulting decision — not by
task volume:

| Tier | Seats | Why |
|---|---|---|
| **Opus** | `finance`, `ethics-governance`, `fundraising-ir` | Highest judgment stakes: finance owns capital allocation and downside math; ethics-governance holds legal judgment and BLOCK authority; fundraising-ir analyzes terms where a missed nuance costs equity. (Convening/synthesis is the main-session `council` skill — run by the human's `opus`-class session, not a seat with a `model:` of its own — where a subtle failure would corrupt everything downstream.) |
| **Sonnet** | `market-insight`, `pricing-strategy`, `gtm-strategy`, `revenue`, `growth-engine`, `technology-strategy`, `people-org` | Analysis and strategy seats: strong reasoning over sources and frameworks, invoked frequently, cost-efficient. |

> `product-manager` (the product anchor) and `evidence-auditor` (the evidence gate)
> run at `sonnet` and `opus` respectively but live in the shared **`blackraptor-core`**
> plugin, auto-installed with this council — so their tiering is documented there.

There is deliberately no cheaper volume tier: every council output is
advice a CEO may act on, so the quality floor is uniform. Assignments are
coaching records — if a seat under-reasons in practice, promote it (one
line in its frontmatter). Ports should preserve the tiering with their
vendor's equivalents (see [docs/PORTING.md](docs/PORTING.md)).

## Requirements & platforms

The Council's potency comes from its mechanics (independent drafts,
anonymized review, challenge protocol), which require an **agent runtime**
— Claude Code or Cowork natively, or a faithful port (OpenAI Agents SDK,
CrewAI, LangGraph): see [docs/PORTING.md](docs/PORTING.md). **There is
deliberately no single-prompt "chat mode"** — one chat window cannot keep
five advisors honestly independent, and we don't ship degraded versions.

## Honest limits

An AI council models the world; it is not the world. It gives you rigor,
structure, memory, and tireless challenge — genuinely valuable and rare —
but internal coherence is not external truth. Use it to think harder and
decide better, then go get ground truth: real customers, real dollars,
real market signal. The agents are not lawyers, accountants, or investment
advisors, and they will tell you when licensed professionals are required.

## Companion project: development-team-agents

The Council answers *"are we building the right company?"* Its companion,
**[BlackRaptor Workforce — development](https://github.com/BlackRaptorAI/blackraptor/tree/main/engineering)**,
answers the question downstream of it: *"are we building the thing right?"*
— a governed AI development team (architect, engineers, security,
compliance, QA, and blocking review gates) battle-tested on production
energy-monitoring infrastructure.

The two teams connect through one artifact: the Council's signed
**Definition Brief** (`templates/definition-brief.md`) is the input the
development team builds against. Same operating philosophy (advise →
decide → enforce, preserved dissent, a human signs), same license, same
authors. Run both and you have the full loop: decide what and why, then
build it right.

## Contributing & contact

Improvements welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Keep the
attribution (NOTICE) and a link back to this repository with any copy,
port, or derivative. **All contact is through GitHub** — issues for bugs
and gaps, discussions for ideas and results. No other channel is
monitored.

## License

Released under the Apache License 2.0 (see [LICENSE](LICENSE)) — the same
license as our development-team-agents companion. Use it, adapt it, build
on it, commercially or not; the [NOTICE](NOTICE) attribution travels with
every copy, port, and derivative.
