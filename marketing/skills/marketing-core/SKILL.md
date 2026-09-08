---
name: marketing-core
description: >
  This skill should be used when the user asks to "update the marketing context",
  "review our marketing core", "onboard the marketing team", "set up marketing context",
  or before ANY marketing agent in this plugin produces output. It loads and maintains
  the shared Marketing Intelligence Core that all marketing agents read first.
metadata:
  version: "1.1.0"
---

# Marketing Intelligence Core

## Purpose

The Marketing Intelligence Core is the hub of the marketing-team plugin. It prevents the fragmentation failure mode: a content agent that can't see analytics, an SEO agent that doesn't know brand voice, and a publishing agent with no strategic context each running confidently within an incomplete frame.

## Instructions

1. **Resolve the marketing context per the resolution order** (see the shared `mkt-context-resolution` include below) before any marketing work. The filled context lives at the project root so pack updates cannot touch it.

**Context resolution order (marketing).** Resolve your context in this order and stop at the first that exists: (1) `MARKETING-CONTEXT.md` at the project root — the onboarded, filled copy; if it is missing or still the template, invoke the `context-onboarding` skill before producing external-facing output; (2) an explicit path the user names; (3) never the in-pack `${CLAUDE_PLUGIN_ROOT}/context/marketing-context.md` — that is only the blank template (first line `<!-- TEMPLATE — not onboarded -->`), never the live copy, and a pack update overwrites it. Full detail: `marketing-core` skill.

2. **If the project-root file is missing or still the template, invoke the shared `context-onboarding` skill first**, then read its result. That interview uses the marketing question set in `references/context-questions.md` (company/product, brand architecture, personas in priority order, GTM, voice, competitors, proof standards, ethics guardrails) and writes the approved, dated context to the project root — never into the pack.
3. When any marketing agent produces output that contradicts the context, the context wins. Flag the contradiction to the user rather than silently proceeding.
4. When new truth arrives (audited proof point, pricing change, new persona), do not silently rewrite: propose a diff to the context file, apply on approval, and re-date-stamp — the update-on-approval rule the `context-onboarding` skill defines for every context file.
5. Never remove or weaken the §6 hard gates without an explicit user instruction, and restate the risk when asked to.

## Maintenance cadence

Prompt the user to review the core whenever: a campaign launches, a quarter closes, positioning is debated, or 90 days pass without an edit.
