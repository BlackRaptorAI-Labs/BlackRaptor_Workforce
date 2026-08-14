# Customization guide (~30 minutes)

The templates are parameterized with `{{PLACEHOLDERS}}`. This guide takes you
from clone to a working, governed agent team on your repo.

## 1. Run the installer

```bash
./install.sh /path/to/your/repo
```

It copies agents → `.claude/agents/`, hook/skill/commands → `.claude/`,
CI workflow + templates → `.github/`, and governance docs → `docs/`, backing up
anything it would overwrite.

## 2. Fill the global placeholders (10 min)

Search your repo's new files for `{{` and fill these, everywhere they appear:

| Placeholder | Meaning | Example |
|---|---|---|
| `{{COMPANY}}` | Your company/product name | Acme Health |
| `{{PLATFORM_NAME}}` / `{{PLATFORM_SUMMARY}}` | What the platform is, one line | patient-scheduling SaaS |
| `{{STACK_SUMMARY}}` | Tech stack, one line | Rails API, React, Postgres, GCP |
| `{{DEPLOY_MODEL}}` | What merge-to-main does | deploys to staging; prod releases are tagged |
| `{{SECOND_APPROVER}}` | The human in your two-person rule | Maria |
| `{{SECOND_KEY_TEAM}}` | GitHub team containing only that person | @acme/release-approvers |
| `{{SPEC_DIR}}` / `{{PLAN_DIR}}` | Where feature specs/plans live | docs/specs · docs/plans |
| `{{COVERAGE_FLOOR}}` / `{{CRITICAL_COVERAGE}}` | Test coverage minimums | 80% · 90% |

Tip: `grep -rn "{{" .claude .github docs CONTRIBUTING.md` lists every slot.

## 3. Define your Tier-3 paths (10 min — the important part)

Tier 3 = code where a mistake is a security incident, data loss, or a
regulatory event. Typically: authentication/authorization, database schema and
migrations, anything that executes commands remotely, CI/CD configuration, and
your regulated domain's module. Encode the SAME list in three places (they
must stay in sync — `devops-sre`'s persona says so too):

1. `.claude/hooks/protect-tier3.py` → `TIER3_PREFIXES` / `TIER3_FILES`
2. `.github/CODEOWNERS` → routes those paths to `{{SECOND_KEY_TEAM}}`
3. `.github/workflows/change-record-required.yml` → the `GATED` list
   (Tier 2 surfaces belong here too — privacy-sensitive and
   data-of-record paths that need a Change Record but not a second key)

The enforcement config protects itself: keep `.github/`, `.claude/hooks/`, and
`.claude/settings.json` in all three lists.

## 4. Trim the roster (5 min)

Delete agents that don't apply — a smaller team steers better than an idle one:

- No LLM features → delete `ai-ml-engineer.md`
- No regulated domain → delete `domain-compliance.md` (and its gate rows in the
  Change Record template); privacy + compliance remain
- No marketing function → delete `product-marketing.md`
- No edge/on-device tier → delete `edge-agent-engineer.md`
- No consequential automated actions and no operator-facing workflows → delete
  `operational-readiness.md` (and its gate row); think twice — if the platform
  automates anything irreversible, this is the gate that keeps a human in the
  loop
- No public-facing legal/policy documents to maintain → delete
  `legal-docs-writer.md`
- No intellectual property you actively protect → delete `ip-counsel.md`
- Orchestration is not an agent file: the process-only lifecycle is the
  main-session `dev-team` skill, run by your own session. No agent holds the
  `Agent` tool (in subagent context the `Agent`/Task tools are stripped, so no
  agent can invoke another) — the skill holds no gate and no content authority

**Adding a specialist the kit doesn't ship** (e.g. a `mobile-engineer`, a
`data-scientist`): copy the closest
existing agent, keep the house structure (frontmatter, reasoning-method line,
mission, boundaries, and — if it gates — the PASS/CONCERNS/FAIL Change-Record
paragraph), and give it a distinct reasoning method.

Then personalize the keepers: each file's `<!-- CUSTOMIZE -->` header marks
what to review. The deepest edits are usually `domain-compliance` (write your
regime's lens) and the engineer agents' conventions sections.

## 5. GitHub setup (human-only, 10 min)

1. Create the `{{SECOND_KEY_TEAM}}` team with ONLY your second person (write
   access). Not you — you can't approve your own PRs anyway, and a clean
   membership makes the two-person story legible.
2. Replace/merge `.github/CODEOWNERS` — **no global `*` rule**, or you'll block
   yourself on everything.
3. Branch protection per `docs/branch-protection-checklist.md`: require PRs,
   **0** required approvals, require code-owner reviews, dismiss stale
   approvals, required checks = your CI + `change-record-required`.
4. **Run the three verification tests in the checklist.** Do not skip: the
   0-approvals + code-owners combination must be proven on your plan/settings.

## 6. Prove the hook

Start `claude` from your repo root and ask it to edit a Tier-3 file. It must be
blocked. If it isn't: check that you launched from the repo root (project
config binds at session start) and that `.claude/settings.json` registered the
hook. Intentional Tier-3 work: `ALLOW_TIER3=1 claude` (logged).

## 7. First feature

Run `/new-feature <a small, low-stakes outcome>` and take it end to end —
definition interview, sliced plan, TDD build, `/gate-review`, signed Change
Record, `/pre-merge`, merge. Shake down the process where mistakes are cheap.
When an agent misses, log it in `docs/AGENT-RETROS.md` and amend the persona —
that loop is what makes the team yours.
