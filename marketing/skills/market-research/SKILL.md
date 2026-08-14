---
name: market-research
description: >
  This skill should be used when the user asks to "size the market", "research this market",
  "who buys this", "design a customer survey", "build an interview guide", "validate demand",
  "synthesize customer feedback", or "is there a market for X". It runs integrity-gated
  market research: bottom-up sizing, segmentation, voice-of-customer instruments, and
  demand validation with graded evidence.
metadata:
  version: "1.1.0"
---

# Market Research

## Purpose

Produce market truth the team can bet on: sized opportunities, ranked segments, and customer evidence — with the rigor to survive challenge. This is the input side of the marketing engine; the compliance-claims-gate is the output side.

## Process

### 1. Frame

Read the Marketing Intelligence Core (`${CLAUDE_PLUGIN_ROOT}/context/marketing-context.md`). State the decision this research serves and what answer would change it — research without a decision attached is a report, not research.

### 2. Choose the mode

- **Sizing** — bottom-up: population counts × qualification rates × reachable share × plausible price. Cite every count; show arithmetic; deliver a low/base/high range with the sensitivity drivers named.
- **Segmentation** — segment by compliance obligation, pain intensity, and reachability; score each segment on evidence strength; recommend a beachhead only when evidence supports it.
- **Voice-of-customer** — interview guides: open-ended, non-leading, past-behavior-over-intent questions; surveys: one construct per question, Van Westendorp block available for pricing work. Synthesis: pattern → supporting quotes → count of independent sources → confidence grade.
- **Demand validation** — design the cheapest honest falsification test; pre-register what result kills the hypothesis before running it.
- **Secondary sweep** — regulatory, competitive, and buyer-trend monitoring with source appraisal.

### 3. Grade the evidence

Every finding carries two grades: source reliability (primary data > independent research > trade press > vendor content, vendor flagged in-line) and evidence certainty (confirmed by multiple independent sources → single-source → inference). Check citation independence — shared upstream sources collapse into one.

### 4. Report

Deliver: the answer, the range, the evidence table with citations and retrieval dates, the assumptions block, what would change the conclusion, and the cheapest next test. Report contradicting evidence prominently.

## Reference methodology (read before designing instruments or channel plans)

- `references/questionnaire-methods.md` — Dillman survey design, sampling/bias controls, the pricing-research hierarchy (Van Westendorp → Gabor-Granger → MaxDiff → conjoint), Mom Test / JTBD / switch-interview methods, and the honest publishing/fielding workflow.
- `references/audience-channel-discovery.md` — Bullseye channel framework, watering-hole mapping with verification rules, channel scoring, and attributed reach frameworks (95:5, share of search, category entry points).

## Rules

- No statistic without a findable citation; no invented sources, ever.
- Distinguish "customers said" from "we infer" in every synthesis.
- Findings feed the core: validated statistics enter the cleared-claims list only via the compliance-claims-gate.
- When evidence is thin, the deliverable says so and prescribes the interview or test that fixes it — never papers over it.
