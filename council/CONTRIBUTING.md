# Contributing

Improvements are welcome — that's the point of sharing this. If the
Council caught something for you, or missed something it shouldn't have,
bring it back so everyone's council gets sharper.

## How to contribute

- **Found a gap or defect in an agent?** Open a GitHub issue: which
  agent, what it did, what it should have done, and (ideally) the
  question that exposed it.
- **Improved an agent?** Open a pull request against the agent file.
  Treat agent files as coaching records: say what miss your change
  prevents. Small, surgical diffs beat rewrites.
- **Built a port** (OpenAI Agents SDK, CrewAI, LangGraph, other)? Open a
  PR adding it under `docs/` or link it in a discussion — ports must
  preserve the full mechanics (see `docs/PORTING.md`); no single-prompt
  chat versions.
- **Have results or ideas?** GitHub Discussions.

## Ground rules

1. **Keep the attribution.** The NOTICE file, the Tom Hanks /
   BlackRaptor AI credit, and a link back to this repository travel with
   every copy, port, and derivative (Apache 2.0, Section 4d).
2. **Slugs are immutable.** Never rename an agent's `name:` slug —
   they're load-bearing identifiers. Personas are the adopter's business;
   the shipped agents stay nameless.
3. **Don't soften the council.** PRs that make agents more agreeable,
   remove "What You Lose," strip confidence labels, weaken the challenge
   protocol, or bypass the HITL/ethics gates will be declined. Toughness
   is the product.
4. **Charter changes are rare.** `COUNCIL.md` binds every seat; propose
   changes by issue with reasoning before opening a PR.

## Contact

**GitHub only** — issues and discussions on this repository. No other
channel is monitored.
