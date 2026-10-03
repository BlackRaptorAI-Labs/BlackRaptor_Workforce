# Contributing to BlackRaptor Workforce

## What this repository is

This repository is the built release of five Claude Code agent packs: engineering, council,
marketing, hardware, and core. The files here are produced from a private source repository by a
build step. We review every change here, then make it in that source, where it passes the same
checks as our own changes before it ships.

## What you can do

- **Open an issue.** Pick the template for the pack you used. Tell us the pack version (paste the
  `/workforce-doctor` output), the agent or skill, what you asked, what it did, and what you
  expected. A defect report with those five things is the most useful thing you can send.
- **Open a pull request.** Edit the agent or skill file here and explain the miss your change
  prevents. A maintainer reviews it. If we accept it, we port it into the private source and it
  ships in a later release. Your pull request is closed when that release goes out, and you are
  credited by name in the pack's `CHANGELOG.md`.
- **Ask a question.** Use the template for the pack you are asking about and say it is a question.

## What we will not merge

- Edits to the operating contract block (the text between `CORE-CONTRACT-START` and
  `CORE-CONTRACT-END` in agent and skill files).
- Edits to hooks (`core/hooks/`) or to the verdict schema (`verdict-schema.json`).
- Any change that adds a performance, speed, cost, or quality claim without a measurement we can
  re-run.

## The four commitments

Every agent here works under four commitments, and every contribution must keep them: nothing
invented (no source, standard, quote, or number that cannot be traced to something real), nothing
hidden (uncertainty and gaps are stated where the reader sees them), nothing half-done (no
placeholders where the work could have been done), and nothing unaccountable (every output records
what governed it and what was checked).

## How long to expect

A maintainer reads new issues and pull requests within 7 days. Porting an accepted change waits for
the next release that carries it; there is no fixed date.

## Security problems

Do not open a public issue. See [SECURITY.md](SECURITY.md).
