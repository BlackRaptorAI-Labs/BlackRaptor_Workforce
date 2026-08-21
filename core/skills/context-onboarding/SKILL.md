---
name: context-onboarding
description: >-
  The first-run welcome + the one standardized interview that teaches a pack your company and/or
  project before it does substantive work. Use on true first run (context file missing/template AND
  USER-PREFS.md missing), when a pack's context file is missing or still a template, or when the user
  says "set up the workforce", "onboard", "set up the context", "learn my business", "update the
  context", or points you at documents. Shared by every pack; choice-first, document-fed with
  provenance, approval before writing, and it can always be deferred with "Later".
---

# Context onboarding — first-run welcome & the standardized interview

One shared flow, used by every pack, that welcomes a new user, learns the company/project, learns
how the user wants to work, and proves what it recorded. It is choice-first, reads documents you
provide, marks where every fact came from, never writes without approval, and can always be
deferred.

## A. First-run detection & sequence (R7)

**True first run** = the pack's context file is missing or still a template AND `USER-PREFS.md` is
missing. Sequence: **W1 welcome → path choice → context interview (§C, core → extension) →
settings entry (§E) → closing summary → activation offer.**

**Smart skipping (guaranteed by project-root storage):** context present but prefs missing ⇒ settings
only; prefs present but context missing ⇒ interview only; both present ⇒ never welcome again.

### W1 — welcome (owner-ratified verbatim; do not substitute any earlier draft; changes need owner sign-off)

Open with exactly this (UNCHANGED; the §5 ACCEPT-WITH-RISK item stays in force):

> Welcome to BlackRaptor Workforce. To start out, let's tell the agents a little about your
> business and/or project and how you like to work. It's a short setup now, and the team uses
> it to give you better outcomes in the work that follows.

