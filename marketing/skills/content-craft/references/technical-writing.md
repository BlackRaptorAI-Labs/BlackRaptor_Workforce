# Technical Writing — White Papers, Docs, Explainers

## The core evidence

- **Plain language works for experts too — verified, but the evidence is observational, not a controlled study.** NN/g's article ("Plain Language Is for Everyone, Even Experts") reports usability-session observations of domain experts (IT managers, a professor, a nurse practitioner), not a quantitative comprehension study — no sample size or statistics are published. Example: an IT manager praised a site for being "short, easy to digest" and criticized another for unexplained jargon; a nurse practitioner preferred simpler formatting on a medical article. Cite this as documented usability-research observation, not as a statistically established finding — the direction is well-supported across NN/g's broader body of scanning/reading research, but this specific piece is qualitative.
- **People scan, they don't read.** NN/g's long-running web reading research: front-load conclusions, use meaningful headings (a heading should carry information on its own), short paragraphs, bulleted steps for procedures.
- **Style-guide discipline.** Adopt one published style guide (Microsoft Writing Style Guide or Google Developer Documentation Style Guide — both free and public) and follow it for terminology consistency, capitalization, and UI references. Consistency is a trust signal.

## Structure standards by asset type

- **White paper**: executive summary that stands alone (the exec may read nothing else) → problem with evidence → mechanism/approach → proof or honest proof-status → implications → call to action. 6–12 pages; every figure sourced; methodology of any cited study named.
- **Explainer / compliance guide**: what the obligation is (cite the actual regulation section) → who it applies to → what satisfying it requires → how the product helps (cleared claims only) → next step. Regulation citations link to the primary source (e.g., the actual FTC Safeguards Rule text), never only to a vendor summary.
- **Documentation / how-to**: task-oriented (titles are verbs), one procedure per page, numbered steps with one action each, prerequisites first, expected result stated after each significant step.
- **Case study**: situation → obligation/problem → what was done → measurable result (only if audited/consented) → customer quote (with written consent). No composite "customers" presented as real.

## Rules

- Define every term a non-specialist reader would stumble on at first use; expand acronyms per the core's acronym rule.
- Accuracy outranks polish: a reviewed-by-SME (subject-matter expert) pass is part of the workflow for anything touching regulation — flag which statements need SME/counsel review.
- Version and date every technical document; regulatory content carries a "current as of" date.
- Readability report attached (grade level + scan-ability check: can a reader get the gist from headings alone?).
