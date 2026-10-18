# Delta re-review

A re-review checks what changed since the last review and whether earlier findings are closed. It
does not re-review the whole plan or diff.

## Inputs (all three, or it is not a delta re-review)

1. The prior findings, by id (`F1`, `F2`, ...), each with its recorded minimum fix and proof of
   closure.
2. The diff since the last reviewed commit: `git diff <last reviewed sha> <new sha>`.
3. The reviewed commit SHA (the new one). Every fact is read at that commit.

## Output

1. **Every prior finding, first**, marked CLOSED, PARTIAL or OPEN with evidence at the new commit
   (closure-line format in the `gate-verdict-format` skill's `references/finding-contract.md`).
2. **New findings**, limited to text the diff changed, plus any Critical anywhere.
3. **Verdict:** PASS when no OPEN item at High or above remains. Otherwise CONCERNS or FAIL as usual.

## Fix-strength guard

A claimed fix is judged by the agent that raised the finding, or by `red-team-reviewer` if that
agent is not on this roster, against the recorded minimum fix and proof of closure. A fix that
closes the finding with a weaker check than the minimum fix is PARTIAL, not CLOSED. CLOSED needs the
proof of closure run, or quoted, at the new commit.

## Re-review of a fix (the eight items)

Every re-review verdict on a fix answers all eight items, each with MEASURED or CITED evidence. An item
you cannot answer is a condition, never a silent skip (D-187).

1. **Head sha.** The full sha you reviewed. If it differs from the sha in the request, say "head moved
   from X to Y" and review Y.
2. **Replay.** Every input that produced a prior finding is planted again, and the new guard fails on
   each one. Quote each failure.
3. **Red first.** The guard fails on the tree at the last reviewed sha and passes at the new one.
4. **Permitted cases.** At least three inputs the guard must allow still pass. You name them, not the
   producer.
5. **Liveness.** The guard runs on the live path: CI config includes it, and packaging and archives
   leave out what must stay private (the `enforcement-liveness` skill).
6. **Scope.** `git diff --stat <last sha> <new sha>` lists only the fix's files, or you name and rule
   on every extra file.
7. **Suite and CI.** The suite count and CI state at the new head, from completion-auditor's MEASURED
   run. A gate with no shell cites that run as CITED, with its output path.
8. **Approval line.** A PASS reads `Approved at <full 40-character sha>`. Set `rereview_of` in the
   verdict block to the last reviewed sha; the validator then requires the full sha in `artifact`. The
   verdict never merges anything.

## Round cap

The two-round cap still applies: the original review plus one re-review after a fix. A third round
means the change needs re-scoping or a human ruling.
