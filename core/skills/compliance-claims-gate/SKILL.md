---
name: compliance-claims-gate
description: >
  Use to check marketing/sales copy against proof standards and ethics guardrails before ANY external-facing asset is delivered, returning pass/fix/block per claim. This is the METHOD; dispatch the isolated claims-gate AGENT instead of running this on copy the current context authored — that is self-review.
metadata:
  version: "1.2.0"
---

# Compliance-Gated Claims Engine

## The gate is the isolated `claims-gate` AGENT — not self-review (A1)

This skill is the **method**. The **gate** is the separate **`claims-gate` agent**, which runs this
method in a context that has **not** seen the copy's author reasoning (P5). The mandatory routing rule —
*every external-facing marketing asset is dispatched to the `claims-gate` agent before delivery* — is
carried on loaded surfaces (this skill and each producer's
description; no hook carries it) because a plugin-root `CLAUDE.md` carrier does **not** load on a marketplace install (measured;
SPEC §2 P11). **Do NOT run this skill on copy the current context wrote** — that is self-review, which the
gate exists to prevent; dispatch the `claims-gate` agent instead. Guaranteed isolated dispatch is the
`marketing-campaign` skill's mandatory step; for an ad-hoc single asset, dispatch the `claims-gate` agent
and, if you cannot, say so and do not present the copy as gate-cleared.
The DRAFT/GATED write gate is best-effort: it trusts any `.verdict.md` on disk, so a verdict file a
producer wrote itself is caught only by the `Stop` hook's dispatch check, and only when no
`claims-gate` dispatch happened later in the same turn.

## The DRAFT/GATED file convention (mechanical enforcement, the 2.1.0 claims-gate change)

Every producer of external-facing copy — the marketing pack's asset and release-note producers,
`product-docs-writer`, and the `marketing-campaign` skill — writes an asset as `<name>.DRAFT.md`,
never as `<name>.md` directly. An asset becomes `<name>.md` only after an isolated `claims-gate`
dispatch has written a sibling `<name>.verdict.md` carrying a valid verdict block whose `verdict` is
`PASS` or `CONCERNS` with no `BLOCK`-graded claim row. This is stated once, here; a producer body or
skill references this rule in one sentence and does not restate the mechanics.

Two controls make this mechanical rather than checklist-only (the 2.1.0 claims-gate change):
- A **PreToolUse hook** (`enforce-draft-gate.sh`, Core) refuses a `Write`/`Edit` whose target is a
  `*.md` file under a directory the session has marked as a marketing-asset directory (a `.br-assets`
  marker file, written by the `marketing-core` skill at onboarding and by `marketing-campaign` at
  campaign start), unless the target is `*.DRAFT.md`, `*.verdict.md`, or a `*.md` whose sibling
  `*.verdict.md` exists and validates. Outside a marked directory the hook is inert. Kill switch:
  `BR_CLAIMS_HOOK=off`. Malformed input fails OPEN (the write is allowed; the event is logged), same
  discipline as the verdict Stop hook.
- The core **Stop hook** (`validate-verdicts.sh`) additionally blocks the turn when the transcript
  shows a `Write` of a `*.DRAFT.md` under a marked directory with no later `claims-gate` dispatch in
  the same session — the gap the unscoped August hook did not have and over-blocked trying to close;
  this check is scoped to marked directories only, so an engineering or council session sees zero
  false blocks.

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
 - **Puffery** — subjective, non-measurable ("support"). Pass but flag if it borders on measurable.
   - **Testimonial/endorsement** — verify consent and FTC endorsement-guide disclosure. Block without both.
   - **Conflict of interest** — affiliate or partner relationships must be disclosed in-body. Fix.
4. Check channel-specific law: CAN-SPAM for email (identification, opt-out, physical address), TCPA for SMS/calls, FTC endorsement guides for influencer/UGC-style content.
5. Return a verdict table: claim → classification → verdict (PASS = publish · CONCERNS = fix per the suggested rewrite, then publish · FAIL = block, with reason) → evidence required to unblock.

## Rules

- Default to BLOCK when uncertain; a delayed claim costs less than a retracted one.
- Never rewrite a blocked claim into a technically-true version that preserves the misleading implication.
- The gate's output is advisory research support, not legal advice; say so when the stakes warrant counsel.
- Log recurring blocks — a claim blocked three times is a signal to go get the proof, and say so.
