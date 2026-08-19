---
name: context-onboarding
description: >-
  The one standardized interview that teaches a pack your company and/or project before it does
  substantive work. Use when a pack's context file is missing or still a blank template, or when
  the user says "onboard", "set up the context", "learn my business", "update the context", or
  points you at documents about their company/project. Shared by every pack; choice-first
  (questions / documents / mix), document-fed with provenance, approval before writing.
---

# Context onboarding — the standardized interview

One interview, shared by every pack, that produces the pack's **context file** — the durable
record of the company and/or project the pack serves. It is choice-first, can read documents you
provide, marks where every fact came from, and never writes anything until you approve it.

## 0. Open with this — VERBATIM (owner-ratified; do not edit without owner sign-off)

The interview MUST open with exactly this text, word for word:

> I need to learn your business and/or project before the team can do good work. How would
> you like to do this? I can interview you with questions and you type the answers, you can
> point me at a folder or files and I'll do the reading, or we can mix both — documents
> first, then I'll ask about whatever they don't cover. You can also add more material later
> anytime.

## 1. Where the context file lives (resolution order — one place, all packs)

Filled context files live at the **project root the user is working in**, never inside an
installed pack (a pack update would overwrite it, and Cowork cannot durably write into synced
packs). Canonical names at the project root:

- `BUSINESS-CONTEXT.md` — company-level context (council).
- `MARKETING-CONTEXT.md` — company-level marketing context (marketing).
- `PROGRAM-CONTEXT-<program>.md` — one per hardware program (hardware).
- Engineering uses the project's existing context conventions; read those where they already live.

**Resolution order (every pack follows this):** (1) the current working / project root → (2) an
explicit path the user names → (3) if none is found, run this onboarding and, before writing, ask
where to save, defaulting to the project root. The pack-internal template is NEVER the live copy —
it only tells you the shape of the file and that onboarding has not been done.

## 2. Branch on the user's choice — never assume a folder exists

After the opening, do what they choose: **questions**, **documents**, or **mix**. Do not assume
documents exist; ask.

## 3. Documents path — read, draft, and mark provenance

When the user points you at folders, files, or URLs (URLs only when the user provides them — no
web-crawling):

1. Read what they gave you.
2. **Draft** the context file from it — do not treat the draft as final.
3. Mark **every entry's provenance** inline:
   - `[doc: <filename>]` — taken from a document the user supplied (name the document).
   - `[user]` — stated by the user in the interview.
   - `[unknown]` — not established yet; needs an answer or is left as an open gap.

## 4. Clarify only gaps and conflicts

Ask deep clarifying questions **only** for gaps (facts no document or answer covers) and
conflicts. When two documents disagree, **flag the conflict explicitly and let the user rule** —
never silently pick one. Do not re-ask what the documents already answer.

## 5. Approve before writing

Present the **full draft for approval**. If the user has asked for one decision at a time, walk
the open points one at a time rather than dumping them at once. Write nothing until they approve.

## 6. On approval — write the file, dated, with Sources

Write the approved context to the resolved project-root location. Include:
- a **date stamp** (the date the context was captured/approved), and
- a **`## Sources`** section listing every document and URL consumed, so the provenance is auditable.

The written file carries no template marker (its presence + date stamp is how the trigger and
`workforce-doctor` check 6 tell "onboarded" from "still template").

## 7. Maintenance — propose diffs, never silently rewrite

When new material arrives later, do **not** overwrite. Produce a **PROPOSED DIFF** ("here is what
would change and why"), apply it only on approval, and re-date-stamp. Conflicts with the existing
file are surfaced the same way as document conflicts — the user rules.

## 8. Per-pack question set

Interview against the question set the **pack you are serving** provides — each pack supplies its
own, so the questions fit the discipline:

- **Marketing** — the marketing question set carried by the `marketing-core` skill (company/product,
  brand architecture, personas in priority order, GTM, voice, competitors, proof standards, ethics
  guardrails). Preserve marketing's hard-gate rules; never weaken them during onboarding.
- **Council** — the fields in the council pack's business-context template.
- **Hardware** — the fields in the hardware pack's program-context template (one file per program).

If a pack supplies no question set, interview from the resolution order and the file's own headings.

## 9. Precedence (universal)

Once written, the context file **wins over agent improvisation**. An agent whose output would
contradict the context file flags the contradiction to the user — it never silently overrides the
file.
