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
   - **Sandbox**: turn on Claude Code's sandbox for this project, so shell commands can write inside
     the repo and the temporary folder, and not elsewhere in the home folder (default yes).
   - **Test command** (`TEST_CMD`), suggesting the one found; mention the lint and typecheck
     commands found, which are recorded too unless the user says no.
   If the repo already has `.claude/workforce-installed.json`, do not ask: offer `--upgrade` or
   `--remove` instead.
4. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/workforce_init.py --yes` with the answers as
   `--mode`, `--sandbox yes|no`, `--test-cmd`, `--lint-cmd`, `--typecheck-cmd` (or the arguments
   given). Show the user its output as it printed it.
   - Exit 3 on `--upgrade` means it stopped before deleting copies the newer packs no longer ship.
     Show the list it printed and ask whether to delete them; only on a yes, run it again with
     `--upgrade --confirm-removals`.
   - If the sandbox is already on and the script cannot write under `.claude/` ("Operation not
     permitted"), say so and run the same command again outside the sandbox; the client asks the
     user first. Never change the sandbox settings to get around it.
5. After an install or an upgrade, run the `workforce-doctor` skill and report its result. After a
   remove, list any files the script kept because they changed since the install.
6. Tell the user which files to commit (the script lists them), and that `--remove` undoes the
   install.
