---
name: set-preferences
description: >-
  Use when the user wants to set or change how the assistant communicates with
  them — reading level, verbosity, how many clarifying questions to ask, or how
  often to checkpoint. Triggers: "set my preferences", "explain things more
  simply", "be more concise", "stop asking so many questions", "check in less
  often". Writes or updates the user-owned USER-PREFS.md; it does not change any
  agent, skill, or shipped file. The conversational front end for the Layer-0
  Core contract's Interaction-preferences directive.
---

# Set interaction preferences

Capture how this user wants to be communicated with into **`USER-PREFS.md`** in
the working directory. Every agent and the main session honor that file via the
Core contract's *Interaction preferences* directive — so you set it in one place,
DRY, and it applies everywhere without touching any agent body.

## What USER-PREFS.md is (and is not)

- **User-owned and local.** It lives in the user's working directory. It is
  **never** shipped, synced, built, or committed into the plugin/mono-source —
  it is explicitly OUT of the mono-source invariant. Do not add it to `_source/`,
  `dist/`, or any repo. If you are ever asked to "ship preferences," refuse and
  explain it is user-space by design.
- **Small.** Keep it to **≤ ~10 lines**. It is a preference file, not a profile.
- **Advisory, never overriding.** It changes *how* you communicate, never *what*
  is true. It cannot weaken the four Core commitments (nothing invented / hidden /
  half-done / unaccountable) or the provenance and standards rules.

## The seven preference dimensions

| dimension | key | values (default in **bold**) | effect |
|---|---|---|---|
| reading level | `reading-level` | **`plain`** / `technical` (also accepts `8th-grade`, `expert`) | target readability of prose (graded) |
| verbosity | `verbosity` | **`brief`** (cap ~120 words / answer) / `detailed` (also accepts `succinct`, `normal`, `thorough`) | length budget per answer (graded) |
| question style | `question-style` | **`ask`** / `assume-and-flag` | on mid-task ambiguity: stop and ask, or make a labeled ASSUMED assumption and continue |
| checkpoint frequency | `checkpoint-frequency` | `frequent` / **`milestones`** | how often to pause for confirmation |
| decisions grouping | `decisions-grouping` | **`one-at-a-time`** / `grouped` | how choices are brought to the user — honored in ALL interactions |
| context-review cadence | `context-review-cadence` | **`quarterly`** / `at-launches` / `off` | in-session staleness reminder (R13.2); never out-of-session contact |
| units | `units` | `metric` / `imperial` / **`both`** | measurement display; honored in the hardware pack (R13.3), inert elsewhere |

Optional keys, written only when set: `role` (free text, from onboarding) · `declined` (list of
dimensions the user declined to tune) · `offered` (list of dimensions offered once via
observe-then-suggest). Safety gates, the claims gate, and approvals are NOT preferences and are not
settable here.

## Process

1. **Read the current file** if it exists (`USER-PREFS.md`); otherwise start fresh.
2. **Ask only for what is ambiguous** — if the user said "be more concise," set
   `verbosity: brief` and confirm; do not interrogate all seven dimensions.
3. **Write the file** in the fixed format below. Overwrite cleanly; keep ≤10 lines.
4. **Confirm** the change in one sentence and apply it immediately in your next reply.

## Fixed format

```
# USER-PREFS — how to communicate with me (user-owned; never shipped)
reading-level: plain              # plain | technical
verbosity: brief                  # brief | detailed
question-style: ask               # ask | assume-and-flag
checkpoint-frequency: milestones  # frequent | milestones
decisions-grouping: one-at-a-time # one-at-a-time | grouped
context-review-cadence: quarterly # quarterly | at-launches | off
units: both                       # metric | imperial | both
# optional, written only when set:
# role: <free text>
# declined: []
# offered: []
```

## Conformance (how "honored" is checked)

- **Schema:** `_eval/baseline/prefs_conformance.py validate --prefs USER-PREFS.md` confirms all
  seven required keys are present with allowed values, and that optional `role`/`declined`/`offered`
  are well-formed when present. Schema validation proves the keys exist — not behavioral conformance.
- **Behavioral (graded):** `reading-level: plain` → prose scores **≤ grade 10** (Flesch–Kincaid);
  `verbosity: brief` → answers stay **within the word cap**. `prefs_conformance.py check` measures
  these, not asserts them. The other five dimensions are honored by named mechanisms at their cited
  file:line (units in hardware, cadence at the context-resolution step, decisions-grouping in every
  interaction), demonstrated rather than FK/word-count graded.
