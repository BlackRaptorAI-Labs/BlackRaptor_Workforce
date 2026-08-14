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

## The four preference dimensions

| dimension | example values | effect |
|---|---|---|
| **reading level** | `8th-grade`, `plain`, `expert` | target readability of prose |
| **verbosity** | `succinct` (cap ~120 words / answer), `normal`, `thorough` | length budget per answer |
| **question style** | `minimal` (≤1 clarifying Q), `normal` (2–4), `ask-freely` | intake-ladder questioning (7.2) |
| **checkpoint frequency** | `every-chunk`, `milestones`, `end-only` | how often to pause for confirmation |

## Process

1. **Read the current file** if it exists (`USER-PREFS.md`); otherwise start fresh.
2. **Ask only for what is ambiguous** — if the user said "be more concise," set
   `verbosity: succinct` and confirm; do not interrogate all four dimensions.
3. **Write the file** in the fixed format below. Overwrite cleanly; keep ≤10 lines.
4. **Confirm** the change in one sentence and apply it immediately in your next reply.

## Fixed format

```
# USER-PREFS — how to communicate with me (user-owned; never shipped)
reading-level: 8th-grade        # 8th-grade | plain | expert
verbosity: succinct             # succinct | normal | thorough
question-style: minimal         # minimal | normal | ask-freely
checkpoint-frequency: milestones # every-chunk | milestones | end-only
```

## Conformance (how "honored" is checked)

- **8th-grade mode** → prose scores **≤ grade 8** on a readability check
  (Flesch–Kincaid). `succinct` → answers stay **within the word cap**.
- The check is scripted: `_eval/baseline/prefs_conformance.py` grades a response
  against a `USER-PREFS.md`. Conformance is measured, not asserted.
