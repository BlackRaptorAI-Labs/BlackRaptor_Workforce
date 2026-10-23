# Customization guide (~30 minutes)

The agents carry `{{...}}` slots for facts about your project (your test command, where specs live,
your regulated domain). You fill them once, in your project context file, and every agent reads them
from there. This guide takes you from install to a working, governed agent team on your repo.

## 1. Install the pack, then run one command

Install from the marketplace in Claude Code:

```
/plugin marketplace add BlackRaptorAI-Labs/BlackRaptor_Workforce
/plugin install blackraptor-engineering@blackraptor
```

This also installs `blackraptor-core`. The agents, skills and commands load from the plugin.

The enforcement files must live in your repo, because Claude Code and your CI read them from there.
From your repo root, in Claude Code, run:

```
/workforce-init
```

It asks at most three questions: the install mode, whether to turn on Claude Code's sandbox for this
project (default yes), and your test command (it suggests one from `package.json`, `pyproject.toml`
or a `Makefile`, and records your lint and typecheck commands the same way). Then its script writes the
files below, and the command runs `workforce-doctor`. You can skip the questions: `/workforce-init --mode copy`.

The three modes:

- **plugin** (default): your repo's `.claude/settings.json` names the BlackRaptor marketplace and the
  packs you have installed, so a collaborator who opens and trusts the repo is offered the same packs.
