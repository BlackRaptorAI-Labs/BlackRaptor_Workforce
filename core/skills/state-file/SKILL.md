---
name: state-file
description: >-
  Use for any multi-chunk or multi-session task to keep work from drifting — read
  the STATE file at the start of each chunk, update it at the end, and never carry
  claims in your head across a context boundary. Triggers: starting a chunk of a
  larger task, resuming work, or any job decomposed into more than one session.
  The anti-drift execution protocol (7.4) — the discipline this build used on
  itself, shipped as a skill.
---

# The anti-drift execution protocol

Long work drifts: claims made early are forgotten or misremembered late, and each
fresh context re-derives the world slightly differently. This protocol fixes the
world in a **STATE file** with checkable provenance, decomposes work into
**chunks**, and matches **checkpoint** frequency to the stakes.

## Part 1 — the STATE file (fixed schema)

One file, `STATE.md`, updated at every chunk boundary. Exactly these sections:

```
# STATE — <task name>  ·  updated <date>
## done            # completed & VERIFIED — each entry carries a checkable ref
## in-progress     # started, not finished — each entry carries a ref where one exists
## constraints     # rules the work must hold to (forward-looking; no ref required)
## decisions       # choices made & why — each entry carries the ref that enacted it
## next            # the immediate next steps (forward-looking; no ref required)
```

- **Read at chunk START**, **update at chunk END.** "State updated" is part of the
  **definition of done** for every chunk — the completion-audit gate checks it (its
  checklist item, added the same way the 7.2 done-criteria ruler was).
- **PROVENANCE RULE (enforced, not aspirational).** Every entry in **done**,
  **in-progress**, and **decisions** MUST carry something checkable — a **commit
  hash** or a **file path**. Prose-only claims ("fixed the thing", "it works") are
  **banned** in those sections. `constraints`/`next` are plans, not claims of
  reality, so they need no ref.
- **Gates check state-vs-reality.** The scripted audit `_eval/baseline/state_audit.py`
  resolves every claim entry's ref against reality (commit hash → `git cat-file`;
  file path → exists?) and FAILs on a prose-only entry or an unresolvable ref.
- **Size-capped.** Keep `STATE.md` bounded; when a section grows past ~15 lines,
  move settled entries to `STATE-archive.md` (append-only) and keep the live file
  to the current and next chunk.

## Part 2 — chunked execution

- **Decompose BEFORE executing.** Break complex work into coherent chunks —
  **~5–7 steps** as a guideline, but the real rule is **one testable outcome per
  chunk** (a chunk ends where a gate, test, or check can pass/fail).
- **Each chunk = a fresh session + the STATE file in.** Start the chunk by reading
  `STATE.md`; do not rely on prior-context memory. This is what makes the protocol
  drift-proof across context boundaries.

## Part 3 — tiered checkpoints

How often you pause for a human is a **tier**, and the tier is not guessed:

| tier | checkpoint cadence | when |
|---|---|---|
| **heavy** | **user checkpoint every chunk** | consequential / irreversible / high-ambiguity work |
| **light** | **gate-checks + one end summary** | routine, reversible, clear-done work |

- **The tier is SET by the intake ladder (7.2):** a request that escalated to
  Rung 3 (≥2 specialists, irreversible, or no stateable done-criteria) → **heavy**;
  a Rung 1/2 request → **light**.
- **The tier is TUNABLE by the user via USER-PREFS (7.3):** `checkpoint-frequency:
  every-chunk` forces heavy; `end-only` forces light; `milestones` follows the
  intake tier. USER-PREFS wins when it conflicts with the intake default.
