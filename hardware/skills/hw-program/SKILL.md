---
name: hw-program
description: Run a hardware engineering program as its technical conductor — dispatch discipline work, keep the decision register, control interfaces between disciplines, trace requirements, assess gate readiness (PDR/CDR/MRR), and author handoffs. Use for any multi-discipline hardware effort or cross-domain conflict. Triggers: "run the program", "resolve this cross-domain conflict", "assess CDR readiness", "author the manufacturer handoff".
---

# Run a hardware program

Conduct a hardware program so no contradiction between disciplines ever reaches the
manufacturer. **This skill runs in the main session, which dispatches each seat as its
own subagent** — there is no orchestrator subagent (P1/P2). It owns the register and the
interfaces; it does not do the discipline work itself.

**Delegation policy:** when a task matches a specialist's domain, delegate rather than self-perform.

## 1. When to convene

Any multi-discipline hardware effort (power / thermal / RF / firmware / mechanical /
reliability / cost / manufacturing / compliance), any cross-domain conflict, or a gate
readiness review (PDR / CDR / MRR). Load the **`hw-operating-standard`** skill first —
datasheets are ground truth, worst-case not typical, units everywhere.

## 2. Seat selection rule

Select the disciplines the decision crosses; for a full board effort that is most of the
seats. **Minimum for any gate review = the disciplines that own the gate's exit criteria.**
Reliability and cost are added to any decision that changes parts or architecture.

## 3. Dispatch instruction

**In a SINGLE message, spawn the independent disciplines as separate subagents** (Agent
tool) so power/thermal/RF/firmware/etc. analyze concurrently; sequence only real
dependencies (e.g. power tree → thermal). Give each its slice of the register + interfaces.

## 4. Context each specialist receives (and must NOT receive)

Each discipline gets: the requirement(s) it owns, the interface contracts touching it, and
the relevant locked decisions from the register. A reviewing seat must **NOT** receive the
producing seat's rationale where an independent check is the point (P5).

## 5. Synthesis rule — the decision register + interface control

Record every decision in the **decision register** (what, why, who, the ref that enacted
it) and every cross-discipline boundary in **interface control**. When two disciplines
conflict, surface it explicitly and resolve it in the register — never let both ship a
contradictory assumption. Preserve the dissent and the trade.

## 6. Closing gate

Assess **gate readiness** (PDR/CDR/MRR) against each discipline's exit criteria; the
**`hw-design-reviewer`** runs the adversarial review before any board spin, firmware
release, or purchase. **With the `blackraptor-dev` (Build) pack installed**, `completion-auditor`
confirms the register + interface control are complete and consistent before the handoff is authored;
**otherwise the main session records that completion check UNVERIFIED** and authors the handoff noting
the audit gate was not run (§9.3 — degrade, don't dangle).

## 7. Degradation (pack absent)

If a needed discipline's pack is absent, mark that domain **UNVERIFIED** in the register,
lower confidence, and flag the gate as not-ready — never author a manufacturer handoff with
a silent gap (§9.3).
