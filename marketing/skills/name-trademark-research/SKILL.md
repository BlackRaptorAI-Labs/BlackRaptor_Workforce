---
name: name-trademark-research
description: >
  This skill should be used when the user asks to "name a product", "check a name for
  trademark conflicts", "generate name candidates", "run a USPTO sweep", "validate this
  brand name", or "score these name candidates". It runs a research-integrity-gated
  naming process: compound name generation, trademark and domain conflict sweeps,
  conflict scoring, and a decision-ready handoff document.
metadata:
  version: "1.1.0"
---

# Name & Trademark Research

## Purpose

Generate and validate names with the same rigor a trademark paralegal would apply on a first-pass screen — while being explicit that this is research support, not legal advice.

## Process

### 1. Brief

Read the Marketing Intelligence Core (`${CLAUDE_PLUGIN_ROOT}/context/marketing-context.md`) first. Confirm: what is being named (company, product, feature, agent), the parent brand architecture, target buyer, and any naming constraints (tone, length, must-avoid words).

### 2. Generate

Produce 20–40 candidates across at least four construction strategies: descriptor + base-word compounds (the BlackRaptor formula), truncated/blended compounds, evocative real words, and coined words (e.g., -ium constructions). Draw on multi-language guardian/protector/watcher word families where the brief fits. For each, note the semantic logic. Kill candidates that collide with §6 guardrails (e.g., names implying certification or compliance conferral).

### 3. Sweep (per surviving candidate)

Run web searches for each of the following, and record what was actually found — never assume a clear result without a search:

- **USPTO trademark records** — search Justia trademarks (`trademarks.justia.com`) and USPTO TESS-equivalent public search for exact and close-variant marks; record class numbers, live/dead status, and owner.
- **Common-law use** — general web + app stores + GitHub + Product Hunt for active products using the name in adjacent classes.
- **Domains** — .com/.ai/.io availability signals (registrar search pages or live-site checks).
- **Social handles** — X, LinkedIn availability signals where checkable.
- **Linguistic hazards** — unintended meanings in major languages, awkward pronunciations, negative acronyms.

### 4. Score

Score each candidate 0–5 on: trademark conflict risk (inverted), common-law crowding (inverted), domain feasibility, distinctiveness, fit-to-brief. Show the evidence behind every score — a score without a recorded search result is invalid.

### 5. Handoff document

Deliver a decision document containing: top 3–5 candidates ranked, full conflict table with links to every record found, kill list with reasons, open risks, and a plainly stated limitation block: *"This is a first-pass research screen, not a legal clearance opinion. Engage a trademark attorney before filing or launch."*

## Integrity rules

- Never state "no conflicts found" without listing the searches actually run.
- Distinguish dead marks from live marks; a dead mark is a lower risk, not zero risk.
- Same-name marks in unrelated classes are recorded, not silently dropped.
- If search tooling fails for a candidate, mark it UNSWEPT — never let it appear cleared.
