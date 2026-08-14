# Why development-team-agents Exists

## The vision

AI agents can write most of the code now. The hard part was never the typing —
it's trust. How do you let agents build and ship to production without either
pretending you're a 50-person org with a change-advisory board, or crossing your
fingers and hoping the model got it right this time? Most answers are one of two
failures: ceremony nobody follows, or no controls at all.

This project is a third answer. **The vision: help everyone build better
software — safely, auditably, and fast — by giving a solo developer or a tiny
team the governance of a mature engineering organization, run by agents and
enforced by machines, with a human always on the signature line.**

I built these agents to build my own company on infrastructure where a bad merge
reaches production in minutes. I'm sharing them so you can build yours without
learning those lessons the expensive way. — Tom Hanks

## What it is

Eighteen specialist AI agent templates and the governance around them, modeled
on how a disciplined engineering organization actually works — not a folder of
clever prompts, but a three-layer operating model:

- **Agents advise** — a `principal-architect` that orchestrates (the only agent
  that invokes others), plus engineers, `security-architect`, `privacy-counsel`,
  `compliance-officer`, `domain-compliance` (your regulated domain), QA, code
  review, DevOps/SRE, runtime security, red-team, and technical writing. They
  draft, build test-first, and review.
- **Humans decide** — every sensitive change carries a signed **Change Record**:
  the agent's PASS/CONCERNS/FAIL verdict is *evidence*; your signature is the
  *control*. Overruling a FAIL forces a written risk acceptance with a revisit
  date.
- **Machines enforce** — a fail-closed path-guard hook, a CI check that blocks
  gated changes lacking a Change Record, sparse CODEOWNERS for a real two-person
  rule on the dangerous few percent, and branch protection. What the prompts ask
  agents not to do, the machinery makes them unable to do.

The team answers *"are we building the thing right?"* — and hands your release a
trail an auditor can follow.

## The strengths

**1. Governance is mechanical, not aspirational.** "Be careful" prompts wear
off; machinery doesn't. Changes are tiered — **Tier 1** routine merges on green
CI; **Tier 2** requires a signed Change Record or CI blocks the merge; **Tier 3**
(auth, schema, remote execution, CI config, your regulated domain) additionally
requires a second person's code-owner approval, and a local hook stops agents
from editing those paths at all.

**2. Five blocking gates with real teeth.** Security, privacy, compliance,
domain, and schema agents produce Change-Record-ready verdicts. A FAIL is a stop,
not a suggestion — and overriding one leaves a written, dated record of who
accepted what risk and why. That record *is* the audit evidence.

**3. Evidence over confidence.** Agent verdicts are structured, cite specifics,
and drop cleanly into the Change Record. The `red-team-reviewer` is read-only by
design and **complements, never replaces, a human penetration test** — it says
so, unprompted, in every report.

**4. Disagreement is preserved.** When an agent blocks and a human overrules, the
dissent stays on the record — so a bad call is traceable and correctable later.
Your decisions get a memory.

**5. The team is a set of coaching records, not static prompts.** When an agent
misses — said PASS and a defect shipped — the miss is logged and the agent's
definition is amended with a concrete example of the failure. A companion
agent-evals convention catches regressions before they ship. The kit gets
sharper the more it's used.

**6. The human stays accountable.** The Change Record exists precisely because a
model can be wrong; the signature keeps a person answerable for every
consequential change. Advise → decide → enforce.

**7. Battle-tested, not theoretical.** This was extracted from a production
platform where merge-to-main deploys straight to production, one developer runs
the whole show, and the controls had to be the compensating story for a
no-staging, solo-developer shop. It earned its rules in production.

## Intended use

- **Solo developers and tiny teams** shipping straight to production with AI
  doing much of the work, who need it to be safe and auditable without pretending
  to be an enterprise.
- **Startups** that want SOC 2 / ISO-style compensating controls in place from
  the first commit, so the audit later is a formality, not a scramble.
- **Teams in regulated domains** (fill `domain-compliance` for HIPAA, SOX/PCI,
  GDPR-heavy, gov/FedRAMP) that need compliance reasoning in the loop, not bolted
  on after.
- **Anyone letting agents touch a production codebase** who wants a human on the
  signature line and a trail that proves the control operated.

It is **not** a substitute for a real security review, a real auditor, or your
own judgment. The local hook is a seatbelt, not a wall; the server-side controls
are the enforcement of record. Compliance framing here is a design pattern, not
legal advice.

## Why you'd want it

Because the alternative to governed agents isn't ungoverned genius — it's a
production incident you can't explain to a customer, an auditor, or yourself.
The questions that sink AI-assisted teams are knowable in advance — *did a human
approve this? was the security gate actually run? can we prove it? what happens
when the model is confidently wrong?* — and this kit makes the answer "yes, and
here's the record" the path of least resistance. It never gets tired, never skips
the gate to hit a deadline, and writes down what it decided and why.

## Honest limits

This kit practices what it preaches, so here is its own CONCERNS verdict:

- The local hook is **bypassable by a determined actor** — server-side controls
  (CI + CODEOWNERS + branch protection) are the real enforcement.
- Agent verdicts are only as good as the model and the context you give them; the
  human signature is there because the model can be wrong.
- The solo-mode design (0 blanket approvals + code-owner-only review) depends on
  GitHub branch-protection behaving as documented — **run the verification
  tests** in `docs/branch-protection-checklist.md` before trusting it.
- Compliance framing (SOC 2-style compensating controls) is a design pattern, not
  legal advice or a certification. Confirm with your auditor.

## Provenance & contact

Created by **Tom Hanks (BlackRaptor AI)**, who built these agents to build his
own companies, and is sharing them with the world. Companion to
the **[BlackRaptor Agents — council](https://github.com/BlackRaptorAI/BlackRaptor_Agents/tree/main/council)**
executive advisory team from the same author — that team decides *what* to build;
this one builds it *right*. Keep this attribution and a link back to the source
repository (https://github.com/BlackRaptorAI/BlackRaptor_Agents/tree/main/development) with any copy,
port, or derivative — and if you improve them, share it back so everyone builds
better software.

**Contact is through GitHub only** — open an issue or start a discussion on this
repository. No other channel is monitored.
