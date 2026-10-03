# BlackRaptor Workforce

**Public. Issues and pull requests are open; see [CONTRIBUTING.md](CONTRIBUTING.md).** The invite-only alpha has ended; its notes stay in [docs/ALPHA.md](docs/ALPHA.md).

> **2.0.0 — breaking change.** Gate verdict blocks now use one schema: `confidence` is an integer 0–10
> (it was `high`/`medium`/`low`), a cited `standards[]` is required, and `N/A` is no longer a verdict —
> a Change Record carrying old-shape blocks fails validation until its blocks are re-emitted.
> Two engineering gates join the roster (`schema-reviewer`, `test-auditor`), and a Stop hook now
> validates verdict blocks as they are written (disable with `BR_VERDICT_HOOK=off`).
> Gates are strict by design: `CONCERNS` with conditions is the common verdict on sound work,
> and `PASS` is not the default.
> **Upgrading → [docs/UPDATING-YOUR-WORKFORCE.md](docs/UPDATING-YOUR-WORKFORCE.md).**

> **2.3.0.** Gate findings are one claim per row, with the sibling paths checked, a severity, the
> smallest fix and the check that proves it closed; every evidence line starts with how it was obtained.
> A new `/plan-review` command reviews a plan with a core set of reviewers and checks earlier findings
> for closure. `test-auditor` passes a test set only on a measured run. The Core hooks carry timeouts,
> are tested on every verify run, and all turn off with `BR_HOOKS=off`.
> **Upgrading → [docs/UPDATING-YOUR-WORKFORCE.md](docs/UPDATING-YOUR-WORKFORCE.md).**

> **2.2.1.** The Stop hook's block message no longer repeats a gate's name when the same turn is
> retried. Six agent and skill descriptions across the Core, Council, Engineering, and Hardware
> packs are shorter, with the same scope and behaviour.

> **2.2.0.** Agent and skill descriptions across the roster were rewritten to state scope more
> directly. Onboarding now fires once at session start instead of intercepting your first prompt;
> the one-shot claims-gate reminder hook is removed (its job is now carried directly in each
> producer's own instructions). The `gate-review` command no longer produces an invalid result when
> no gate applies to a change.
> **Details → [docs/UPDATING-YOUR-WORKFORCE.md](docs/UPDATING-YOUR-WORKFORCE.md).**

> **2.1.0.** `product-marketing` moved from the Engineering pack to the Marketing pack. The
> Marketing pack's DRAFT/GATED file convention is now mechanical — a `<name>.DRAFT.md` becomes
> `<name>.md` only once `claims-gate` has written a validating verdict, enforced by two hooks
> (kill switches `BR_CLAIMS_HOOK=off` and `BR_VERDICT_HOOK=off`). The verdict `Stop` hook now
> also waits for a gate seat still finishing in the background instead of treating it as missing.
> The Executive Council's orchestrator independently re-runs the decision-driving numbers a seat
> cites before the chair convenes, replacing seat-to-seat cross-review.
> **Details → [docs/UPDATING-YOUR-WORKFORCE.md](docs/UPDATING-YOUR-WORKFORCE.md).**

![agents](https://img.shields.io/badge/agents-63-6E56CF) ![skills](https://img.shields.io/badge/skills-29-6E56CF) ![packs](https://img.shields.io/badge/packs-5-6E56CF) ![license](https://img.shields.io/badge/license-Apache--2.0-blue)

**Specialist agent packs with read-only review gates: they judge the work and record a cited verdict, machine-checked as it is written.**

Five governed agent packs for Claude Code — Engineering, Executive Council, Marketing, Hardware Engineering, and a shared Core — that hold AI-assisted work to a professional standard through named review gates, cited standards, and machine-checkable verdicts. Agents advise, draft, and review; humans decide.

## Install

```
/plugin marketplace add BlackRaptorAI-Labs/BlackRaptor_Workforce
```

Installed from the old address? It still works; GitHub redirects. Update when convenient with `/plugin marketplace remove blackraptor` then the add line above.

Then install the packs you need (below). The **Core** pack auto-installs as a dependency of every team — you do not install it directly.

**How to update your installed packs → [docs/UPDATING-YOUR-WORKFORCE.md](docs/UPDATING-YOUR-WORKFORCE.md).**

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

## How to install, by situation

- **Just you (user scope).** The two commands above install at the user level — available in every repo you open. CLI installs also appear in Cowork automatically; no separate step there.
- **A whole team, standardized on one repo** — the way to standardize a team on one repo. Commit a `.claude/settings.json` so everyone who opens the repo gets the same packs:
  ```json
  {
    "extraKnownMarketplaces": {
      "blackraptor": { "source": { "source": "github", "repo": "BlackRaptorAI-Labs/BlackRaptor_Workforce" } }
    },
    "enabledPlugins": {
      "blackraptor-engineering@blackraptor": true,
      "blackraptor-council@blackraptor": true
    }
  }
  ```
  Each collaborator still installs under their own GitHub auth.
- **Vendored into a repo's `.claude/`** (no marketplace) — for the **Engineering and Marketing packs only**: run `./engineering/install.sh /path/to/repo` (and/or `./marketing/install.sh /path/to/repo`). Each appends one idempotent `@.claude/blackraptor-workforce.md` line to your `CLAUDE.md`; your existing content is preserved and both packs merge into that one file.

## The packs

| Pack | id | Agents | What it is |
|---|---|---|---|
| Engineering | `blackraptor-engineering` | 23 | Governed software-engineering team: architect, engineers, and blocking-gate reviewers (security, privacy, compliance, red-team) + the advisory completion-auditor. |
| Executive Council | `blackraptor-council` | 12 | Executive advisory council convened through a challenge protocol (sourced evidence, counter-case, voice-of-customer). |
| Marketing | `blackraptor-marketing` | 12 | Full-stack marketing department; producer agents are instructed to route external-facing copy to the isolated claims-gate agent, which you can also invoke explicitly on anything that ships. |
| Hardware Engineering | `blackraptor-hardware` | 9 | Hardware-engineering department + an adversarial design-review gate before any board spin, tooling, or purchase. |
| Core | `blackraptor-core` | 7 | Seven cross-cutting agents shared by every team — `product-manager`, `evidence-auditor`, `claims-gate`, `product-docs-writer`, and the market, pricing and competitive-intel analysts — plus the shared skills. Auto-installed with any team. |

**63 agents · 29 skills · 5 packs** across the marketplace.

## How it works

- **Read-only gates.** Reviewer agents (security, privacy, compliance, red-team, evidence, design-review, claims) hold read-only tools by design — they judge work, they don't rewrite it. A gate's job is to block, with a reason, until the work meets the bar.
- **Cited standards, dated.** Agents name the standard and edition they rely on and flag anything they could not verify against the primary source.
- **Machine-checkable verdicts.** Gate output is a structured verdict block; the Change Record captures the human decision that acts on it.
- **Humans decide.** No autonomous sends, posts, spend, or irreversible actions — agents draft and advise; a person approves.

## License

Apache-2.0. Each pack ships its own `LICENSE` and `NOTICE`; please keep the NOTICE and a link back to this repository with any copy or derivative.