Then ask the **setup choice** VERBATIM (buttons **"Set up now" / "Later"**; render `{team-name}`
with the installing pack's name):

> Would you like to do the {team-name} setup now, or come back to it later?

## B. Widgets & plain-text fallback (R8)

Where the client offers a multiple-choice widget (e.g. AskUserQuestion), use it for CHOICE-type
questions; otherwise ask the SAME question in plain text. Hard rules: button labels are 1–3 words;
the explanation lives in the QUESTION TEXT (never compressed into a button); every choice question
ships WITH its question text; open-ended answers stay in normal chat; one question at a time.
Canonical labels: welcome = **Set up now / Later**; path = **Interview me / Read my documents /
Mix**; settings entry = **Use defaults / Customize**; approval = **Approve / Make changes**.

## C. The interview — path choice, then core, then extension

### C.0 — Path choice, VERBATIM (gate-cleared SHIP 2026-08-21; buttons "Interview me" / "Read my documents" / "Mix")

> How would you like me to learn about your business and/or project?

The three button labels carry the explanation (**Interview me / Read my documents / Mix**), so the
prompt stays terse. Branch on the choice: **questions (Interview me) / documents / mix**. Never
assume a folder exists. (This replaces the retired prose opener; its old byte-lock is retired.)

On the **documents** path (or the documents phase of Mix), open VERBATIM (gate-cleared; the
connector clause gates on "if you've already connected one" — keep that wording exactly):

> Great. Let's start with documents. You can attach files here in the chat, name a folder
> on your computer (I'll ask for access), or, if you've already connected one, point me at
> a source like Google Drive, SharePoint, or ClickUp. Anything that describes the business
> or project works well: a pitch deck, business plan, product overview, README, or website
> copy.

### C.1 — Effort expectation (questions path, and the questions phase of Mix) — R12(f)

On the questions path, open by stating the size, using this text VERBATIM apart from the two
rendered counts:

> This is about {N} short questions — the first {M} cover your business, the rest are
> specific to this team. Answer as briefly as you like, and say "later" at any point to
> stop; I'll save what we have.

`{N}` = the total questions in this pack's set (core + extension); `{M}` = the count of core
questions. Both are rendered AT DISPLAY TIME by counting the actual question sets — never a
hardcoded integer, never a duration claim.

### C.2 — Core block first, every pack (R14.1)

Ask the shared CORE set first (phrase naturally — this is a topic list, not fixed strings). Core
answers write to the shared business layer (`BUSINESS-CONTEXT.md`; engineering: repo-root
`BUSINESS-CONTEXT.md`):

1. **What it is** — what the company/project does (a sentence or two).
2. **Who it's for** — who uses it AND who pays (they can differ).
3. **Stage** — idea / building / testing with early users / selling / scaling.
4. **How money comes in** — the business model, current or intended.
5. **Priorities right now** — the top 1–3 goals for the next few months.
6. **Off-limits** — claims that can't be made yet, topics to avoid, rules/regulations the business
   operates under (seeds every pack's guardrails, including marketing proof standards).
7. **The user's role** — the one fixed-string question (§C.3).

### C.3 — Role question (core block, open-ended, no buttons) — R14.3

Ask VERBATIM:

> What's your role in the company or on this project? This helps the team match how it
> works with you — what to explain, what to skip, and which questions you're the right
> person to answer. (Optional.)

Store the answer as the optional `role` key in `USER-PREFS.md`; agents use it to tune explanation
depth (alongside reading-level, not replacing it) and to route questions. If the role suggests the
user likely can't answer an extension question, offer — VERBATIM — instead of pressing:

> Want me to mark it UNKNOWN so a teammate can fill it in later? Nothing gets sent to anyone.

Answering the role question is optional; skipping stores nothing.

### C.4 — Per-team extension (R14.2, dedupe rule)

After core, continue with the installing pack's OWN extension set — the per-pack question set the
pack provides. DEDUPE RULE: an extension question may DEEPEN a core answer ("you said X buys — walk
me through the buying decision") but must NEVER re-ask core ground. Extension answers write to the
pack's own context file (per R1): marketing → `MARKETING-CONTEXT.md`; council → the remaining
business-context fields; hardware → `PROGRAM-CONTEXT-<program>.md`; engineering → the technical set
(writes `CLAUDE.md`), see §G.

### C.5 — Cross-pack reuse — never re-ask core (R14.4)

When a pack onboards and the shared business layer already exists (another pack set up first), SKIP
the core block and confirm VERBATIM (apart from the two rendered names `{file}`/`{team}`):

> I found your business info from an earlier setup ({file}). I'll use what's there and only
> ask what's missing plus the {team}-specific questions — and if anything's changed, tell
> me: I'll show you the change before I save it.

Entries derived this way carry provenance `[doc: {file}]`. "What's missing" includes UNKNOWN markers
left by an earlier partial setup — those business questions ARE re-asked. "Something changed" routes
to the normal PROPOSED-DIFF path, never a silent rewrite.

## D. Thoroughness, provenance, approval, write (R5 + R12)

- **Walk EVERY section** of the pack's context template (core + extension). Each section is either
  filled or carries an explicit **"UNKNOWN — user to provide"** marker the user chose — never
  silently blank.
- **Provenance per entry:** `[doc: <filename>]` (from a supplied document, name it) · `[user]`
  (stated in the interview) · `[unknown]` (a gap the user chose to defer).
- **Clarify only gaps and conflicts.** Flag document-vs-document conflicts explicitly and let the
  user rule — never silently resolve. Do not re-ask what documents already answer.
- **Completeness read-back before approval (R12c):** show filled / unknown / conflicts-resolved.
- **Approve before writing.** Present the full draft; if the user set one-decision-at-a-time, walk
  the open points one at a time. Write nothing until approved.
- **On approval:** write to the resolved project-root location, **date-stamped**, with a `## Sources`
  section listing every consumed document/URL, and the file's UNKNOWNs listed in one place (R12d).
  The written file carries no template marker.
- **Maintenance:** new material later ⇒ a **PROPOSED DIFF** ("here's what would change"), applied only
  on approval, re-date-stamped. Never a silent rewrite.

## E. Settings round (R9) — writes USER-PREFS.md; defaults-first

Ask the entry question VERBATIM, then buttons **"Use defaults" / "Customize"** ("Use defaults"
first). "Use defaults" writes `USER-PREFS.md` with exactly the named defaults; the closing summary's
file list names it.

> How should the team work with you? The defaults are plain language, brief answers, ask
> when unsure, check in at milestones, one decision at a time, a quarterly heads-up at
> session start to review your context file, and both unit systems for hardware work. Happy
> with those for now? You can change any of them later — just say "set my preferences." I'll
> save your choices to USER-PREFS.md in this project so I don't ask you to set these up
> again. (Safety checks and approvals aren't preferences and aren't configurable here.)

**Customize** — one widget question per setting, each shipped WITH its question text VERBATIM,
defaults marked (d). Each maps to a `USER-PREFS.md` key (see the `set-preferences` skill):

1. "How should I explain things?" — **Plain** (d) / **Technical**  → `reading-level`
2. "How long should my answers be?" — **Brief** (d) / **Detailed**  → `verbosity`
3. "If something's unclear mid-task, should I stop and ask you, or make a reasonable assumption, label it, and keep going?" — **Ask me** (d) / **Assume and flag** (maps to the ASSUMED provenance label — never unlabeled guessing)  → `question-style`
4. "When choices come up, how should I bring them to you?" — **One at a time** (d) / **Grouped**  → `decisions-grouping`
5. "How often should I check in while working?" — **Frequent** / **Milestones** (d)  → `checkpoint-frequency`
6. "Want me to flag when your context file is getting stale? I'll mention it at the start of a session when it's due — I won't contact you between sessions. ('At launches' means when you kick off a campaign or release.)" — **Quarterly** (d) / **At launches** / **Off** (honored per R13.2)  → `context-review-cadence`
7. (Hardware pack only) "How should I show measurements?" — **Metric** / **Imperial** / **Both** (d) (honored per R13.3)  → `units`

NEVER offered as settings: the claims gate, no-autonomous-send/spend, or any safety gate.

## F. Closing summary + activation (R7)

After writing, show the closing summary VERBATIM (the file list is rendered — it MUST name every
file actually written THIS run, including `USER-PREFS.md` whenever written, and no file that wasn't;
add no benefit/performance claims):

> All set. I saved your answers in this project: [list of files written, with paths].
> Anything we marked UNKNOWN is listed inside the files above; add it whenever you're ready.
> To change things later, just say "update the context" or "set my preferences."

Then, as a SEPARATE message, the activation offer VERBATIM (open-ended, no buttons; a named task
starts work immediately; a decline ends the flow politely):

> Want to put the team to work right now? Tell me what you'd like done first and I'll get
> started.

## G. Engineering repo-native variant (R10)

Engineering is PROJECT-SCOPED (do not change). Context home = the repo: `CLAUDE.md` (auto-loaded) +
`BUSINESS-CONTEXT.md` + `USER-PREFS.md` at the repo root. A **bare repo** (no `CLAUDE.md`, no
business context) ⇒ full welcome flow with the ENGINEERING question set (project purpose, language +
stack, environments, build/test commands and expectations, definition of done, merge/deploy rules,
conventions), writing `CLAUDE.md` (technical) + `BUSINESS-CONTEXT.md` (business) under the same
provenance/approval rules. A **populated repo** ⇒ no welcome; offer a short "review and fill gaps"
pass. Preferences per §E to repo-root `USER-PREFS.md`.

## H. "Later" — defer gracefully at any point (R7.1)

"Later" at the welcome, or "later" at ANY point in the interview, ends the flow gracefully:
everything answered so far is saved (partial context file with UNKNOWN markers per §D; partial prefs
written), agents proceed normally, and anything they must assume about the business carries the
ASSUMED provenance label. The flow never re-launches unprompted in the same session. Acknowledge
VERBATIM:

> No problem — the team is ready to work now. Until we finish setup, I'll mark what I had
> to assume about your business. Say "set up the workforce" whenever you're ready and I'll
> pick up where we left off.

"Set up the workforce" (or the R3 trigger in a later session) RESUMES from the partial file —
previously answered sections are not re-asked.

## I. Resolution order (every pack) & precedence

**Resolution order:** current working / project root → an explicit path the user names → if none,
run this flow and, before writing, ask where to save (default: project root). Canonical project-root
files: `BUSINESS-CONTEXT.md` (council; engineering: repo root), `MARKETING-CONTEXT.md` (marketing),
`PROGRAM-CONTEXT-<program>.md` (hardware). The pack-internal template is NEVER the live copy.

**Precedence (universal):** once written, the context file wins over agent improvisation; an agent
whose output would contradict it flags the contradiction to the user — never a silent override.
