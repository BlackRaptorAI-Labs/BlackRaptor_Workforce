# Contributing to development-team-agents

Thanks for wanting to make the team better. Contributions are licensed under
Apache-2.0 (the license's §5 applies — no separate CLA).

## The contribution we want most: agent misses

This kit's core idea is that agent definitions are **coaching records** — they
improve when real-world failures get fed back into them. If you run these
agents and one of them misses (said PASS and a defect shipped; blocked
something it shouldn't have, repeatedly; kept violating its own instructions),
that experience is gold.

Open a PR that amends the agent file, and include in the description:

1. **What happened** — the change, what the agent said, what went wrong.
2. **Root-cause class** — instruction gap, context gap, knowledge gap, or
   model-judgment limit (see docs/AGENT-RETROS.md for definitions).
3. **The amendment** — prefer adding a *concrete example of the failure* to the
   persona over another abstract rule; examples steer models better.
4. **Re-run evidence** — did the amended agent catch it on the same input?

Use the "Agent miss report" issue template if you'd rather report than patch.

## Other welcome contributions

- **New role agents** — a persona we're missing (tech-writer? data-scientist?
  mobile?). Follow the house structure: frontmatter, mission, review
  lens/conventions, hard boundaries, and — if it gates — the
  PASS/CONCERNS/FAIL Change-Record verdict paragraph.
- **Domain adaptations** — `domain-compliance` variants for HIPAA, SOX/PCI,
  GDPR-heavy, gov/FedRAMP, etc. These can live in `adaptations/<domain>/` with
  a short README on what you changed and why.
- **Enforcement improvements** — hook coverage, CI-check robustness, the
  branch-protection recipe (especially reports of how GitHub's settings behave
  on different plans — the 0-approvals + code-owners combination is the
  load-bearing assumption; evidence welcome).
- **Docs** — anything that shortens the path from clone to first gated merge.

## House rules

- **Keep the attribution.** The NOTICE file, the Tom Hanks / BlackRaptor AI
  credit, and a link back to this repository travel with every copy, port, and
  derivative (Apache 2.0, Section 4d).
- Keep placeholders in `{{DOUBLE_BRACE_SNAKE_CASE}}` and reference
  CUSTOMIZATION.md when you add one.
- No company-specific content — templates must be generic. PRs that leak your
  own internal paths/names will be asked to sanitize (we've been there).
- Agent files stay lean (~2 pages max). If a persona needs more, move
  reference material into a doc or skill it reads.
- One logical change per PR; conventional commit messages
  (`feat(agents): ...`, `fix(hook): ...`, `docs: ...`).
- Be kind in review. Verdicts are for code, not people.

## Testing your change

For hook changes, run the test block in `claude/hooks/README` (or add cases).
For agent changes, include a before/after transcript snippet showing the
behavioral difference on a realistic input.

## Questions / ideas

Open a Discussion. Show-and-tell posts about your adaptation — stack, domain,
what you kept, what you dropped — are actively encouraged; they're how the
next person finds their starting point.

## Contact

**GitHub only** — issues and discussions on this repository. No other channel
is monitored.