- **copy**: the engineering agents and the skills they use are copied into `.claude/agents/` and
  `.claude/skills/`, with a checksum file and a CI job that fails when a copy is edited. Use it when
  the packs must travel with the repo (for example, a cloud session, which does not install plugins
  that a repo's settings name). Copy mode installs the agents, skills and the Tier-3 hook only; the
  Stop hook, draft gate, onboarding hook and the five slash commands come from the core plugin and are
  not present; use plugin mode or run the validator by hand.
- **user**: nothing goes into the repo except your project values and the installed list. The
  Tier-3 hook and the Change Record check do not run in this mode; `workforce-doctor` says so.

What it writes (every file is listed with its checksum in `.claude/workforce-installed.json`):

| File | Mode | What it is |
|---|---|---|
| `.claude/hooks/protect-tier3.py` | plugin, copy | the Tier-3 protection hook; it also blocks commands that reach a live system (cloud, cluster, deploy, remote host, remote database) |
| `.claude/live-commands-allow.txt` | plugin, copy | empty; your read-only exceptions to the live-system check, one regular expression per line, each matching one whole command (for example `aws sts get-caller-identity`). Only you edit it: the hook protects it. `--remove` deletes it only while it is still empty |
| `.claude/gates-allow.txt` | you add it | optional; your project's own gate agents, one name per line. Only an agent on the core gate list, a council seat, or this file may sign a verdict block. Only you edit it: the Tier-3 hook protects it |
| `.claude/settings.json` | plugin, copy | the hook entry, the sandbox (if you said yes), and in plugin mode the marketplace and packs; merged key by key into an existing file |
| `.github/workflows/change-record-required.yml` | plugin, copy | the Change Record CI check |
| `.gitignore` | plugin, copy | one line, `.claude/hooks/tier3-attempts.log`, so the hook's log of blocked attempts stays out of `git status`; created if absent, added only if missing, and the only line `--remove` takes out |
| `.claude/skills/gate-verdict-format/validate_verdict.py` and `verdict-schema.json` | plugin, copy | the verdict validator the CI check runs |
| `.claude/agents/*.md`, `.claude/skills/<name>/` | copy | the engineering agents and the skills they name |
| `.claude/review-copies.sha256`, `.claude/check-review-copies.py`, `.github/workflows/review-copies.yml` | copy | the checksum file, the guard script and its CI job |
| `BUSINESS-CONTEXT.md` | all | adds `TEST_CMD`, `LINT_CMD`, `TYPECHECK_CMD` rows to the `## Project values` table; other rows are never touched |
| `.claude/workforce-installed.json` | all | the installed list: pack versions, mode, date, and every file with its sha256 |

It never overwrites a file of yours: a different file already at one of these paths is skipped and
reported, and an agent of your own in `.claude/agents/` is never touched. Commit the files it lists.

Later: `/workforce-init --upgrade` after you update the packs (it lists added, changed and removed
files, and in copy mode stops before deleting a copy the new packs no longer ship), and
`/workforce-init --remove` to take it all out again (a file you changed since the install is kept and
reported). `--dry-run` shows what any of these would do without writing.

If the sandbox is on and a later run cannot write under `.claude/` (the sandbox protects that folder),
Claude asks you before running it outside the sandbox.

## 2. Record your project values (10 min)

Agents load from the installed pack, so you do not edit their files. Instead, add a
`## Project values` table to `BUSINESS-CONTEXT.md` at your repo root (the `context-onboarding`
skill creates that file), one row per slot, and fill the ones your project uses:

```markdown
## Project values

| Slot | Value |
|---|---|
| TEST_CMD | npm test |
| SPEC_DIR | docs/specs |
| REGULATED_DOMAIN | HIPAA health records |
```

Six slots are gate-critical. If one is unset when an agent needs it, a gate returns
COULD NOT ASSESS and names it, and a producer stops and replies `MISSING VALUE: <NAME>`:

| Slot | What it is |
|---|---|
| `APPROVED_CLAIMS_DOC` | the file listing the external claims your project has approved; claims-gate passes only claims listed there |
| `REGULATED_DOMAIN` | the regulated domain your data falls under, or "none" |
| `CONSEQUENTIAL_ACTIONS` | the automated actions that are hard to undo (remote commands, bulk changes, payments) |
| `COMPLIANCE_DOCS_DIR` | the folder holding your control standards (token and session lifetimes, MFA, retention) |
| `SPEC_DIR` | the folder where feature specs live |
| `TEST_CMD` | the command that runs your test suite |

`LINT_CMD` and `TYPECHECK_CMD` are optional. `dev-team`, `/gate-review`, `/pre-merge` and `/red-team`
run them, with `TEST_CMD`, as cheap checks before any gate (lint, typecheck, changed-file tests, full
suite). An unset one is reported as "not configured" and skipped; it is never a COULD NOT ASSESS.

Every slot the engineering and core packs use is listed below, with the files that use it. Fill the
ones that apply; leave out the rest.

<!-- PLACEHOLDER-TABLE-START (generated by _eval/proofs/2026-10-plan/phase3/gen_placeholder_table.py from the built tree; do not hand-edit) -->
| Slot | Gate-critical | Used in |
|---|---|---|
| `AI_STACK_SUMMARY` |  | agent `ai-ml-engineer` |
| `APPROVED_CLAIMS_DOC` | yes | agent `claims-gate` |
| `ARCH_STACK_SUMMARY` |  | agent `principal-architect` |
| `AUDIT_ENTITY` |  | agent `backend-engineer`, agent `compliance-officer`, agent `operational-readiness` |
| `AUTH_PROVIDER` |  | agent `security-operations` |
| `BACKEND_STACK_SUMMARY` |  | agent `backend-engineer` |
| `BUILD_CMD` |  | agent `completion-auditor` |
| `CI_CHECKS` |  | agent `code-reviewer`, agent `devops-sre`, agent `infra-reviewer`, agent `qa-test-engineer` |
| `CLOUD_SECURITY_BLOCKS` |  | agent `security-operations` |
| `COMPANY` |  | agent `ai-ml-engineer`, agent `backend-engineer`, agent `code-reviewer`, agent `compliance-officer` and 14 more |
| `COMPLIANCE_DOCS_DIR` | yes | agent `compliance-officer` |
| `COMPLIANCE_FRAMEWORKS` |  | agent `compliance-officer` |
| `COMPONENT_LIB` |  | agent `ux-designer` |
| `CONSEQUENTIAL_ACTIONS` | yes | agent `operational-readiness` |
| `CONSTANTS_PKG` |  | agent `backend-engineer` |
| `CORE_ENGINE` |  | agent `backend-engineer`, agent `qa-test-engineer` |
| `CORE_LOGIC_NAME` |  | agent `backend-engineer` |
| `COVERAGE_FLOOR` |  | agent `backend-engineer`, agent `qa-test-engineer` |
| `CRITICAL_COVERAGE` |  | agent `backend-engineer`, agent `qa-test-engineer` |
| `DEP_LIST` |  | agent `principal-architect` |
| `DESIGN_SYSTEM` |  | agent `ux-designer` |
| `DESIGN_SYSTEM_NAME` |  | agent `qa-test-engineer`, agent `ux-designer` |
| `DESIGN_SYSTEM_SPEC` |  | agent `ux-designer` |
| `DOMAIN_AUTHORITY` |  | agent `domain-compliance` |
| `DRIFT_EXAMPLE` |  | agent `technical-writer` |
| `DUAL_WRITE_EXAMPLE` |  | agent `qa-test-engineer` |
| `EDGE_STACK_SUMMARY` |  | agent `edge-agent-engineer` |
| `ENFORCEMENT_LIVENESS_EXAMPLE` |  | agent `security-architect` |
| `FLEET_SUMMARY` |  | agent `operational-readiness` |
| `FORWARD_SPEC_DIR` |  | agent `technical-writer` |
| `FRONTEND_SCALE_ROWS` |  | agent `frontend-engineer` |
| `FRONTEND_STACK` |  | agent `ux-designer` |
| `FRONTEND_STACK_SUMMARY` |  | agent `frontend-engineer` |
| `FRONTEND_TEST_CMD` |  | agent `frontend-engineer` |
| `I18N_JURISDICTION_NOTE` |  | agent `ux-designer` |
| `I18N_MARKETS` |  | agent `ux-designer` |
| `INFRA_PATHS` |  | agent `backend-engineer` |
| `INFRA_PATHS_BARE` |  | agent `code-reviewer`, agent `devops-sre`, agent `infra-reviewer` |
| `INFRA_SCALE_TARGET` |  | agent `devops-sre` |
| `INFRA_STACK_SUMMARY` |  | agent `devops-sre` |
| `INJECTION_VECTORS` |  | agent `security-architect` |
| `LINT_CMD` |  | agent `backend-engineer`, command `/gate-review`, command `/pre-merge`, command `/red-team` and 1 more |
| `LOG_LIB` |  | agent `backend-engineer`, agent `code-reviewer` |
| `MONOREPO_UNIT` |  | agent `backend-engineer` |
| `MSG_BUS` |  | agent `edge-agent-engineer` |
| `MSG_TOPICS` |  | agent `backend-engineer` |
| `MSG_TOPICS_SHORT` |  | agent `qa-test-engineer` |
| `MSG_TOPIC_INJECTION` |  | agent `red-team-reviewer` |
| `OPERATOR_DATA_TYPES` |  | agent `ux-designer` |
| `OPERATOR_ROLES` |  | agent `operational-readiness` |
| `OPERATOR_ROLE_COUNT` |  | agent `operational-readiness` |
| `PAGE_COUNT` |  | agent `ux-designer` |
| `PERMISSION_GUARD` |  | agent `ux-designer` |
| `PKG_ECOSYSTEMS` |  | agent `security-architect` |
| `PKG_SCOPE` |  | agent `completion-auditor` |
| `PLAN_DIR` |  | `github/pull_request_template.md`, agent `principal-architect`, command `/new-feature` |
| `PLATFORM_NAME` |  | agent `completion-auditor`, agent `compliance-officer`, agent `data-engineer`, agent `domain-compliance` and 8 more |
| `PLATFORM_OVERSIGHT_DISCIPLINE` |  | agent `operational-readiness` |
| `PRIVACY_REGIMES` |  | agent `security-operations` |
| `REGULATED_DATA` |  | agent `operational-readiness` |
| `REGULATED_DOMAIN` | yes | agent `domain-compliance` |
| `REGULATED_DOMAIN_DOCS` |  | agent `domain-compliance` |
| `REMOTE_AGENTS` |  | agent `security-architect`, agent `security-operations` |
| `ROLE_COUNT` |  | agent `principal-architect` |
| `SCALE_TARGET` |  | agent `backend-engineer`, agent `qa-test-engineer` |
| `SCHEMA_DIR` |  | agent `code-reviewer` |
| `SCHEMA_OWNER` |  | agent `backend-engineer`, agent `code-reviewer` |
| `SCHEMA_PATH` |  | agent `backend-engineer`, agent `data-engineer`, agent `principal-architect` |
| `SECOND_APPROVER` |  | `github/pull_request_template.md`, command `/gate-review`, command `/pre-merge` |
| `SECRETS_STORE` |  | agent `security-architect` |
| `SEC_ATTACK_SURFACES` |  | agent `security-architect` |
| `SHELL` |  | agent `completion-auditor` |
| `SPEC_DIR` | yes | `github/pull_request_template.md`, agent `code-reviewer`, agent `legal-docs-writer`, agent `principal-architect` and 4 more |
| `SPEC_RANGE` |  | agent `technical-writer` |
| `TENANT_FILTERS` |  | agent `security-architect` |
| `TENANT_ROLES` |  | agent `security-architect` |
| `TEST_CMD` | yes | agent `backend-engineer`, command `/gate-review`, command `/pre-merge`, command `/red-team` and 1 more |
| `TEST_FRAMEWORK` |  | agent `ai-ml-engineer`, agent `backend-engineer`, agent `frontend-engineer`, agent `qa-test-engineer` |
| `TRUST_BOUNDARIES` |  | agent `security-architect` |
| `TYPECHECK_CMD` |  | command `/gate-review`, command `/pre-merge`, command `/red-team`, skill `dev-team` |
| `TYPES_PKG` |  | agent `backend-engineer`, agent `frontend-engineer` |
| `TYPOGRAPHY` |  | agent `ux-designer` |
| `UI_INTERACTION_EXAMPLES` |  | agent `ux-designer` |
| `VALIDATION_LIB` |  | agent `ai-ml-engineer`, agent `backend-engineer`, agent `code-reviewer`, agent `qa-test-engineer` and 1 more |
| `YOUR_HANDLE` |  | `github/pull_request_template.md` |

86 slots, generated from the built tree.
<!-- PLACEHOLDER-TABLE-END -->

## 3. Define your Tier-3 paths (10 min — the important part)

Tier 3 = code where a mistake is a security incident, data loss, or a
regulatory event. Typically: authentication/authorization, database schema and
migrations, anything that executes commands remotely, CI/CD configuration, and
your regulated domain's module. Encode the SAME list in two places (they
must stay in sync — `devops-sre`'s persona says so too):

1. `.claude/hooks/protect-tier3.py` → `TIER3_PREFIXES` / `TIER3_FILES`
2. `.github/workflows/change-record-required.yml` → the `GATED` list
   (Tier 2 surfaces belong here too — privacy-sensitive and
   data-of-record paths that need a Change Record but not a second key)

The enforcement config protects itself: keep `.github/`, `.claude/hooks/`, and
`.claude/settings.json` in both lists. The owner approves every pull request, while write access stays with the owner and one agent account (the branch-protection checklist says how); required checks and the owner's approval gate the merge.

## 4. Trim the roster (5 min)

With a marketplace install the agent files live in the pack, so you do not delete them. An agent you
do not need is simply never dispatched; it costs only its description in each session. If
your project has no regulated domain, set `REGULATED_DOMAIN` to "none" and mark its gate row N/A in
the Change Record template. If the platform automates anything irreversible, keep
`operational-readiness` in play: it is the gate that keeps a human in the loop. Orchestration is not
an agent: the `dev-team` skill runs in your own session and holds no gate.

**Adding a specialist the kit doesn't ship** (e.g. a `mobile-engineer`, a
`data-scientist`): copy the closest
existing agent into your repo's `.claude/agents/`, keep the house structure
(frontmatter, reasoning-method line, mission, boundaries, and — if it gates — the
verdict block), and give it a distinct reasoning method and a new name.

