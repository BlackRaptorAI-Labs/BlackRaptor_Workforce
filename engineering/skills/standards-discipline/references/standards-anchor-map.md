# Verified Anchor Map — governing standards by discipline

> **Sanctioned Rule-3 registry (SPEC §9.2).** This map is keyed by *discipline* (which some packs
> name identically to an agent slug, e.g. `power-electronics`, `compliance-cert`); the slugs are row
> labels for a domain→standard catalogue, not agent-dispatch instructions, and confer no cross-pack
> dependency. `verify.sh`'s Rule-3 grep skips this file, as the audit sanctioned for the gate registry.

The per-agent standards map and its drift-control rules. Load your pack's section when applying or citing a standard. The **method** (provenance labels, verify-before-cite, conformance-from-record, citation-block placement) is in the `standards-discipline` SKILL.md; this file is the map it points to.

## Verification stamps (per-entry; seeds `[4h]`'s 180-day re-verification window)

Each line records a verification actually performed against the **issuing body** this session, with the date and source (a secondary/reseller confirmation is not accepted — issuing body or UNVERIFIED, nothing between). `[4h]` reads these dates; an entry older than 180 days, marked UNVERIFIED, or absent must be re-verified before citing. **The pass is in progress; entries not yet stamped rest on the 3 Aug 2026 table-level date below and are red-by-truth under `[4h]` until stamped.** Stable-sorted by pack then designation.

