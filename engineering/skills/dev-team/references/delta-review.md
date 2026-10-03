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

## Round cap

The two-round cap still applies: the original review plus one re-review after a fix. A third round
means the change needs re-scoping or a human ruling.