## 5. GitHub setup (human-only, 10 min)

1. Agents and the build account open pull requests; they must not be admins on the repo. You approve and merge.
2. Branch protection per the engineering pack's `docs/branch-protection-checklist.md`, or
   `/workforce-init --setup-branch-protection` from your own terminal: require PRs, **1** required
   approval (yours), dismiss stale approvals, require approval of the most recent push, required
   checks = `head-suite`, `base-suite`, your CI and `change-record-required`, up to date with the
   base branch. The owner approves every pull request, while write access stays with the owner and one agent account (the branch-protection checklist says how); required checks and the owner's approval gate the merge.
3. **Run the verification tests in the checklist.** Do not skip them.

## 6. Prove the hook

Start `claude` from your repo root and ask it to edit a Tier-3 file. It must be blocked. If it isn't:
check that you launched from the repo root (project config binds at session start) and that the
`.claude/settings.json` and `.claude/hooks/protect-tier3.py` you copied in step 1 are committed.
Intentional Tier-3 work: `BR_ALLOW_TIER3=1 claude` (the override is logged).

The same hook blocks a command that reaches a live system: `aws`, `gcloud`, `gsutil`, `bq`, `az`,
`kubectl`, `helm`, `terraform`/`tofu` apply, destroy, import and state, `pulumi` up and destroy,
`cdk` deploy and destroy, `serverless`/`sls` deploy, `flyctl`, `heroku`, `vercel --prod`, `ssh`,
`scp`, `sftp`, `rsync` to a remote host, and `psql`, `mysql`, `mongosh` or `redis-cli` given a host
other than localhost (a connection URL naming localhost or 127.0.0.1 is local). It also blocks commands that
publish or send data out: `gh pr merge`, `gh release`, `gh repo delete`/`edit`, `gh secret`, `gh variable`,
a `gh api` call that is not a GET, a forcing or deleting `git push`, `npm`/`yarn`/`pnpm publish`, `twine upload`,
`cargo publish`, `gem push`, `docker push`/`login`, `nc` to a remote host, and `curl`, `wget` or `http` sending
data or a POST, PUT, PATCH or DELETE to a host that is not local. It looks through `sh -c`, `env`, `sudo`, `$(...)` and full
paths, an alias defined on the same line, and a heredoc fed to a shell; it blocks a pipe into a shell
(`| sh`, `| bash`) and `curl -K`, and checks `python -c` and `node -e` text, best effort, for a live
tool or a call to a remote host. Agents do not run these; you run them yourself, add a read-only one to
`.claude/live-commands-allow.txt`, or start a session with `BR_ALLOW_LIVE=1 claude` (logged). Like the
Tier-3 check, it blocks the direct forms and catches accidents, not a determined actor. It does not see
repo scripts, Makefile targets, copied or renamed binaries, PATH shadowing, flags held in variables,
hosts from environment variables, or interpreters running files; a sandbox network allowlist is the
boundary for those. Then run the `workforce-doctor` skill to confirm the install.

## 7. First feature

Run `/new-feature <a small, low-stakes outcome>` and take it end to end —
definition interview, sliced plan, TDD build, `/gate-review`, signed Change
Record, `/pre-merge`, merge. Shake down the process where mistakes are cheap.
When an agent misses, log it (the engineering pack's `docs/AGENT-RETROS.md` is
the template) and record the fix in your project values or your own agent copy —
that loop is what makes the team yours.
