# Facts pack (Step 0 of any review with more than one agent)

Produced once, by `completion-auditor`, before reviewers are dispatched. Every reviewer receives it
as a cited input and cites it; no reviewer re-derives these facts. Every fact is read at the
reviewed commit, never from the working tree.

Set two variables first and record them at the top of the pack:

```
REVIEWED=<the commit under review>      # git rev-parse HEAD at dispatch time
LAST=<the last commit already reviewed>  # or the merge base: git merge-base origin/main "$REVIEWED"
```

## 1. Changed files since the last reviewed commit

```
git diff --name-status "$LAST" "$REVIEWED"
git diff --name-status "$LAST" "$REVIEWED" | wc -l
```

## 2. Dependency-graph consistency

Every item the plan says depends on another names one that exists, and nothing depends on a later
step. For a plan with numbered items, list each `depends on` reference and confirm its target:

```
git show "$REVIEWED":<plan path> | grep -nE 'depends on|blocked by|after step'
```

Report each broken or forward reference by line.

## 3. ID coverage (plan versus audits or tests)

Every finding or requirement ID the plan must cover appears in it, and every test the plan cites
exists at the reviewed commit:

```
comm -23 <(grep -oE '<ID pattern>' <audit or requirement file> | sort -u) \
         <(git show "$REVIEWED":<plan path> | grep -oE '<ID pattern>' | sort -u)
git ls-tree -r --name-only "$REVIEWED" | grep -E '<test path pattern>'
```

List the missing IDs. A count without its command is not a fact.

## 4. File-ownership collisions

Two plan items, or two producers, that change the same file in the same wave:

```
git show "$REVIEWED":<plan path> | grep -oE '[A-Za-z0-9_./-]+\.[a-z]{1,5}' | sort | uniq -d
```

## 5. Every count, with its command

Each number in the pack is followed by the command that produced it and its raw output.

## Test evidence table (from the producer)

When the change includes tests, attach the producer's table. `test-auditor` and `completion-auditor`
start from it; the MEASURED line a test-quality PASS rests on comes from `completion-auditor`'s own
run.

| guarantee | test | type | result | evidence path |
|---|---|---|---|---|
| <the behaviour it protects> | <file::test name> | unit / integration / e2e | MEASURED RED then GREEN at <sha> | <path to the run log> |

A test counts as RED only if it was compiled, executed and failed for the intended reason.

## Where the pack goes

`completion-auditor` writes the pack only to the path the orchestrator names in the dispatch, and
leaves no scratch file in the tree.
