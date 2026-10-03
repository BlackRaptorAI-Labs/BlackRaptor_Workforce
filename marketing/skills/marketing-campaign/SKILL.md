---
name: marketing-campaign
description: Orchestrate a multi-agent marketing campaign end-to-end — strategy, copy, creative, channels, and measurement into one coherent launch. Use when the user wants a full campaign built ("run the PTIN-renewal campaign", "build the launch"), not a single asset. Every external-facing asset MUST pass the claims gate before it can be produced.
---

# Run a marketing campaign

Coordinate the marketing specialists into one coherent launch. **This skill runs in the
main session, which dispatches each specialist as its own subagent** — there is no
orchestrator subagent (P1/P2). Its non-negotiable is the **claims gate**: nothing goes
external without it in the trace.

**Delegation policy:** when a task matches a specialist's domain, delegate rather than self-perform.

**At campaign start**, write a `.br-assets` marker file into the campaign's asset directory (create
the directory if it does not exist) — this is what tells the core PreToolUse and Stop hooks that the
DRAFT/GATED convention (`compliance-claims-gate` skill) applies to writes under it.

## 1. When to convene

A full campaign or launch spanning multiple assets/channels — not a single blog post
(hand that straight to the copywriter). A single asset is still *subject to the gate rule*:
the always-on rule rides the core
`compliance-claims-gate` skill and each producer's description. Measured limit (SPEC §2 P11):
outside this skill's mandatory dispatch step, isolated single-asset dispatch to the separate
`claims-gate` agent is best-effort (P3 dispatched 0/3 — the model tends to self-review), so
**this skill is the one guaranteed path** — it is for orchestrating the multi-asset case, not
for granting single assets an exemption. Ground first in the **Marketing Intelligence Core**
(`marketing-core` skill): audience, positioning, proof standards.

## 2. Seat selection rule

Select by campaign shape: `brand-architect`/`content-strategist` for the narrative,
`copywriter`/`creative-director`/`video-creative-producer` for assets, `paid-media-manager`/
`seo-geo-engineer`/`social-community-manager`/`email-outbound-sequencer` for channels,
`analytics-attribution-engineer` for measurement. Always include the **claims gate** as a
mandatory reviewer of every external asset.

## 3. Dispatch instruction

**In a SINGLE message, spawn the independent producers as separate subagents** (Agent
tool) so strategy/copy/creative/channel work runs concurrently once the narrative is set.
Sequence only the real dependency: narrative → assets → channel plan → measurement.

## 4. Context each specialist receives (and must NOT receive)

Each producer gets: the approved narrative/positioning, its specific asset brief, and the
proof standards. A producer must **NOT** gate its own output — the claims review is a
separate dispatch in a fresh context (P5). Give the claims reviewer the finished asset +
the proof standard, not the producer's rationale.

## 5. Synthesis rule

Assemble the campaign as one coherent whole; surface where channel/measurement seats
disagree on approach and why. Preserve the measurement seat's dissent on any claim it
cannot yet substantiate.

**DRAFT/GATED file convention.** Every producer this skill dispatches writes its asset as
`<name>.DRAFT.md`, never `<name>.md` directly — the rule and its two mechanical controls (a
PreToolUse write guard and a Stop-hook check) are stated once in the `compliance-claims-gate` skill.

## 6. Closing gate — CLAIMS GATE (MANDATORY)

**No external-facing asset may be produced without the claims gate in its trace.** The
mandatory step **dispatches the `claims-gate` agent** (a separate subagent, isolated context —
it did NOT write the copy, per P5) on every asset before delivery; it decomposes the asset into
claims and returns a per-claim substantiated/FIX/BLOCK verdict + overall SHIP/HOLD, and enforces
the retired-claims ban. A producer running the `compliance-claims-gate` **skill** on its own
output is self-review, not a gate — always route to the **agent**. **Enforcement category today:
Checklist-only** — the mandatory step is an agent dispatch the campaign is instructed to make,
**not yet mechanically blocking** (marketing assets have no stable CODEOWNERS/CI paths in this repo;
see 5.7b). Stated honestly, not overclaimed. **With the `blackraptor-dev` (Build) pack installed**,
`completion-auditor` confirms `claims-gate` is in the trace before ship; **otherwise the main session
performs that trace check itself and records it UNVERIFIED-by-gate** (§9.3 — degrade, don't dangle) —
but never ships an asset the claims gate has not cleared regardless.

## 7. Degradation (pack absent)

If the marketing pack or the claims gate is unavailable, **do not publish** — mark the
asset UNVERIFIED and stop. An external claim without the gate is never shipped on a
"degrade gracefully" rationale (§9.3); here the degradation is: hold, do not ship.
