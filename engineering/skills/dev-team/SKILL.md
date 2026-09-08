---
name: dev-team
description: Run the development team's delivery lifecycle for any non-trivial change. Use when a feature or fix needs more than one specialist — routing work and reviews across the dev specialists, convening collaboration, enforcing the engineering challenge on every claim, reconciling against the blocking-gates table, and assembling the Change Record. Triggers: "run the lifecycle for X", "get design and backend on this", "assemble the change record", any change touching a gated surface.
---

# Run the development team

Drive a change from approved spec to verified, gated delivery. **This skill runs in
the main session, which dispatches each specialist as its own subagent** — there is no
orchestrator subagent (P1/P2). It holds no content authority: it routes, convenes, and
assembles verdicts; it never designs or writes code itself.

**Delegation policy:** when a task matches a specialist's domain, delegate rather than self-perform.

## 1. When to convene

Any non-trivial change: ≥2 dev specialists implied, a gated surface touched
(auth / schema / infra / CI / AI-prompt path), or a change that needs a spec then
build then review. Trivial one-file edits do not need the team — do them directly.

**Context read-path (repo-native, R10).** Engineering is project-scoped; context lives in the repo:
`CLAUDE.md` (auto-loaded, technical) + `BUSINESS-CONTEXT.md` (business) + `USER-PREFS.md` at the repo
root — update-proof by construction. The Core `prompt-brief` intake runs the Rung-0 context precheck
at session start. A **bare repo** (no `CLAUDE.md`, no business context) ⇒ `context-onboarding` runs
the full welcome flow with the engineering extension set (`references/context-questions.md`): the
shared core block writes `BUSINESS-CONTEXT.md`, the technical set writes `CLAUDE.md`. A **populated
repo** ⇒ no welcome; offer a short "review and fill gaps" pass. Same provenance/approval rules.

## 2. Seat selection rule — the tier matrix

**Intake first (the ROSTER §6 hand-off).** Requirement intake runs through the Core `prompt-brief`
ladder, which escalates to **`product-manager`** when a change needs a defined problem statement, user
stories, and acceptance criteria before design — Intake → `product-manager` → `principal-architect`.
With that brief in hand, start with **`principal-architect`** for the spec on any new feature. Then
select the producers the change needs (backend / frontend / data / ai-ml / edge-agent engineers) and
the **blocking gates** from the table below — a surface present in the diff with its gate omitted is
an incomplete selection. This table is derived from `TEAM.md`'s "Blocking gates" table (the source of
record if the two ever disagree, fix here) and is the one this skill actually reads, so the routing
step never depends on prose recall.

| Surface in the diff | Gate(s) | Stage |
|---|---|---|
| Auth, RBAC/ABAC, remote access, mTLS, secrets, tenant isolation | `security-architect` | spec + review |
| Audit trail, access control, retention, change management | `compliance-officer` | spec + review |
| Personal data collected/stored/transferred/sent to an LLM | `privacy-counsel` | spec + review |
| Data of record underpinning a regulated output | `domain-compliance` | spec + review |
| Any test missing or weak | `qa-test-engineer` (plan-time strategy) then `test-auditor` (audit gate) | plan + pre-review |
| `prisma/schema.prisma` change | `schema-reviewer` (gate; `data-engineer` authors and does not gate its own migration) | review |
| `/infrastructure/`, `/.github/` change | `devops-sre` (CODEOWNERS) | review |
| UI surface | `ux-designer` | spec + review |
| New attack surface, no stated detection/monitoring | `security-operations` (consulted; gate held by `security-architect`) | spec |
| Consequential automated/AI-driven/irreversible action | `operational-readiness` | spec + review |
| Operator-facing workflow readiness | `operational-readiness` | spec + definition-of-done |
| As-built spec drift | `technical-writer` (checked by `code-reviewer`) | review |
| Every change, no exception — unconditional, not surface-matched; include it even when the ask is framed as "just the gate wave" or names only the surface-matched gates (D-78) | `code-reviewer` + green CI, then `completion-auditor` last (§8) | review + close |

## 3. Wave order, and FAIL / COULD NOT ASSESS handling

Four waves, in order: **(1) spec** — `principal-architect` (+ `product-manager` if intake escalated)
— **(2) build** — the selected producers, TDD-style, from the approved spec — **(3) gates** — every
gate the tier matrix selected, dispatched together once the build wave's diff exists — **(4)
`completion-auditor`** — closes, per §8. Do not open wave *n+1* before wave *n*'s outputs exist; within
a wave, dispatch concurrently (§5 below).

- **A gate's FAIL stops the merge.** Route the FAIL and its stated fix back to the owning producer;
  the producer's fix re-enters wave 2, not wave 3 — a fixed diff is a new build, not a patched review.
- **A gate's COULD NOT ASSESS re-dispatches that gate once**, with the specific missing input named
  in the CNA's `reason`. If the re-dispatch still cannot assess, escalate to the human — a second CNA
  on the same gate is not treated as a pass by default or silently dropped.
- **Two-round re-review cap.** A gate may be re-dispatched at most twice on the same diff (the
  original pass plus one re-review after a fix). A third round means the diff needs to be re-scoped
  or the human needs to adjudicate directly — do not loop a gate a third time hoping it clears.

## 4. Cost quote (before dispatch)

Before dispatching a wave, state the quote as **agents × tier × estimated tokens**: list each agent
about to be dispatched, its model tier (opus/sonnet/haiku), and a rough per-dispatch token estimate,
summed. This is a stated estimate, not a metered measurement — say so — and it lets the human stop an
oversized wave before it runs rather than after.

## 5. Dispatch instruction

**In a SINGLE message, spawn the independent specialists as separate subagents** (Agent
tool) so they run concurrently; sequence only where a real dependency exists (spec →
build → gate review). Give each a context packet (§6). Producers work from the approved
spec, TDD-style.

**`code-reviewer` is part of every gate wave, dispatched regardless of how the ask is framed
(D-78).** A request scoped to "just the gate-review wave" or one that names only the
surface-matched gates does not narrow row 55 of the tier matrix — that row is unconditional, not
a surface match, so it is never read out of the selection by the framing of the ask.

## 6. Context each specialist receives (and must NOT receive)

Each gets: the approved spec/plan, the specific surface it owns, and the acceptance
criteria (the prompt-brief Done-criteria where one exists). A **gate reviewer must NOT
receive the producer's reasoning** — its fresh-context ignorance is the value (P5).
Pass the diff/artifact to the gate, not the author's rationale.

## 7. Synthesis rule

Enforce the **engineering challenge** on every claim: no "it works" without the check
that shows it. Collect each gate's verdict (PASS / CONCERNS / FAIL) into the **Change
Record**; preserve dissent; a single blocking FAIL stops the merge. Never average a
FAIL into a soft pass.

## 8. Closing gate

**`completion-auditor` runs last** on the assembled work — it re-checks ground truth
(refs advanced, CI green, STATE updated, Done-criteria met) before anything is reported
done. Route the code to `code-reviewer` and confirm the right CODEOWNERS gates cleared.

## 9. Degradation (pack absent)

If a required gate's pack is absent, mark that control **UNVERIFIED**, lower confidence,
and say so — never silently ship a gated surface ungated (§9.3). If the architect seat is
unavailable, do not let a producer self-spec a gated change; escalate instead.
