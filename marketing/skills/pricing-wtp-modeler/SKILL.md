---
name: pricing-wtp-modeler
description: >
  This skill should be used when the user asks to "model willingness to pay", "price this
  product", "design pricing tiers", "model MSP wholesale pricing", "run a pricing scenario",
  or "what should we charge". It models per-endpoint SaaS pricing for regulated verticals,
  MSP wholesale discount structures, compliance-tier upsells, and willingness-to-pay by
  persona — grounded in cited comparables, never invented numbers.
metadata:
  version: "1.1.0"
---

# Pricing Strategy & Willingness-to-Pay Modeler

## Purpose

Pricing is the highest-leverage, most under-owned lever in most companies. This skill produces decision-ready pricing analysis for a regulated-vertical B2B SaaS with a two-surface GTM (direct + MSP wholesale).

## Process

### 1. Ground truth

Read the Marketing Intelligence Core. Confirm the price metric candidates (per endpoint, per seat, per site, flat tier), the personas, and the two-surface structure. Pull current COGS assumptions from the user or existing models — never invent them.

### 2. Comparable landscape

Research published pricing for named competitors and adjacent categories. Cite every figure with its source and retrieval date; flag list-vs-street price uncertainty. Where pricing is unpublished, say so — do not estimate silently.

### 3. Willingness-to-pay by persona

For each persona, model WTP from: the cost of the compliance obligation they're solving (fines, audit costs, breach costs — cited), the cost of alternatives (staff time, incumbent tools), and any voice-of-customer evidence available. Label every WTP figure as an evidence-based estimate with its confidence level. Recommend a Van Westendorp or direct WTP survey when evidence is thin, and provide the question set.

### 4. Structure design

Design 2–3 candidate structures, each specifying: price metric, tier ladder and fence logic (what forces an upgrade), compliance-tier upsell placement, direct list price, MSP wholesale discount and margin math per endpoint, and floor price derived from COGS + target gross margin. Show the arithmetic.

### 5. Scenario model

Build a simple model (spreadsheet when useful): revenue and gross margin at low/base/high adoption for each structure, direct vs. MSP mix sensitivity, and the break-even endpoint count. State every assumption in an assumptions block.

### 6. Recommendation

Recommend one structure with the reasoning, the top 2 risks, and the cheapest experiment that would de-risk it (e.g., a 10-prospect WTP interview script, included).

## Rules

- No invented statistics; every market figure carries a citation or an explicit "assumption" label.
- Discounting policy is part of pricing — always include a maximum-discount guardrail and who can approve exceptions.
- Check pricing claims and comparisons through the compliance-claims-gate before any external use.
