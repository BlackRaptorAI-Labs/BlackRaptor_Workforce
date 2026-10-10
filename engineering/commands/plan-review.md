---
description: Use when an implementation plan or design needs several reviewers before code is written. Assigns a core roster plus specialists on triggers, gives each reviewer a lane and the same facts pack, and tracks earlier findings to closure on re-review. Always route plan sign-off here.
---

Review an implementation plan or design with a tiered roster. This runs in the main session, which
dispatches every reviewer as its own subagent. For a review of a diff, use `/gate-review` instead.

Inputs: the plan (path), the commit it is reviewed at, and, for a second review, the prior findings
by id. If the prior findings exist, this is a delta re-review (step 6).

1. **Pin the commit.** `REVIEWED=$(git rev-parse HEAD)`. Every repo fact in this review is read at
   `$REVIEWED` (`git ls-tree "$REVIEWED"`, `git show "$REVIEWED":<path>`), never the working tree.

2. **Facts pack first.** Dispatch `completion-auditor` alone to produce the facts pack from the
   `dev-team` skill's `references/facts-pack.md`, written to the path you name in the dispatch.
   Wait for it. Every reviewer receives the pack as a cited input and does not re-derive it.

3. **Roster.**
   - **Core 8, always:** `security-architect`, `red-team-reviewer`, `principal-architect`,
     `devops-sre`, `security-operations`, `operational-readiness`, `test-auditor`, `code-reviewer`.
     `completion-auditor` runs the facts pack (step 2) and pairs with `test-auditor` on every
     test-quality question, executing the suite or mutation `test-auditor` names.
   - **Specialists, only when the plan or diff triggers them:**

     | Trigger in the plan or diff | Add |
     |---|---|
     | Personal data, data retention, or terms and agreements | `privacy-counsel`, `ip-counsel`, `legal-docs-writer` |
     | Telemetry, or measurement, reporting and verification of regulated outputs | `domain-compliance` (and the carbon seat, where the install has one) |
     | Field devices, device messaging (for example MQTT) | `edge-agent-engineer` |
     | Web flows or user-facing screens | `frontend-engineer`, `ux-designer` |

   - Producers (the agents that build, or write tests) are never dispatched as reviewers, except where
     a trigger above names one as a findings-only seat.
   - **The plan's author never reviews that plan.** If an agent wrote the plan or design (often
     `principal-architect`, who authors specs), drop it from the roster and say so.
   - **Findings-only seats (no verdict block):** `principal-architect`, `devops-sre`,
     `security-operations`, `ip-counsel`, `legal-docs-writer`, `edge-agent-engineer`,
     `frontend-engineer`. They return the findings table only. Every other reviewer named here is a
     gate and ends with a verdict block.
   - State the roster and why each specialist was added before dispatching.

4. **Lanes.** Assign each reviewer the plan sections it owns and name them in its dispatch. Outside
   its lane a reviewer reports Critical findings only.

5. **Dispatch and collect.** In a single message, dispatch the roster concurrently, each with the
   plan, the facts pack, its lane, and the `gate-verdict-format` finding contract (one claim per row
   with class coverage, severity, minimum fix and proof of closure). Never background a reviewer.
   Your final message is the deliverable: wait for every reviewer's result before ending the turn.

6. **Delta re-review (second and later rounds).** Follow the `dev-team` skill's
   `references/delta-review.md`: every prior finding marked CLOSED, PARTIAL or OPEN at `$REVIEWED`;
   new findings only in changed text plus any Critical anywhere; PASS when no OPEN item at High or
   above remains. A claimed fix is judged by the reviewer who raised it (or `red-team-reviewer`)
   against the recorded minimum fix and proof of closure. The two-round cap applies.

7. **Merge and self-check.** Send back any row missing class coverage, minimum fix or proof of
   closure. Merge duplicates by `path:line`. Before publishing, re-check every Critical and a random
   10 percent of the other findings yourself at `$REVIEWED`, and state which ones you sampled.

8. **Cost log.** Append one line per reviewer to `.claude/plan-review-costs.jsonl`:
   `{"run": "<UTC timestamp>", "commit": "<REVIEWED>", "agent": "<slug>", "tokens": <n>, "wall_s": <n>}`,
   taken from each subagent's reported usage. Do this on every run.

9. **Output.** The roster with reasons; the merged findings table; each gate reviewer's verdict block;
   the re-check sample; for a re-review, the closure list first. Do not fill in human decisions.

$ARGUMENTS
