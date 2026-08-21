<!-- TEMPLATE — not onboarded -->
# Engineering context — extension question set (repo-native, R10)

The engineering pack's EXTENSION set for the `context-onboarding` interview. Engineering is
repo-native: the shared CORE block (what it is · who it's for · stage · how money comes in ·
priorities · off-limits · role) is asked first and writes the **business** layer to the repo-root
`BUSINESS-CONTEXT.md`; these technical questions run AFTER core and write the **technical** layer to
the repo-root `CLAUDE.md`. Do not re-ask core ground. Same provenance/approval rules.

Run this only for a **bare repo** (no `CLAUDE.md`, no business context). For a **populated repo**,
skip the welcome and instead offer a short "review and fill gaps" pass.

1. **Project purpose** — what this repo builds (deepens core "what it is" at the technical level).
2. **Language + stack** — primary languages, frameworks, key libraries, package manager.
3. **Environments** — local / staging / prod; how they differ; how to run locally.
4. **Build / test commands and expectations** — the exact commands; coverage/CI expectations.
5. **Definition of done** — ask VERBATIM (gate-cleared SHIP 2026-08-21):
   > Definition of done for a code change: beyond lint, tests, and build passing in CI, is
   > there anything you require before a PR merges or a version publishes? For example: an
   > updated README, a change record for gated paths, a manual test against a real client, or
   > a version bump and tag. If your docs already describe your actual practice, just say
   > "as documented."
6. **Merge / deploy rules** — branch protection, required reviews, who deploys, gated surfaces.
7. **Conventions and environments** — ask VERBATIM (gate-cleared SHIP 2026-08-21):
   > Conventions and environments: is there anything the agents should know that isn't in the
   > repo docs? For example a coding style beyond what your linter or formatter enforces, how
   > you test locally against a real client, which channels you're targeting for launch, or
   > anything you'd rather the team never touch (for example CI or publish workflows).
   > "Nothing extra" is a fine answer.

Answers write to `CLAUDE.md` (technical) with `[doc:]`/`[user]`/`[unknown]` provenance; unknowns are
marked, never left silently blank.
