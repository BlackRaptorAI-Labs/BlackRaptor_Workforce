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

1. Read `${CLAUDE_PLUGIN_ROOT}/context/marketing-context.md` in full before any marketing work.
2. If the file's placeholder values do not match the user's actual company, run an onboarding interview: company/product, brand architecture, personas in priority order, GTM structure, voice standards, competitors, proof standards, and ethics guardrails. Rewrite the file with the answers.
3. When any marketing agent produces output that contradicts the core, the core wins. Flag the contradiction to the user rather than silently proceeding.
4. When new truth arrives (audited proof point, pricing change, new persona), update the file and date-stamp the edit.
5. Never remove or weaken the §6 hard gates without an explicit user instruction, and restate the risk when asked to.

## Maintenance cadence

Prompt the user to review the core whenever: a campaign launches, a quarter closes, positioning is debated, or 90 days pass without an edit.
