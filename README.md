# BlackRaptor Workforce

![agents](https://img.shields.io/badge/agents-58-6E56CF) ![skills](https://img.shields.io/badge/skills-26-6E56CF) ![packs](https://img.shields.io/badge/packs-5-6E56CF) ![license](https://img.shields.io/badge/license-Apache--2.0-blue)

**Specialist agent packs with read-only review gates that block work until it meets the standard.**

Five governed agent packs for Claude Code — Engineering, Executive Council, Marketing, Hardware Engineering, and a shared Core — that hold AI-assisted work to a professional standard through named review gates, cited standards, and machine-checkable verdicts. Agents advise, draft, and review; humans decide.

## Install

```
/plugin marketplace add BlackRaptorAI/blackraptor
```

Then install the packs you need (below). The **Core** pack auto-installs as a dependency of every team — you do not install it directly.

## Starter recipe

Most people start here:

- **`blackraptor-engineering`** — the software-engineering team (architecture, implementation, and blocking review gates).
- **`blackraptor-council`** — the executive advisory council for company/strategy decisions.

Installing either one pulls in **`blackraptor-core`** automatically. Then add, when the need arrives:

- **`blackraptor-marketing`** — when you start publishing (every external claim routes through a compliance gate).
- **`blackraptor-hardware`** — when you build physical devices.

```
/plugin install blackraptor-engineering@blackraptor
/plugin install blackraptor-council@blackraptor
```

## The packs

| Pack | id | Agents | What it is |
|---|---|---|---|
| Engineering | `blackraptor-engineering` | 22 | Governed software-engineering team: architect, engineers, and blocking-gate reviewers (security, privacy, compliance, red-team) + the advisory completion-auditor. |
| Executive Council | `blackraptor-council` | 10 | Executive advisory council convened through a challenge protocol (sourced evidence, counter-case, voice-of-customer). |
| Marketing | `blackraptor-marketing` | 15 | Full-stack marketing department; every external-facing claim is routed to a separate claims-gate agent for review. |
| Hardware Engineering | `blackraptor-hardware` | 9 | Hardware-engineering department + an adversarial design-review gate before any board spin, tooling, or purchase. |
| Core | `blackraptor-core` | 2 | Shared `product-manager` + `evidence-auditor` and the `research-integrity` skill. Auto-installed with any team. |

**58 agents · 26 skills · 5 packs** across the marketplace.

## How it works

- **Read-only gates.** Reviewer agents (security, privacy, compliance, red-team, evidence, design-review, claims) hold read-only tools by design — they judge work, they don't rewrite it. A gate's job is to block, with a reason, until the work meets the bar.
- **Cited standards, dated.** Agents name the standard and edition they rely on and flag anything they could not verify against the primary source.
- **Machine-checkable verdicts.** Gate output is a structured verdict block; the Change Record captures the human decision that acts on it.
- **Humans decide.** No autonomous sends, posts, spend, or irreversible actions — agents draft and advise; a person approves.

## License

Apache-2.0. Each pack ships its own `LICENSE` and `NOTICE`; please keep the NOTICE and a link back to this repository with any copy or derivative.
