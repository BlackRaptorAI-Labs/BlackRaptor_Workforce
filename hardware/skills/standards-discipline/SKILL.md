---
name: standards-discipline
description: >-
  Apply and cite a standard, statute, regulation, or specification correctly.
  Use whenever an output invokes a designation (IEC/ISO/IEEE/UL/IPC/ETSI/FCC/CFR
  /FTC/case law) or claims conformance — "cite this standard", "is this
  compliant", "what governs this", "STANDARDS APPLIED block". The long form of
  the Layer-0 Core standards rule; the verified anchor map is in
  references/standards-anchor-map.md.
---

# Standards discipline

Core states the rule (versions are facts not memories; assert conformance only
from a record; the negative case is mandatory). This skill is the method that
satisfies it, plus the verified anchor map of what governs which discipline
(`references/standards-anchor-map.md` — load your pack's section).

## 1. Versions are facts, not memories

Standard designations, edition years, statute citations, and regulatory clause
numbers are **verified against the issuing body at time of use** — never
recalled. An agent that cannot verify a designation states it as **UNVERIFIED**
rather than asserting it. The live example the whole architecture exists to
prevent: `ISO/IEC/IEEE 12207:2017` was withdrawn 29 April 2026 and replaced by
`12207:2026` — citing the 2017 edition from memory today cites a withdrawn
standard with full confidence.

## 2. Conformance is asserted only from a conformance record

You may state which standard you **applied**. You may **not** assert
conformance unless you can name the record that establishes it — test report,
certificate, audit, or Supplier's Declaration of Conformity, **with issuer and
date**.

- ✅ "Applied the derating approach of IEC 61709:2017."
- ✅ "Designed against IEC 60529 Ed. 2.2 ingress requirements; **not tested, not certified**."
- ✅ "Complies with 47 CFR Part 15 Subpart B per test report [lab, number, date]." — a record is named.
- ❌ "IP67 compliant." ❌ "Meets IEC 62368-1." ❌ "FCC compliant." — no record.

Two deliberate allowances: for a **regulation**, "complies with Part 15" is the
operative legal concept and is permitted; and reporting a customer's genuine
certificate is reporting a fact.

## 3. Label the instrument type (six categories)

Never type an instrument outside these six: **statute** · **regulation / trade
regulation rule** · **voluntary program codified in the CFR** · **interpretive
policy statement** · **guide** · **voluntary consensus standard / regulatory
specification**. (A CFR-codified voluntary program — e.g. 47 CFR Part 8 Subpart B,
the FCC Cyber Trust Mark — is *not* a "Regulation"; a Guide such as 16 CFR Part
255 is the Commission's interpretation of what §5 prohibits, with no safe harbour.)

## 4. Every discipline output carries a STANDARDS APPLIED block

Short and mandatory. Four requirements per entry: **designation, edition and
year** (not "the IEC ingress standard"); **what was actually used** (the clause,
method, or requirement — a standard named but unused is padding, and padding a
provenance block is a form of fabrication); **verification stamp** (the date the
designation was checked against the issuing body, and where); **access honesty**
(if paywalled and not held, say you worked from a summary — the most-skipped,
most-damaging item).

```
STANDARDS APPLIED
  IEC 60529 Ed. 2.2 (2013) — ingress classification method, §4–6 — VERIFIED 2026-08-03 — paywalled, not held
  47 CFR Part 15 Subpart B — conducted/radiated emission limits — REGULATION — free, verified at eCFR
  No published standard governs the cost-allocation method used; applied practice:
    bottom-up should-cost with tiered volume scaling. Provenance: internal method, not externally validated.
```

**Placement.** The full block goes at the end — **but** where either "we worked
from a summary of a paywalled standard we do not hold" **or** "no published
standard governs this" applies, a **one-line statement goes inline at the point
the conclusion is made**, not only in the terminal block. A terminal block is a
footnote by function, and Core forbids burying material disclosure in a footnote.

> "…the enclosure should reach IP65. **(Assessed against a secondary summary of IEC 60529; we do not hold the standard. Not tested.)**"

**The negative case is mandatory.** Where no published standard governs, say so
and name the practice applied instead, with its provenance. Silence reads as "a
standard was followed." Most business, marketing, and strategy work falls here —
saying so is a strength.

## 5. The anchor map and drift control

`references/standards-anchor-map.md` lists the governing reference, designation,
edition, type, and access for each discipline, plus the caveats agents must
carry (withdrawn designations, editions in flight, scope stretches) and the
drift-control rules. **Load your pack's section; do not cite from this SKILL.md's
memory.** Entries carry per-entry verification stamps; an entry over 180 days, or
marked UNVERIFIED, must be re-verified against the issuing body before you cite
it. Withdrawn designations stay in the map marked WITHDRAWN so you recognise one
in a customer document rather than accepting it.
