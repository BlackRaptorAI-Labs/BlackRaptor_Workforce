---
name: state-file
description: >-
  Use for any multi-chunk or multi-session task to keep work from drifting — one state file per
  WORKSTREAM, done-condition written first, decisions recorded with ADR discipline, read at the
  start of each chunk and updated when work turns significant. Never carry claims across a context
  boundary. Triggers: starting/resuming a workstream, a decision made, real work completed. The
  anti-drift execution protocol (v2).
---

# The anti-drift execution protocol (v2)

Long work drifts: claims made early are forgotten or misremembered late, and each fresh context
re-derives the world slightly differently. This protocol fixes the world in a **per-workstream state
file** with checkable provenance and ADR-disciplined decisions, decomposes work into **chunks**, and
matches **checkpoint** frequency to the stakes. The state file IS the session-to-session handoff — no
separate handoff docs between sessions of the same work (go-blocks between different actors remain).

## Part 1 — the state file

### 1.1 Unit and naming (per WORKSTREAM, never per-session/per-topic)
One state file per **workstream** — a piece of work with its own stateable done-condition. Name:
**`<work-slug>-state.md`** — short kebab-case slug, stable for the life of the work, no dates in the
name (the date lives in the header). Lives at the project root (code work: repo root or `docs/`), in
version control where one exists. When a project has **two or more** state files, add
**`STATE-INDEX.md`**: one line per workstream — slug, status, one-phrase description.

### 1.2 The workstream test (creation rule)
Create a state file when (a) the user asks, or (b) the **significance trigger** fires — a decision was
made or real work was completed — AND the work passes the test: **can you write its done-condition in
one sentence?** If yes, it's a workstream: create `<slug>-state.md` and write `done-condition:` in the
header FIRST, before work starts. If no, it's a topic, not a workstream — do not create a file (see
1.6). A session that wanders across five topics does NOT get five files.

### 1.3 Schema
```
# STATE — <work name> · updated <date>
status: active | paused | done | superseded-by: <file>
done-condition: <one sentence, written before work starts>
related: <other state files, if any>
## done          # completed & VERIFIED — every entry carries a checkable ref
## in-progress   # started, not finished — ref where one exists
## constraints   # rules the work must hold to (forward-looking; no ref)
## decisions     # ADR discipline — see 1.4
## next          # immediate next steps (forward-looking; no ref)
```

- **PROVENANCE RULE (enforced).** Every entry in `done`, `in-progress`, `decisions` carries a
  checkable ref — a commit hash or a file path. Prose-only claims are banned there.
  `_eval/baseline/state_audit.py` resolves refs against reality and the new header fields, and FAILs
  on a prose-only entry, an unresolvable ref, or a missing `status`/`done-condition`.
- **Size-capped.** When a section grows past ~15 lines, move settled entries to the append-only
  archive — moved **VERBATIM, never summarized** (summarization is where drift lives).

### 1.4 Decisions get ADR discipline
Each decision entry: an **ID** (D-01, D-02…), a **date**, one decision, why, and its ref. Entries are
**immutable** — reversing a decision is a NEW entry ("D-07 supersedes D-03: <why>"), never an edit or
deletion. The trail of mind-changes is itself the record.

### 1.5 Update cadence
Update at chunk boundaries and whenever the significance trigger fires (a decision made, a
done-criterion flips, an external commitment made). For code work the commit hash is the natural ref
— update when something worth a decision or done entry happened, not on every edit. "State updated"
stays part of the definition of done, so the most a dying session loses is its current chunk.

### 1.6 Multi-topic sessions (the honest rule)
Decisions attach to the **workstream they BIND**. A wandering session usually advances one or two
actual workstreams — update those. A topic with no workstream yet gets nothing; if it matures into
work later, it gets a file THEN, and its earlier decisions are copied in with their original refs.

### 1.7 Relating & merging workstreams (never rewrite history)
1. **Related but separate** → add each file to the other's `related:` line; each stays authoritative.
2. **One absorbs the other** → the absorbing file receives the absorbed file's live entries WITH
   their original refs and decision IDs (prefixed, e.g. "from X: D-03"); the absorbed file's body
   becomes a **tombstone** — `status: superseded-by: <file>` + date — and is KEPT, never deleted.
3. **Merging is never summarizing** — entries move verbatim or not at all.

## Part 2 — chunked execution
- **Decompose BEFORE executing.** One testable outcome per chunk (a chunk ends where a gate, test, or
  check can pass/fail); ~5–7 steps as a guideline.
- **Each chunk = a fresh read of the state file in.** Start by reading `<slug>-state.md`; do not rely
  on prior-context memory. This is what makes the protocol drift-proof across context boundaries.

## Part 3 — tiered checkpoints
| tier | checkpoint cadence | when |
|---|---|---|
| **heavy** | user checkpoint every chunk | consequential / irreversible / high-ambiguity work |
| **light** | gate-checks + one end summary | routine, reversible, clear-done work |

- **SET by the intake ladder:** a Rung-3 escalation (≥2 specialists, irreversible, or no stateable
  done-criteria) → heavy; Rung 1/2 → light.
- **TUNABLE by USER-PREFS:** `checkpoint-frequency: frequent` forces heavy; `milestones` follows the
  intake tier. USER-PREFS wins on conflict.
