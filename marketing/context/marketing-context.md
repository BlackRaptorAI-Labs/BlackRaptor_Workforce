<!-- TEMPLATE — not onboarded -->
# Marketing Intelligence Core

> **This file is the hub.** Every marketing agent and skill in this plugin reads
> this file BEFORE producing any output. If a section conflicts with an agent's
> generic best practice, this file wins. Keep it current — a stale core produces
> confident, wrong marketing.
>
> **This is the blank template — it ships in the pack and a pack update overwrites it.** The
> filled copy lives at your **project root** as `MARKETING-CONTEXT.md`, never inside the pack.
> Say **"set up the marketing context"** (or "onboard") and the shared `context-onboarding`
> skill runs the standardized interview and writes the dated result to your project root. Until
> it exists, agents must ask for the missing context rather than inventing it.

## 1. Company & Product

- **Company:**
- **Product (one paragraph, no jargon):**
- **Vision in one sentence:**
- **Stage:** (idea / pre-launch / design partners / first revenue / scaling) —
  stage constrains every claim (see §6).
- **Strategy files (read when present in the project folder):** list the
  vision/strategy/pricing documents agents should treat as ground truth.

## 2. Buyers & Phasing

- **Current-phase segment (ALL current marketing energy goes here):** who
  exactly, their real pain in their words, buying triggers, and the channels
  where they actually are.
- **Later-phase segments:** listed with an explicit HOLD until the current
  phase proves out. No content for future-phase segments before then.
- **Surface rules:** if different GTM tracks must not share pages/messaging
  (e.g., direct vs. channel), state the rule here.

## 3. Naming Status

- Final names, working names, and anything pending trademark counsel.
- **Blocked names (live marks/conflicts — never use):**
- **Candidates pending counsel (INTERNAL ONLY — never publish):**

## 4. Approved External Claims (the ONLY cleared claims)

Two tables. Anything absent from the first is not cleared; anything in the second is banned outright.
The claims gate reads both. Date the list and name an owner per row — an undated claims register is
how a claim that was true last quarter ships this quarter.

### 4a. Cleared claims

| Claim (verbatim, as it may be published) | Evidence status | Proof standard it must meet | Date cleared | Owner |
|---|---|---|---|---|
| <the exact wording> | measured / cited / attested / customer-stated | <what would substantiate it, e.g. "a third-party report naming the scope and date"> | YYYY-MM-DD | <role> |

### 4b. Retired and banned claims (hard BLOCK)

Claims that were once used, or are commonly reached for, and must never ship again. The claims gate
BLOCKS any copy that asserts one in substance, however it is reworded.

| Claim | Why it is banned | Proof standard that would be needed | Date retired | Owner |
|---|---|---|---|---|
| "fewer tokens than plain Claude" (or any cheaper/less-compute-than-a-single-chat framing) | Contradicted by our own measurement: a multi-agent run spends token MULTIPLES of a single chat. The standing always-on roster tax alone was measured at 11,628 tokens per turn for a full install. | A like-for-like measured comparison on the same task set, published with its method | 2026-08-07 | marketing owner |
| "only truth" / "never wrong" | Unearnable by any system. | none — not assertable | 2026-08-07 | marketing owner |
| "no hallucination" / "cannot hallucinate" | Unearnable by any system. | none — not assertable | 2026-08-07 | marketing owner |
| "fewer interactions" / "less rework per deliverable" as a MEASURED value claim | Measured and earned, but owner-HELD pending ride-along conditions and outside counsel. Earned is not cleared to assert. | Owner release, then only in the narrowed conditions-met wording | 2026-08-11 | owner |

## 5. Voice

Tone rules, persona-awareness, what the brand never sounds like, acronym rules,
and which channels are founder-voice vs. brand-voice.

## 6. Ethics & Compliance Rules (HARD GATES — no agent may override)

Adapt to your business; keep the pattern. Recommended defaults:

1. **No efficacy/performance numbers in external copy without audited,
   citable data.** State capability and mechanism, not percentages.
2. **No "certified" / "compliant" / certification-conferral language** unless
   the certification is actually held. Use "built to X controls" / "X-aligned".
3. **No autonomous marketing sends, posts, or spend.** Agents draft; a human
   approves and sends. CAN-SPAM/TCPA and platform rules apply.
4. **Statistics require a findable citation.** Vendor figures flagged as
   vendor figures. Never assert unverified numbers.
5. **No fake testimonials, fake customers, or AI-generated people presented
   as real.** FTC endorsement guides apply.
6. **Conflicts of interest disclosed** (affiliate/referral/partner framing).
7. All external-facing copy passes the `compliance-claims-gate` skill before
   delivery.

## 7. Competitors

The tracked competitor set. All competitive claims verified against primary
sources; battle cards refreshed before any campaign referencing a competitor.

## 8. Key Dates & Windows

The buying-trigger calendar: renewal windows, regulatory deadlines, seasonal
spikes, industry events — with what each window means for content and spend.

## 9. Open Items Gating Marketing

What is currently blocked and on what (counsel clearances, evidence not yet
audited, name not final, budget approvals).

## 10. Maintenance

Update on: name clearance, persona/phase change, new cleared claim, pricing
change, guardrail change. Date-stamp material edits. Review whenever a campaign
launches, a quarter closes, positioning is debated, or 90 days pass.

**Last material edit:** (unset — run onboarding)
