---
name: clean-output
description: >-
  Keep AI-attribution boilerplate and authoring-tool fingerprints out of the business
  documents and code the Workforce produces. Use before delivering any document, or when
  setting up a repo, to strip "Generated with Claude"-style trailers, co-author trailers,
  and generator/authoring-tool metadata fields from delivered files. Triggers: "clean the
  output", "remove the AI boilerplate", "strip the commit trailer", "scrub file metadata
  before I send this". Does NOT remove content-provenance marks (see Boundaries).
metadata:
  version: "0.1.0"
---

# Clean output — attribution boilerplate & metadata hygiene

Business documents should read as the company's own work product, not carry tool
boilerplate. This skill removes attribution noise and authoring-tool fingerprints from what
the Workforce delivers. It is document hygiene, not provenance defeat — read Boundaries.

## Boundaries (hard — do not cross)

This skill NEVER attempts to remove, weaken, or obscure:
- The **text watermark** embedded in Claude-generated prose (statistical, imperceptible;
  applied globally to models launched on/after 2026-08-02; no opt-out). It is not in scope
  and cannot be stripped by editing metadata or trailers.
- **C2PA content credentials** — the signed provenance metadata on generated image files
  (.png/.jpg/.svg). These are a provenance standard, not tool boilerplate; leave them
  intact.

If a request asks to remove either of those, STOP and say so plainly — that is out of scope
for this skill and for the Workforce. Everything below concerns ordinary attribution
boilerplate and authoring-tool fingerprints only.

## 1. Document body — no AI-attribution boilerplate

When any agent produces a deliverable (.md, .docx, .pdf source, slides, email text):
- Do NOT add lines like "Generated with Claude", "Written by AI", "Draft produced by
  Claude", or similar attributions anywhere in the body, header, or footer.
- Do NOT add an AI-tool signature block or "created using…" credit unless the user
  explicitly asks for one.
- The document stands as the company's work product. (Provenance obligations, if any apply
  to the user's jurisdiction/industry, are the user's call to make deliberately — this
  skill does not add disclosure and does not remove any embedded watermark that carries it.)

## 2. Git commits — trailer hygiene (engineering / build repos)

Claude Code adds a co-author trailer and a "Generated with Claude Code" line to commit
messages by default. For the company's own repos, keep commits clean:
- Set the documented Claude Code option that disables the automatic commit/PR attribution
  trailer (the `includeCoAuthoredBy` setting → false in the repo or user settings). Name the
  exact file:line you changed in your report.
- When writing a commit message directly, do not hand-add the "Generated with Claude Code"
  line or a `Co-Authored-By: Claude` trailer.
- This changes only THIS project's commit style; it is a configuration choice, not a
  circumvention of anything.

## 3. Delivered files — authoring-tool metadata

Before delivering a .docx / .pdf / .pptx, scrub generator/authoring-tool fingerprint fields
from the file's document properties (e.g. the "creator" / "producer" / "application" /
"last-modified-by" fields that name the generating software or a stray account). Rationale:
standard pre-publication metadata hygiene — many organizations already strip these for
privacy. Set them to empty or to a value the user chooses (company name), never to a
misleading claim of a different named author.
- Scope: authoring-tool and account fingerprint fields only.
- Explicitly NOT scrubbed: C2PA content credentials on images (Boundaries), and any field
  the user has asked to keep.
- Report which fields were cleared on each delivered file.

## 4. What this skill will not do

Fabricate authorship (claim a named human or company wrote something they didn't), forge a
provenance record, or remove a content watermark / C2PA credential. Those are out of scope;
if asked, say so and stop.
