---
description: Install, upgrade or remove the BlackRaptor Workforce in this repo (plugin, copy or user mode)
disable-model-invocation: true
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/workforce_init.py *)
---

Set up the BlackRaptor Workforce in the current repo with one script. The script does all the
writing; you only ask the questions and run it. Never edit the files it writes by hand.

Arguments given: `$ARGUMENTS`

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/workforce_init.py --suggest` and read the JSON: the
   repo root, the packs found, any existing install, and the suggested answers.
2. If arguments were given, skip to step 4 and pass them through unchanged.
3. With no arguments, ask at most three questions, in one message, each with the suggested answer
   as the default:
   - **Mode**: `plugin` (default: the repo's settings name the marketplace and the packs, so a
     collaborator who opens and trusts the repo is offered them), `copy` (the engineering agents and
     the skills they use are copied into `.claude/`, with a checksum file and a CI guard), or `user`
     (nothing is written to the repo except the project values and the installed list).
   - **Sandbox**: turn on Claude Code's sandbox for this project (default yes). Shell commands can then
     write inside the repo and the temporary folder, not elsewhere, and no agent's shell command can write
     the enforcement files. Saying no means: enforcement files are not protected without the sandbox;
     hooks still run, but an agent with a shell can edit them.
   - **Test command** (`TEST_CMD`), suggesting the one found; mention the lint and typecheck
     commands found, which are recorded too unless the user says no. The Stop hook runs the test command
     itself as an early warning on a test-auditor or completion-auditor PASS; CI decides whether tests pass,
     on a clean machine, for the exact commit (the engineering pack's workforce-proof workflow). With no
     GitHub, `--no-ci-judge` makes the local run the judge and says it can be faked.
   - **GitHub logins** (engineering pack): the user's own GitHub login (`--owner-login`) and the login of the one
     agent or build account that has write access (`--agent-account`). GitHub counts one
     approval from anyone with write access, so keep write access to those accounts only, and the approval is the
     user's; `/workforce-doctor` lists everyone with write access and reports a FAIL for anyone else. Never read
     the login from `gh` in a session: it is the build account's, not the user's.
   - After install, tell the user to run `--setup-branch-protection` from their own terminal with an admin
     GitHub login: it asks GitHub to require workforce-proof's two checks and one approving review on the
     default branch.
   If the repo already has `.claude/workforce-installed.json`, do not ask: offer `--upgrade` or
   `--remove` instead.
4. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/workforce_init.py --yes` with the answers as
   `--mode`, `--sandbox yes|no`, `--test-cmd`, `--lint-cmd`, `--typecheck-cmd`, `--owner-login`, `--agent-account` (or the arguments
   given). Give `--test-cmd` once per test command when the project needs several (for example one per
   package in a monorepo); each must be a runner the hook reads a report from (the hooks README's "Direct
   test commands" table). Show the user its output as it printed it. `--accept-changes` (plugin mode)
   records the enforcement files as they are after a change the user made; `--accept-runner-config` (plugin
   mode) records the test runner config (the runner's config files, the package.json test scripts, and the
   startup files, pytest plugin entry points and install state of the repo's virtualenvs and node_modules)
   after the user reviewed a change to it. Both are for the user's own terminal.
   - Exit 3 on `--upgrade` means it stopped before deleting copies the newer packs no longer ship.
     Show the list it printed and ask whether to delete them; only on a yes, run it again with
     `--upgrade --confirm-removals`.
   - If the sandbox is already on, the script cannot write the files it manages and prints "cannot write
     ... run this from your own terminal" with the exact command (on macOS and on Linux, D-247). Show that command to the user and ask
     them to run it in their own terminal. Never change the sandbox settings, and never try to run it
     outside the sandbox, to get around it.
5. After an install or an upgrade, run the `workforce-doctor` skill and report its result. After a
   remove, list any files the script kept because they changed since the install.
6. Tell the user which files to commit (the script lists them), and that `--remove` undoes the
   install.