| Designation | Status | Verified | Source (issuing body) |
|---|---|---|---|
| ETSI EN 303 645 V3.1.3 (2024-09) | current | 2026-08-07 | etsi.org/.../en_303645v030103p.pdf |
| IEC 60068-1:2013 Ed. 7.0 | current (replaces 1988 6th ed) | 2026-08-07 | webstore.iec.ch/en/publication/501 |
| IEC 60529 Ed. 2.2 (1989+A1:1999+A2:2013) | current (cor.1:2013, cor.2:2015) | 2026-08-07 | webstore.iec.ch/en/publication/2452 |
| IEC 60812:2018 Ed. 3.0 | current (replaces 2006) | 2026-08-07 | webstore.iec.ch/en/publication/26359 |
| IEC 61709:2017 Ed. 3.0 | current (replaces 2011; cor1:2019) | 2026-08-07 | webstore.iec.ch/en/publication/28554 |
| IEC 62368-1:2023 Ed. 4.0 | current (EN adoption 2024/A11:2024) | 2026-08-07 | webstore.iec.ch/en/publication/69308 |
| IEC 62443-4-1:2018 | current | 2026-08-07 | webstore.iec.ch/en/publication/33615 |
| IEC 62477-1:2022 Ed. 2.0 | current (COR1:2024) | 2026-08-07 | webstore.iec.ch/en/publication/28936 |
| IPC J-STD-001J (2024) | current (replaces H, 2020) | 2026-08-07 | shop.ipc.org/ipc-j-std-001 |
| IPC-A-610J (2024) | current (replaces H, 2020) | 2026-08-07 | shop.ipc.org/ipc-a-610 |
| Telcordia SR-332 Issue 4 (Mar 2016) | current | 2026-08-07 | telecom-info.njdepot.ericsson.net (SR-332) |
| ISO/IEC 42001:2023 | current (pub. Dec 2023) | 2026-08-07 | iso.org/standard/42001 |
| ISO/IEC/IEEE 12207:2026 Ed. 2 | current (replaces 12207:2017) | 2026-08-07 | iso.org/standard/90219.html |
| ISO/IEC/IEEE 15288:2023 Ed. 2 | current (replaces 15288:2015) | 2026-08-07 | iso.org/standard/81702.html |
| NIST AI 100-1 (AI RMF 1.0), Jan 2023 | current (review due <=2028) | 2026-08-07 | nist.gov/itl/ai-risk-management-framework |
| NIST SP 800-218 v1.1 (Feb 2022) | current (Rev.1/SSDF v1.2 still draft) | 2026-08-07 | csrc.nist.gov/projects/ssdf |
| OWASP ASVS 5.0.0 (30 May 2025) | current | 2026-08-07 | owasp.org ASVS project / asvs.dev |
| CONSORT 2025 | current (supersedes CONSORT 2010) | 2026-08-07 | nature.com/articles/s41591-025-03635-5 |
| 16 CFR Part 255 (amended 26 Jul 2023) | current | 2026-08-07 | ecfr.gov title-16 part-255 |
| 16 CFR Part 465 (final 22 Aug 2024, eff. 21 Oct 2024) | current | 2026-08-07 | ecfr.gov title-16 part-465 |
| ISED RSS-Gen Issue 6 (30 Jul 2026) | **current — REPLACES Issue 5 (Apr 2018 + Amd 2 2021-02); ~1-yr transition — SUPERSEDED FINDING** | 2026-08-07 | ised-isde.canada.ca RSS-Gen page |
| ISO 9001:2015 + Amd 1:2024 | current (ISO/FDIS 9001 → 9001:2026 expected Sep 2026, not yet published) | 2026-08-07 | iso.org/standard/62085.html; /88431.html |
| ISO 31000:2018 | current (ISO/CD 31000 in development, stage 90.92) | 2026-08-07 | iso.org/standard/65694.html |
| ISO/IEC/IEEE 29148:2018 Ed. 2 | current (confirmed 2024; DIS in progress) | 2026-08-07 | iso.org/standard/72089.html |
| ISO/IEC 23894:2023 | current | 2026-08-07 | iso.org/standard/77304.html |
| IEEE 1012-2024 | current (approved 2024-11-12, pub 2025-08-22, supersedes 1012-2016) | 2026-08-07 | standards.ieee.org/ieee/1012/7324 |
| ISED RSS-247 Issue 4 (pub. 2025-07-24) | current (replaces Issue 3, Aug 2023); date confirmed at ISED page — secondaries' "Feb 2025" was wrong | 2026-08-07 | ised-isde.canada.ca RSS-247 |
| NIST SP 800-218A (final, Jul 2024) | current | 2026-08-07 | csrc.nist.gov/pubs/sp/800/218/a/final |
| 47 CFR Part 15 | current | 2026-08-07 | ecfr.gov title-47 part-15 |
| 47 CFR Part 8 Subpart B (Cyber Trust Mark) | current | 2026-08-07 | ecfr.gov title-47 part-8 subpart-B |
| PRISMA 2020 | current (replaces 2009) | 2026-08-07 | ncbi.nlm.nih.gov PMC8007028 (BMJ) |
| 15 U.S.C. §45 (FTC Act §5) | current | 2026-08-07 | uscode.house.gov; law.cornell.edu/uscode/text/15/45 |
| 15 U.S.C. §1125(a) (Lanham Act §43(a)) | current (as of 2026-05-27) | 2026-08-07 | uscode.house.gov; law.cornell.edu/uscode/text/15/1125 |
| ISO 20252:2019 Ed. 3 | current (ISO/FDIS 20252 pending) | 2026-08-07 | iso.org/standard/73671.html |
| ICC/ESOMAR Code 2025 (5th ed) | current (supersedes 2016) | 2026-08-07 | standards.esomar.org; iccwbo.org |
| GRADE (Handbook + GRADE Book) | current (mid-migration, rolling) | 2026-08-07 | gradepro.org/handbook; book.gradepro.org |
| ICD 203 (2 Jan 2015) | current | 2026-08-07 | dni.gov; archive.dni.gov/files/documents/ICD/ICD-203.pdf |
| ISO/IEC/IEEE 42010:2022 Ed. 2 | current (replaces 2011) | 2026-08-07 | iso.org/standard/74393.html |
| 42 CFR Part 11 | current (amended 89 FR 97559, 9 Dec 2024) | 2026-08-07 | ecfr.gov title-42 part-11 |
| IEEE/ANSI C63.10-2020 | current (Cor1-2023) | 2026-08-07 | standards.ieee.org/standard/C63_10-2020.html |
| ISO/IEC/IEEE 29119 (-1:2022, -3:2021, -5:2024) | current | 2026-08-07 | iso.org/standard/81291.html (Part 1) |
| TOP 2025 | current (2025 update, replaces 2015) | 2026-08-07 | cos.io/initiatives/top-guidelines |
| IEEE/ANSI C63.4-2014 | current (Amd C63.4a-2017) | 2026-08-07 | standards.ieee.org/ieee/C63.4/5841 |
| IPC-2221C | current (Revision C) | 2026-08-07 | shop.ipc.org/ipc-2221 (Revision-c) |
| ISO 10007:2017 Ed. 3 | current (confirmed 2023) | 2026-08-07 | iso.org/standard/70400.html |
| ANSI/NEMA 250-2020 | current (confirmed at ANSI 2026-08-12: ANSI-approved 2020-12-08; **revises/supersedes ANSI/NEMA 250-2018; NO successor; NOT rescinded**. The earlier task-#8 secondary lead — "rescinded → ANSI/NEMA EN 10250-2024" — is REFUTED by the issuing authority and removed.) | 2026-08-12 | ANSI (blog.ansi.org) |
| AJP-2.1 (NATO; STANAG 2191) | **UNVERIFIED — `[4h] accepted-residual`** (owner-accepted 2026-08-12): cited **only** for the **Admiralty Code** (Table 3.1 — source-reliability × credibility), a convention **stable across editions**. NATO NSO (nso.nato.int) is access-restricted, so the exact edition is unconfirmable; because the cited substance is **version-invariant**, the citation stands. Reported, but does not hard-fail `[4h]` (mirrors `[4l]`'s ratified-exception discipline). | — | nso.nato.int access-restricted; cited substance version-invariant |

**1.4 verification pass — CLOSED. FINAL COUNTS: 45 verified · 2 UNVERIFIED · 1 superseded/withdrawn finding.**
- **45 verified** carry a fresh 2026-08-07 issuing-body stamp above (secondary/reseller confirmations were rejected per the issuing-body-only rule — which caught the RSS-Gen wrong-date).
- **UPDATE 2026-08-12 (both former 1.4 UNVERIFIED entries resolved):** `ANSI/NEMA 250-2020` is now **VERIFIED** at ANSI (current; revises NEMA 250-2018; not rescinded — the earlier rescission lead was refuted). `AJP-2.1` is an **owner-ACCEPTED RESIDUAL** (`[4h] accepted-residual`): cited only for the version-invariant Admiralty Code, NSO access-restricted. **Current section total: 49 verified · 1 accepted-residual · 0 hard-UNVERIFIED** — so `[4h]` is GREEN (the accepted residual is reported, not failed, mirroring `[4l]`).
- **1 superseded/withdrawn finding → [4f]:** `ISED RSS-Gen Issue 5` → Issue 6 (30 Jul 2026). Recorded as **organic catch #1** in `docs/ORGANIC-CATCHES.md` (maintainer record, not shipped with this plugin).
- **STABLE class (no current-edition drift; cited correctly by the map, not given a fresh per-entry stamp):** the FTC interpretive policy statements (Deception 1983, Substantiation 1984), case law (POM Wonderful, Removatron, Thompson Medical, Castrol), the FTC Penalty Offense notices (2021/2023), `.com Disclosures` (2013, FTC review open since 2022, no replacement), and FASB ASC + IFRS (continuously amended — cite the specific Topic/Standard + as-of date, no version number). These are statutes/case-law/policy/continuously-amended instruments with no edition to re-verify.
- **N/A (negative case / not a standard):** cost-engineer & the council disciplines with "no published standard governs"; the Kohavi textbook (explicitly not a standard); NAD/BBB (no designation); the CIA Tradecraft Primer (training primer). No verification applicable.

**SUPERSEDED FINDING → WITHDRAWN list (for `[4f]`):** **ISED RSS-Gen Issue 5** (April 2018 + Amendment 2, 2021-02) is **SUPERSEDED by RSS-Gen Issue 6, published 30 July 2026** (confirmed at the ISED page). Successor designation: **RSS-Gen Issue 6 (2026-07-30)**; ~1-year transition during which either issue is accepted, then Issue 6 only. The map's prior caveat ("Issue 6 is in consultation, not published; Issue 5 remains in force") is now false and is corrected below. *(Secondary sources reported "February 2026" — wrong; the issuing body states 30 July 2026. Issuing-body-only verification caught the error.)*

### Post-1.4 additions — designations cited by agents, surfaced by `[4e]` (2026-08-12); VERIFIED (task #8)

These are named in agent bodies (`compliance-officer`, `security-architect`, `power-electronics`) but were **absent from the map** — a real `[4e]` coverage finding, now tracked. **All three were verified against their issuing bodies on 2026-08-12 (task #8)** — issuing-body only, no secondary/reseller sources. The 1.4-pass counts above (45 verified · 2 UNVERIFIED) are historical to that pass. After the 2026-08-12 resolutions (these 3 verified + `ANSI/NEMA 250-2020` verified at ANSI + `AJP-2.1` accepted-residual), the section carries **49 verified · 1 accepted-residual (`AJP-2.1`) · 0 hard-UNVERIFIED** → `[4h]` GREEN.

| Designation | Status | Verified | Source (issuing body) |
|---|---|---|---|
| ISO 27001:2022 (ISO/IEC 27001:2022, Ed. 3) | current (3rd ed, cancels/replaces 27001:2013; Amd 1:2024 "climate action changes" published 2024-02) | 2026-08-12 | iso.org/standard/27001 (+ iso.org/standard/88435.html for Amd 1) |
| IPC-9592 (Rev. B, 2012) | current revision (IPC-9592B, Nov 2012; replaces Rev A:2010 and the 2008 original) | 2026-08-12 | shop.ipc.org/general-electronics/standards/9592-0-b-english (IPC) |
| IEC 61000-4-5 (2014+AMD1:2017, Ed. 3.0) | current (2014 3rd ed + Amendment 1:2017; surge immunity) | 2026-08-12 | webstore.iec.ch/en/publication/4223 (+ /29449 for AMD1:2017) |

---

## WITHDRAWN / superseded designations — `[4f]` reads this table

Do not cite these as current. **`verify.sh [4f]` derives its match set from the `Match key` column below** — single source of truth, no hand-maintained regex. A withdrawn designation stays here permanently so an agent encountering one in a customer document recognises it.

| Withdrawn designation | Match key | Successor (current) | Superseded / withdrawn |
|---|---|---|---|
| ISO/IEC/IEEE 12207:2017 | `12207:2017` | ISO/IEC/IEEE 12207:2026 | 2026-04-29 (verified) |
| ISO/IEC/IEEE 15288:2015 | `15288:2015` | ISO/IEC/IEEE 15288:2023 | 2023 on successor pub (verified) |
| ISO/IEC/IEEE 29148:2011 | `29148:2011` | ISO/IEC/IEEE 29148:2018 | 2018 on successor pub (verified) |
| IEEE 1012-2016 | `1012-2016` | IEEE 1012-2024 | 2025-08-22 (verified) |
| ISO/IEC/IEEE 42010:2011 | `42010:2011` | ISO/IEC/IEEE 42010:2022 | 2022-11 on successor pub (verified) |
| ISO 26362:2009 | `ISO 26362` | ISO 20252:2019 (incorporated) | 2019 on successor pub (verified) |
| CONSORT 2010 | `CONSORT 2010` | CONSORT 2025 | 2025 (verified) |
| ISED RSS-Gen Issue 5 | `RSS-Gen Issue 5` | ISED RSS-Gen Issue 6 | 2026-07-30 (verified — organic catch #1) |
| IEC 62380 | `IEC 62380` | IEC 61709 / Telcordia SR-332 | withdrawn (3-Aug map caveat; not re-verified this session) |
| IEC 60950-1 | `IEC 60950` | IEC 62368-1 | superseded (3-Aug map caveat) |
| IEC 60065 | `IEC 60065` | IEC 62368-1 | superseded (3-Aug map caveat) |
| MIL-HDBK-217 | `MIL-HDBK-217` | IEC 61709 / Telcordia SR-332 | obsolete for new design, Notice 2 1995 (3-Aug caveat) |
| IEEE 828-2012 | `IEEE 828-2012` | CM clauses of 12207:2026 / 15288:2023 | inactive-reserved 2023-03-30 (3-Aug caveat) |

**Provenance:** the top 8 rows' successors were verified against issuing bodies in the 1.4 pass (2026-08-07); the bottom 5 rest on the map's original 3-Aug caveats (not re-verified this session — flagged for the next sweep). **Every `[4f]` match key now has a table row — no orphan regex entries.**

---

## Part 4 — The verified anchor map

Verified 3 August 2026 against issuing bodies. **Re-verify before relying on any version number** — several entries below have revisions in flight.

### 4.1 Hardware engineering pack

| Agent / discipline | Governing reference | Designation and edition | Type | Access |
|---|---|---|---|---|
| power-electronics | Safety requirements for power electronic converter systems | IEC 62477-1:2022 Ed. 2.0 | Standard | Paywalled |
| power-electronics, reliability | Reference conditions for failure rates and stress models | IEC 61709:2017 Ed. 3.0 | Standard | Paywalled |
| thermal-mechanical | Degrees of protection provided by enclosures (IP Code) | IEC 60529 Ed. 2.2 (1989+A1:1999+A2:2013) | Standard | Paywalled |
| thermal-mechanical (North America) | Enclosures for Electrical Equipment (1,000 V max) | ANSI/NEMA 250-2020 | Standard | Paywalled |
| thermal-mechanical | Environmental testing — general and guidance | IEC 60068-1:2013 Ed. 7.0 | Standard | Paywalled |
| rf-connectivity (US) | Radio Frequency Devices | **47 CFR Part 15** | **Regulation** | Free (eCFR) |
| rf-connectivity (US test method) | Compliance testing of unlicensed wireless devices | ANSI C63.10-2020 | Standard | Paywalled |
| rf-connectivity (US test method) | Methods of measurement of radio-noise emissions | ANSI C63.4-2014 | Standard | Paywalled |
| rf-connectivity (Canada) | General requirements for compliance of radio apparatus | **ISED RSS-Gen Issue 6 (30 Jul 2026)** — replaces Issue 5 + Amd 2 (2021-02) | Regulatory spec | Free |
| rf-connectivity (Canada) | Licence-exempt LAN and digital transmission devices | ISED RSS-247 Issue 4 (2025-07-24) | Regulatory spec | Free |
| manufacturing-dfm | Acceptability of Electronic Assemblies | IPC-A-610J (2024) | Standard | Paywalled |
| manufacturing-dfm | Requirements for Soldered Electrical and Electronic Assemblies | IPC J-STD-001J (2024) | Standard | Paywalled |
| manufacturing-dfm | Generic Standard on Printed Board Design | IPC-2221C | Standard | Paywalled |
| reliability-dfr | Failure modes and effects analysis (FMEA and FMECA) | IEC 60812:2018 Ed. 3.0 | Standard | Paywalled |
| reliability-dfr | Reliability Prediction Procedure for Electronic Equipment | Telcordia SR-332 Issue 4 | Standard | Paywalled |
| compliance-cert | Audio/video, ICT equipment — safety requirements | IEC 62368-1:2023 Ed. 4.0 | Standard | Paywalled |
| hw-program | System life cycle processes | ISO/IEC/IEEE 15288:2023 Ed. 2 | Standard | Paywalled |
| embedded-firmware (IACS scope) | Secure product development lifecycle requirements | IEC 62443-4-1:2018 | Standard | Paywalled |
| embedded-firmware (consumer IoT) | Cyber Security for Consumer IoT: Baseline Requirements | ETSI EN 303 645 V3.1.3 (2024-09) | Standard | **Free** |
| embedded-firmware (US labelling) | Cybersecurity Labeling Program for IoT Products (FCC Cyber Trust Mark) | 47 CFR Part 8 Subpart B | **Voluntary program codified in the CFR** — participation is optional; do not label "Regulation" | Free |
| cost-engineer | *No published standard governs should-cost modelling.* State the method and its provenance. | — | — | — |

**Hardware caveats the agents must carry:**

- **MIL-HDBK-217 is obsolete for new design.** Last technical update was Notice 2 (1995); its component models predate essentially all modern silicon and packaging. It remains contractually invoked on some defence programmes, but presenting it as a current predictive method is a defect. Prefer IEC 61709 or Telcordia SR-332, paired with physics-of-failure and design-for-reliability (DFR) test evidence.
- **IEC 62380 is withdrawn.** Never cite as current.
- **IEC 60950-1 and IEC 60065 are withdrawn**, superseded by IEC 62368-1.
- **"IEC 60529:2020" is a common error.** The current text is Ed. 2.2 (2013 consolidated). ANSI/IEC 60529-2020 is the United States national adoption of that same text.
- **Edition churn on 62368-1.** IEC Ed. 4.0 (2023) is current at IEC level, but the edition that governs a shipment is the *national adoption in force in that market*, and most bodies are still transitioning from Ed. 3.0.
- **RSS-Gen Issue 6 was published 30 July 2026** (ISED), superseding Issue 5 (April 2018 + Amendment 2, 2021-02). A ~1-year transition accepts either issue; after it, Issue 6 only. *(Corrected 2026-08-07 — the prior "in consultation, not published" text was stale; verified at the ISED RSS-Gen page.)*
- **IEC 62443-4-1 is scoped to industrial automation and control systems.** Borrowing it for general embedded firmware is defensible engineering but a scope stretch — say so when invoking it outside that scope.
- **IPC-A-610 and J-STD-001 are complementary.** J-STD-001 governs the process; A-610 governs acceptance. They are not interchangeable.

### 4.2 Development pack

| Discipline | Governing reference | Designation and edition | Type | Access |
|---|---|---|---|---|
| Software lifecycle | Software life cycle processes | **ISO/IEC/IEEE 12207:2026** Ed. 2 (pub. 29 Apr 2026) | Standard | Paywalled |
| Systems lifecycle | System life cycle processes | ISO/IEC/IEEE 15288:2023 Ed. 2 | Standard | Paywalled |
| Requirements | Requirements engineering | ISO/IEC/IEEE 29148:2018 Ed. 2 | Standard | Paywalled |
| Verification and validation | System, Software, and Hardware Verification and Validation | IEEE 1012-2024 | Standard | Paywalled |
| Testing | Software testing (parts 1–5) | ISO/IEC/IEEE 29119-1:2022, -2:2021, -3:2021, -4:2021, -5:2024 | Standard | Paywalled |
| Secure development | Secure Software Development Framework (SSDF) | **NIST SP 800-218 v1.1** (Feb 2022) | Framework | **Free** |
| Secure development, generative artificial intelligence (AI) | SSDF Community Profile for Generative AI | **NIST SP 800-218A** (Jul 2024) | Framework | **Free** |
| Application security | Application Security Verification Standard | **OWASP ASVS 5.0.0** (30 May 2025) | Standard | **Free** |
| Architecture | Software, systems and enterprise — Architecture description | ISO/IEC/IEEE 42010:2022 Ed. 2 | Standard | Paywalled |
| AI management | Artificial intelligence — Management system | ISO/IEC 42001:2023 | Standard (certifiable) | Paywalled |
| AI risk | AI Risk Management Framework | **NIST AI 100-1 (AI RMF 1.0)** (Jan 2023) | Framework | **Free** |
| AI risk (international) | AI — Guidance on risk management | ISO/IEC 23894:2023 | Standard | Paywalled |
| Quality management | Quality management systems — Requirements | ISO 9001:2015 + Amd 1:2024 | Standard | Paywalled |
| Configuration management | CM process clauses of 12207:2026 / 15288:2023; ISO 10007:2017 in a QMS context | — | Standard | Paywalled |

**Development caveats:**

- **Withdrawn — do not cite:** ISO/IEC/IEEE 12207:**2017** (withdrawn 29 Apr 2026), 15288:**2015**, 29148:**2011**, IEEE 1012-**2016**, ISO/IEC/IEEE 42010:**2011**, and the 2013/2015 editions of the 29119 parts.
- **IEEE 828-2012 is Inactive-Reserved** (inactivated 30 Mar 2023). It is no longer an active IEEE standard and must not be cited as governing configuration management.
- **NIST SP 800-218 Rev. 1 (SSDF v1.2) is an initial public draft**, comment period closed 30 Jan 2026, **not final**. v1.1 remains the citable version.
- **Revisions in flight:** ISO 9001 6th edition targeted September 2026 (designation unconfirmed); ISO 31000 at stage 90.92; ISO/IEC/IEEE 29148 in revision; NIST AI RMF under revision with no version or date announced.
- **IEEE 1012-2024 year ambiguity:** board-approved November 2024, published August 2025. Cite as "IEEE 1012-2024".

### 4.3 Research and evidence (bridge pack)

| Discipline | Governing reference | Designation and version | Type | Access |
|---|---|---|---|---|
| Certainty of evidence | GRADE approach | GRADE Handbook (Oct 2013), migrating to the GRADE Book (2024–, rolling) | Voluntary methodology | **Free** |
| Systematic review reporting | PRISMA | **PRISMA 2020** | Voluntary guideline | **Free** |
| Controlled-experiment reporting | CONSORT | **CONSORT 2025** (supersedes CONSORT 2010) | Voluntary guideline | **Free** |
| Source reliability × credibility | Allied Joint Doctrine for Intelligence Procedures, Table 3.1 (the "Admiralty Code") | AJP-2.1 Ed. B Ver. 3 (May 2022), STANAG 2191 | Doctrine | Free (unclassified) |
| Analytic standards | Intelligence Community Directive 203, *Analytic Standards* | ICD 203 (2 Jan 2015) | Binding on US IC only | **Free** |
| Structured analytic techniques | *A Tradecraft Primer* | CIA CSI, March 2009 | Training primer, not a standard | **Free** |
| Pre-registration norms | Transparency and Openness Promotion Guidelines | **TOP 2025** | Voluntary guideline | **Free** |
| Clinical trial registration | Clinical Trials Registration and Results Information Submission | **42 CFR Part 11** (amended 9 Dec 2024) | **Regulation** | Free |

**Research caveats:**

- **GRADE is mid-migration.** Check the GRADE Book first; cite the 2013 Handbook only for sections the Book has not yet rewritten.
- **CONSORT flipped in 2025.** Anything citing "CONSORT 2010" as current is out of date.
- **"Admiralty Code" is a convention name, not a designation.** There is no standalone standard by that title. Cite AJP-2.1 Ed. B Ver. 3, Table 3.1.
- **ICD 203 binds US Intelligence Community elements only.** Applying it commercially is an adopted convention, not compliance.
- **Outside clinical trials there is no pre-registration regulation** — only norms.

### 4.4 Marketing pack

| Discipline | Governing reference | Designation | Type | Access |
|---|---|---|---|---|
| **The statute itself** | Federal Trade Commission Act §5 — unfair or deceptive acts or practices | **15 U.S.C. §45** | **Statute** | **Free** |
| **Competitor false-advertising suits** | Lanham Act §43(a) — false or misleading description of fact | **15 U.S.C. §1125(a)** | **Statute** | **Free** |
| **Industry self-regulation** | National Advertising Division (NAD), BBB National Programs | — | Voluntary forum; the realistic first challenge venue | Free |
| Claim substantiation | FTC Policy Statement Regarding Advertising Substantiation | 23 Nov 1984 | Interpretive policy under §5 | **Free** |
| Deception | FTC Policy Statement on Deception | 14 Oct 1983 | Interpretive policy under §5 | **Free** |
| **Establishment-claim standard** | *POM Wonderful, LLC v. FTC*, 777 F.3d 478 (D.C. Cir. 2015); *Removatron*, 111 F.T.C. 206; *Thompson Medical*, 104 F.T.C. 648 | — | **Case law** — a non-specific establishment claim requires evidence sufficient to satisfy the relevant scientific community | Free |
| **Reliability challenge standard** | *Castrol, Inc. v. Quaker State Corp.*, 977 F.2d 57 (2d Cir. 1992) | — | **Case law** — a challenger need only show the tests were not sufficiently reliable | Free |
| **Civil-penalty exposure** | Notices of Penalty Offenses — Endorsements (Oct 2021); Substantiation (Apr 2023) | FTC Act **§5(m)(1)(B)** | **Penalty Offense notice** — converts guidance into monetary exposure | **Free** |
| Endorsements, testimonials, reviews | Guides Concerning Use of Endorsements and Testimonials in Advertising | **16 CFR Part 255** (amended 26 Jul 2023) | **Guide** — the Commission's interpretation of what §5 prohibits; no safe harbour | Free |
| **Fake and manipulated reviews** | Rule on the Use of Consumer Reviews and Testimonials | **16 CFR Part 465** — final 22 Aug 2024, effective 21 Oct 2024 | **Trade regulation rule (§18) — independently enforceable, civil penalties** | Free |
| Digital disclosure | .com Disclosures | FTC staff guidance, March 2013 | Non-binding staff guidance | **Free** |
| Market research conduct | ICC/Esomar International Code on Market, Opinion and Social Research and Data Analytics | **2025 edition** (supersedes 2016) | Voluntary self-regulatory code | **Free** |
| Market research (formal) | Market, opinion and social research — vocabulary and service requirements | ISO 20252:2019 | Standard (certifiable) | Paywalled |
| Online experimentation | Kohavi, Tang & Xu, *Trustworthy Online Controlled Experiments* (CUP, 2020) | — | ⚠️ **Textbook, NOT a standard** | Paywalled |

**Marketing caveats:**

- **16 CFR Part 255 sits in the CFR but is a Guide** — the Commission's interpretation of what §5 already prohibits. Per §255.0(a), inconsistent practices *may result in corrective action under §5*. It is not "the endorsement law", it is not merely "evidence of a violation", and **compliance with it is not a safe harbour**.
- **16 CFR Part 465 is different in kind.** It is a §18 trade regulation rule, independently enforceable with civil penalties. Any agent reasoning about reviews, testimonials, or endorsements must reach for Part 465 as well as Part 255 — an earlier version of this map listed Part 255 while omitting the enforceable rule sitting next to it.
- **.com Disclosures is stale.** The FTC opened a review in June 2022; no replacement has issued. Cite the 2013 version and flag the pending revision.
- **ICC/Esomar flipped in 2025.** Many third-party sites still serve the superseded 2016 PDF.
- **There is no standards-body standard for online A/B testing.** No ISO, ANSI, IEEE or W3C equivalent exists. Anything presented to you as "the A/B testing standard" is invented. Kohavi et al. is the closest citable reference and is a commercially published textbook.

### 4.5 Council pack

| Discipline | Governing reference | Designation | Type | Access |
|---|---|---|---|---|
| Financial reporting (US) | FASB Accounting Standards Codification | Continuously amended; cite Topic/ASC section + as-of date | Mandatory for SEC registrants | **Free since 27 Feb 2023** |
| Financial reporting (international) | IFRS Accounting Standards | Continuously amended; cite the specific IFRS/IAS + as-of date | Mandated in adopting jurisdictions | Basic free, full paywalled |
| Risk | Risk management — Guidelines | ISO 31000:2018 (stage 90.92, revision underway) | Standard | Paywalled |
| Ethics / AI governance | ISO/IEC 42001:2023 and NIST AI 100-1 | see §4.2 | Standard / Framework | Mixed |
| Pricing, GTM, revenue, people-org, fundraising, technology-strategy | *No published standard governs these disciplines.* | — | — | — |

**Never write "GAAP 2026" or "IFRS 2026."** Neither has a version number. Cite the specific Topic or Standard plus an as-of date.

**The council pack is where the negative case matters most.** Most of what the council does has no external authority behind it. Saying so — in the `Standards applied` block, on every output — is the difference between a defensible advisory product and one that borrows credibility it has not earned.

---

## Part 5 — Drift control

Standards move. Six entries above have revisions in flight and one was superseded four months ago. A map that is not maintained becomes a fabrication engine with a verification stamp on it.

| Mechanic | Rule |
|---|---|
| **Verification stamp** | **Every entry** carries its own date and verification URL — not one blanket date per table. Entries older than 180 days are marked STALE and agents must re-verify before citing. *(The tables above currently carry a single header date. That is a known defect: the map does not yet satisfy its own rule, and the `4h` check below is written to the entry level so it will fail until the stamps are added. Adding them is a prerequisite to relying on this map.)* |
| **Watch list** | Entries with a known revision in flight are flagged. Currently: ISO 9001, ISO 31000, ISO/IEC/IEEE 29148, NIST SP 800-218, NIST AI RMF, GRADE, ISO 10007, RSS-Gen. |
| **No memory citations** | Enforced in Core, not per-agent. An agent that cannot verify a designation states the designation as unverified rather than asserting it. |
| **Quarterly re-verification** | The map is re-checked against issuing bodies quarterly. The check is logged with its date, whether or not anything changed. |
| **Withdrawn list is permanent** | Superseded designations stay in the map, marked WITHDRAWN, so an agent that encounters one in a customer document recognises it rather than accepting it. |
