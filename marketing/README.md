# BlackRaptor Workforce — Marketing Team

A governed, full-stack **marketing department** for Claude: **11 specialist agents + 7 marketing skills** (the shared Core skills — contract, gates, onboarding, content-craft, the claims gate — install with the `blackraptor-core` dependency), hub-and-spoke around a shared **Marketing
Intelligence Core** context file that every agent reads before acting. Built by
[BlackRaptor AI](https://github.com/BlackRaptorAI) as the marketing sibling of
[blackraptor](https://github.com/BlackRaptorAI/blackraptor) (the
development team + executive advisory council), and held to the same operating
standard: **agents advise and draft — humans decide, approve, and send.**

Every charter carries the BlackRaptor **customer-experience north star** (the
customer must need it, find it easy, and get exactly what they were promised —
trust, loyalty, and willingness to spend are the measures) and the
**excellence-pass** output-quality discipline (never ship a first draft). Each
role is written as a 20+-year practitioner and encodes named,
verifiable methodology — Dillman survey design, Kohavi trustworthy
experimentation, IPA/Binet & Field creative effectiveness, Ehrenberg-Bass
distinctive assets, Made to Stick / Ogilvy / NN-g writing craft — cited, not
invented.

## Install

| Where | How | Status |
|---|---|---|
| **Claude Code — recommended** | `claude plugin marketplace add BlackRaptorAI/blackraptor` then `claude plugin install blackraptor-marketing@blackraptor-ai` — installing from the main marketplace auto-pulls **blackraptor-core** (evidence-auditor + research-integrity + product-manager) | ✅ Available now |
| **Claude Code — this repo directly** | `claude plugin marketplace add BlackRaptorAI/blackraptor` then `claude plugin install blackraptor-marketing` (bridge auto-installs only if the `blackraptor-ai` marketplace is also added) | ✅ Available now |
| **Claude Desktop** (no terminal) | **+** next to the prompt box → **Plugins** → **Manage plugins** → **+ Add marketplace** → GitHub repository `BlackRaptorAI/blackraptor` → install **blackraptor-marketing** (bridge comes automatically) → restart the session | ✅ Available now |
| **Any repo, vendored** | `./install.sh <target-repo>` copies agents + skills into the repo's `.claude/` | ✅ Available now |
| **Claude Cowork** (individual, claude.ai) | via Anthropic's official plugin catalog | ⏳ Pending curation — Cowork has no self-serve marketplace yet |
| **Claude Cowork** (organization) | your org admin provisions it centrally (managed plugins) | ✅ Available to org admins now |
| **Claude Cowork** (manual, today) | open **Customize → Skills** and upload a skill's `SKILL.md` from [`marketing/skills/`](marketing/skills/) (upload any bundled `templates/`/`references/` alongside it) | ✅ Available now |

> **No one-click install link exists yet** — that arrives with Anthropic's
> official plugin directory ([claude.com/plugins](https://claude.com/plugins))
> once curation lands; until then use the Desktop GUI steps or the CLI commands
> above.

> **Note on Cowork:** Cowork is skills-centric and has no sub-agent concept, so
> the **skills** work there (upload a `SKILL.md` from [`marketing/skills/`](marketing/skills/))
> while the 15-agent roster and the `marketing-campaign` skill's orchestration are a
> **Claude Code** capability.

## The team

**Agents (15)**, orchestrated by the main-session `marketing-campaign` skill —
`brand-architect` · `name-trademark-researcher` · `market-research-analyst` ·
`content-strategist` · `copywriter` · `creative-director` · `seo-geo-engineer` ·
`paid-media-manager` · `social-community-manager` · `email-outbound-sequencer` ·
`video-creative-producer` · `competitive-intel-analyst` ·
`pricing-strategy-analyst` · `analytics-attribution-engineer` · `claims-gate`

**Skills (9)**

- `marketing-core` — loads/maintains the Marketing Intelligence Core; runs the
  onboarding interview that configures the team for **your** product
- `compliance-claims-gate` — per-claim PASS/FIX/BLOCK screening for regulated
  marketing (efficacy, certification language, statistics, CAN-SPAM/TCPA,
  disclosures); every external asset passes through it
- `name-trademark-research` — compound name generation + USPTO/Justia/common-law
  conflict sweeps with evidence-backed scoring
- `market-research` — integrity-gated sizing, segmentation, voice-of-customer,
  and demand validation (Dillman, Van Westendorp→conjoint hierarchy, Mom
  Test/JTBD, Bullseye channel discovery)
- `experimentation` — trustworthy A/B testing per Kohavi et al.: pre-registration,
  power analysis, SRM/peeking checks, low-traffic B2B alternatives
- `competitive-intel` — competitor weakness mining from verifiable public
  sources + win/loss methodology
- `pricing-wtp-modeler` — pricing structures, willingness-to-pay by persona,
  wholesale/channel discount and tier modeling
- `content-craft` — craft standards for creative writing, technical writing, and
  visual/video creation
- `excellence-pass` — the five behaviors separating top-tier output from
  merely-correct, run as the final pass on every deliverable

## Research rigor — shared with the whole BlackRaptor system

The `market-research` skill embeds the integrity baseline (source × evidence
grading, citation independence, retrieval dates, no uncited statistics). For
heavy-tier validation the team depends on the shared **blackraptor-core**
plugin: the **evidence-auditor** agent (independent adversarial gate over any
research, sizing, or claim a decision rests on), the full **research-integrity**
skill (3-mode methodology + release gate), and **product-manager** (the
outcome-thesis owner marketing positions against). Install via the main
marketplace and the bridge comes automatically — the marketing team is audited
by the same gate as the development team and the executive council.

## Why hub-and-spoke

Adding AI agents to a fragmented marketing stack amplifies the fragmentation: a
content agent that can't see analytics, an SEO agent that doesn't know brand
voice, and a publishing agent with no strategic context each run confidently
within an incomplete frame. Here, one file — `context/marketing-context.md` —
holds personas, phasing, voice, approved claims, and hard ethics gates. Every
agent reads it first; external-facing claims are routed to the separate
`claims-gate` **agent** for review. That review is **guaranteed** on the
`marketing-campaign` workflow's mandatory dispatch step; for ad-hoc single
assets it is **best-effort** (an always-on rule on the plugin's hook + the
`compliance-claims-gate` skill + producer descriptions), not an automatic
screen of everything.

## Hard rules baked in

No autonomous sends, posts, or spend — agents draft, **humans approve**. No
efficacy claims without audited proof. No certification-conferral language. No
uncited statistics. No fake testimonials or AI-generated people presented as
real. Conflicts of interest disclosed.

## Setup

1. Install the plugin (table above).
2. Say **"set up the marketing context"** — the `marketing-core` skill
   interviews you and writes `context/marketing-context.md` for your product
   (it ships as a blank template).
3. Optionally connect live-data MCPs (analytics, search console, ad platforms) —
   the analytics and SEO agents use them when present.
4. Ask for any marketing job in plain language: "build the Q4 editorial
   calendar", "check this copy", "name the new module", "model our pricing",
   "run the full campaign build".

## Provenance & governance

Golden source: the private BlackRaptor golden agents repository; this public
repo is the released copy — improvements flow back via governed PRs. Marked
**Marketing Team** in every charter to differentiate from the development team
and council rosters. Methodology reference files cite named published sources
(Dillman; Kohavi, Tang & Xu; Binet & Field; Romaniuk/Ehrenberg-Bass;
Fitzpatrick; Weinberg & Mares; Heath; Ogilvy; Nielsen Norman Group) — keep the
attributions intact; they are the point.

## License

Apache-2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).
