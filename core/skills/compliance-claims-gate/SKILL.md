---
name: compliance-claims-gate
description: >
  This skill should be used when the user asks to "check this copy", "run the claims gate",
  "is this claim safe to publish", "compliance-check this marketing", or before ANY
  external-facing marketing OR sales copy is delivered — from this plugin OR from any
  third-party marketing/sales tool, which may not include a claims gate of its own.
  It screens marketing claims against the proof standards and ethics guardrails in the
  Marketing Intelligence Core and returns pass/fix/block verdicts per claim. This is the
  METHOD; the isolated gate is the separate `claims-gate` AGENT that runs it in a context
  that did not write the copy — dispatch that agent, do NOT run this skill on copy the
  current context authored (that is self-review, not a gate).
metadata:
  version: "1.1.0"
---

# Compliance-Gated Claims Engine

## The gate is the isolated `claims-gate` AGENT — not self-review (A1)

This skill is the **method**. The **gate** is the separate **`claims-gate` agent**, which runs this
method in a context that has **not** seen the copy's author reasoning (P5). The mandatory routing rule —
*every external-facing marketing asset is dispatched to the `claims-gate` agent before delivery* — is
carried on loaded surfaces (this skill; the marketing plugin's `UserPromptSubmit` hook; each producer's
description) because a plugin-root `CLAUDE.md` carrier does **not** load on a marketplace install (measured;
SPEC §2 P11). **Do NOT run this skill on copy the current context wrote** — that is self-review, which the
gate exists to prevent; dispatch the `claims-gate` agent instead. Guaranteed isolated dispatch is the
`marketing-campaign` skill's mandatory step; for an ad-hoc single asset, dispatch the `claims-gate` agent
and, if you cannot, say so and do not present the copy as gate-cleared.

## Mandatory scope (R35 — safety gate)

This gate is **mandatory, not optional**, and it is **source-agnostic**: every external-facing
marketing or sales artifact — ad copy, email/drip sequences, landing pages, decks, one-pagers —
must pass it before delivery, **including output produced by third-party plugins** — many
marketing/sales tools generate customer-facing copy (email sequences, landing pages, assets)
with no CAN-SPAM line and no claims gate of their own.
Those tools do not gate themselves; this skill is the gate. Under uncertainty the default is
**BLOCK**, and you may never rewrite a blocked claim into a technically-true version that
preserves the misleading implication. Check CAN-SPAM / TCPA / FTC endorsement guides by channel.

## Purpose

Every external-facing sentence is a potential regulatory, legal, or trust liability. This gate is the wrapper all other marketing skills pass through before copy ships. It exists because no published marketing skill has a built-in compliance gate for regulated B2B claims.

## Process

1. Read the Proof Standards & Ethics Guardrails from the marketing context (resolution order: the
   project-root `MARKETING-CONTEXT.md`; else the marketing pack's Marketing Intelligence Core). The
   proof standards / claims ledger remain marketing's — this core gate reads them, it does not own them.
2. Decompose the copy into individual claims — every factual assertion, statistic, comparative, superlative, and implied promise.
3. Classify each claim:
   - **Efficacy claim** — requires audited, citable data. Block if none exists.
   - **Compliance-conferral language** — "certified", "compliant", "guarantees compliance", "audit-proof". Block; suggest supports-obligations phrasing.
   - **Statistic** — require a findable, citable source. Vendor figures must be flagged in-copy as vendor figures. Fix or block.
   - **Competitor comparison** — must be substantiatable and current; check battle-card freshness. Fix or block.
   - **Puffery** — subjective, non-measurable ("world-class support"). Pass but flag if it borders on measurable.
   - **Testimonial/endorsement** — verify consent and FTC endorsement-guide disclosure. Block without both.
   - **Conflict of interest** — affiliate or partner relationships must be disclosed in-body. Fix.
4. Check channel-specific law: CAN-SPAM for email (identification, opt-out, physical address), TCPA for SMS/calls, FTC endorsement guides for influencer/UGC-style content.
5. Return a verdict table: claim → classification → verdict (PASS = publish · CONCERNS = fix per the suggested rewrite, then publish · FAIL = block, with reason) → evidence required to unblock.

## Rules

- Default to BLOCK when uncertain; a delayed claim costs less than a retracted one.
- Never rewrite a blocked claim into a technically-true version that preserves the misleading implication.
- The gate's output is advisory research support, not legal advice; say so when the stakes warrant counsel.
- Log recurring blocks — a claim blocked three times is a signal to go get the proof, and say so.
