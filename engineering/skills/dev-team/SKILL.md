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

**Context read-path.** Engineering keeps the project's **existing** context conventions (the repo's
own docs / `PROGRAM-CONTEXT` / spec — engineering does not introduce a new company-context file).
The Core `prompt-brief` intake runs the context precheck (Rung 0): resolve the project's context per
the resolution order (project root → an explicit path the user names) before substantive work; if the
change depends on company/project context the project does not yet record, `context-onboarding` can
capture it to the project root.

## 2. Seat selection rule

**Intake first (the ROSTER §6 hand-off).** Requirement intake runs through the Core `prompt-brief`
ladder, which escalates to **`product-manager`** when a change needs a defined problem statement, user
stories, and acceptance criteria before design — Intake → `product-manager` → `principal-architect`.
With that brief in hand, start with **`principal-architect`** for the spec on any new feature. Then select the
producers the change needs (backend / frontend / data / ai-ml / edge-agent engineers)
and the **blocking gates** the surface triggers (security-architect, qa-test-engineer,
the relevant compliance/privacy/domain gates, data-engineer for schema). Reconcile the
selection against the standing blocking-gates table — a gated surface with its gate
omitted is an incomplete selection.

## 3. Dispatch instruction

**In a SINGLE message, spawn the independent specialists as separate subagents** (Agent
tool) so they run concurrently; sequence only where a real dependency exists (spec →
build → gate review). Give each a context packet (§4). Producers work from the approved
spec, TDD-style.

## 4. Context each specialist receives (and must NOT receive)

Each gets: the approved spec/plan, the specific surface it owns, and the acceptance
criteria (the prompt-brief Done-criteria where one exists). A **gate reviewer must NOT
receive the producer's reasoning** — its fresh-context ignorance is the value (P5).
Pass the diff/artifact to the gate, not the author's rationale.

## 5. Synthesis rule

Enforce the **engineering challenge** on every claim: no "it works" without the check
that shows it. Collect each gate's verdict (PASS / CONCERNS / FAIL) into the **Change
Record**; preserve dissent; a single blocking FAIL stops the merge. Never average a
FAIL into a soft pass.

## 6. Closing gate

**`completion-auditor` runs last** on the assembled work — it re-checks ground truth
(refs advanced, CI green, STATE updated, Done-criteria met) before anything is reported
done. Route the code to `code-reviewer` and confirm the right CODEOWNERS gates cleared.

## 7. Degradation (pack absent)

If a required gate's pack is absent, mark that control **UNVERIFIED**, lower confidence,
and say so — never silently ship a gated surface ungated (§9.3). If the architect seat is
unavailable, do not let a producer self-spec a gated change; escalate instead.
