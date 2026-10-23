# Branch Protection Checklist — Owner Approval

Target: `main` on `{{ORG}}/{{REPO}}`.
Context: written for an owner who works with agents ({{DEPLOY_MODEL}}). The owner approves every pull
request; required checks and the owner's approval gate the merge (D-258, D-260). GitHub blocks
self-approval, and it counts one approval from anyone with write access, so the settings below are chosen for that
reality and the write list matters (D-273).

> GitHub offers two mechanisms: classic **branch protection rules** and newer
> **rulesets**. This checklist is written for classic branch protection
> (Settings → Branches). Rulesets can express the same things and add logged
> bypasses — noted where relevant. GitHub's UI changes; verify each toggle
> exists where described.

## Prerequisites (do these first)

- [ ] **Agents and the build account open pull requests; you approve and merge.** Agents push and open
      pull requests as the build or agent account, never as you, so you can approve them. Give that
      account **Write** access, never **Admin**: an admin could merge around the checks.
- [ ] Install the kit's `change-record-required.yml` into `.github/workflows/` and let it
      run once on a test PR (a check must run at least once before GitHub lets
      you mark it "required").
- [ ] `/workforce-init` installs `workforce-proof.yml` (the CI judge, D-251) into
      `.github/workflows/`. Push one branch so its `head-suite` and `base-suite` jobs
      run once.

## Settings — "Require a pull request before merging"

- [ ] **Require a pull request before merging: ON.** Direct pushes to `main`
      are the biggest single risk in a no-staging repo.
- [ ] **Required approvals: 1.** GitHub counts one approval from anyone with write access. Keep write
      access to you and one agent or build account, so the approval is yours, on every pull request an agent
      or the build account opens. Record them (`/workforce-init --upgrade --owner-login <you> --agent-account
      <build account>`); the doctor, run from your own terminal, lists everyone with write, maintain or admin
      access and reports a FAIL when anyone else has it. Keep the repo setting "Allow GitHub Actions to create
      and approve pull requests" **off**.
- [ ] **Require review from Code Owners: OFF.** Workforce uses no code-owners file; the one approving
      review above is the only approval rule.
- [ ] **Dismiss stale pull request approvals when new commits are pushed: ON.**
      Otherwise an approved pull request could gain different code and merge on the old approval.
- [ ] **Require approval of the most recent reviewable push: ON.**
      Complements the above for the same reason.

## Settings — status checks (Layer 1, where most enforcement lives)

- [ ] **Require status checks to pass before merging: ON.**
- [ ] **Require branches to be up to date before merging: ON.** In a
      deploy-on-merge repo, testing against stale `main` means deploying an
      untested combination.
- [ ] Mark **required**: your test/lint/typecheck/coverage checks,
      and **`change-record-required`** (the file-presence check).
- [ ] Mark **required**: **`head-suite`** and **`base-suite`**, source **GitHub Actions**
      (D-253). These are workforce-proof's two jobs; CI is the judge of whether the tests
      pass, and the Stop hook reads the same two. `/workforce-init --setup-branch-protection`,
      run from your own terminal with an admin login, asks GitHub for both checks (up to date with
      the base), one approving review, stale approvals dismissed and the last push approved, in one
      call; the doctor reads back what GitHub set.
      ⚠ A check is matched by its name: a second workflow with jobs named `head-suite` can
      report under the same name (measured, Amendment 8 C-2). Your review of every pull request is
      what stops an agent adding one: a new file under `.github/workflows/` is in the diff.

## Settings — the rest

- [ ] **Require conversation resolution before merging: ON.** Cheap; makes
      review questions un-ignorable.
- [ ] **Require linear history: optional.** Nice for audit-trail readability;
      adopt if you already squash-merge.
- [ ] **Allow force pushes: OFF. Allow deletions: OFF.**
- [ ] **Require signed commits: optional but recommended** for a SOC 2 story —
      cryptographically ties commits to you. Skip if it adds friction you
      won't sustain.

## The "Do not allow bypassing the above settings" / include-administrators decision

You are the admin, and GitHub does not let you approve your own pull request.

- **Recommended: OFF (`enforce_admins: false`).** Agents' pull requests still need your approval and
  the checks. Your own pull requests merge by an admin override, which GitHub shows as a bypass on the
  pull request: that record is the evidence. Keep the agent and build accounts out of the admin role.
- If you turn it ON, your own pull requests cannot merge without a second person's approval.
- Emergency path (prod down): merge the hotfix by admin override, then within 24h file a retroactive
  Change Record marked **EMERGENCY** with what/why/when.
- If you use **rulesets** instead of classic rules, prefer them for exactly
  this: bypasses are logged automatically, giving you evidence instead of a
  hole.

## Verification (do all four before trusting the setup)

- [ ] A green pull request from the build or agent account → shows **Review required** until you
      approve; your approval is dismissed if it pushes again.
- [ ] A pull request touching a gated path with no Change Record file → blocked by
      `change-record-required`.
- [ ] A pull request whose change breaks an existing test → blocked by `base-suite`.
- [ ] Your own pull request → merges only by an admin override, shown as a bypass.

## For your auditor (control description language)

Describe this as: *"Compensating controls for a single-owner environment:
(1) required CI quality gates on every pull request an agent opens, including a CI judge that runs the
base branch's own tests; (2) documented self-attestation Change Records for security/privacy/compliance
review, informed by automated analysis; (3) the owner's approval required on every pull request an
agent opens. The owner's own changes and emergency merges skip the required checks by admin override,
which GitHub records as a bypass."* Confirm acceptability with
your specific auditor — SOC 2 permits compensating controls, but acceptance is auditor-specific.
