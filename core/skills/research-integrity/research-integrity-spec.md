# Research-Integrity System — FINAL Build-Ready Spec (v2)

*Head of Research Methodology. Supersedes the v1 draft. This document is the SPEC. It defines an intake triage, the mode-selector, three per-mode tracks (with the C split), the shared spine, the concrete artifacts, and the agent/workflow wiring. This revision closes the seams, the grading-subjectivity gaps, and the reviewer-independence gap the red-team identified. Rejected critiques are marked **[REJECTED]** with reason.*

---

## 0. First principles (load-bearing across everything)

1. **Two orthogonal axes, always graded separately.** Source *reliability* (trust the messenger?) is graded independently from evidence/claim *certainty* (how much do we believe *this* claim?). Present in ICD-203, GRADE, Admiralty, TSE, psychometrics, forecasting. **Never collapse them into one word.** Baker et al. (1968): ~87% of real Admiralty ratings collapse onto the A1/B2/C3 diagonal — a measurable bias smell we detect and block.

2. **Repetition is not evidence; independence is the master variable.** N citations corroborate only if they trace to N *independent origins*. Defeat the Woozle effect (continuing) and citogenesis (originating) by collapsing citation chains to roots and counting **effective-N of independent origins**, not raw volume. When the origin is unreachable, substitute **consilience** — independent lines with *disjoint error modes* converging (Whewell).

3. **Disconfirmation beats confirmation.** Rank hypotheses/options by evidence *inconsistent* with each (ACH). A claim echoed by 50 same-origin sources is HIGH consistency / ZERO diagnosticity — formally worthless.

4. **Freeze the method before the answer.** Pre-registration removes the researcher degrees of freedom motivated reasoning exploits. Identical logic in PRISMA-P, MCDA weights-before-scores, and Simmons/Nelson/Simonsohn pre-registration.

5. **Our judgment ≠ raw reporting.** Every output labels (a) sourced fact, (b) stated assumption, (c) our inference (ICD-203). We publish OUR graded analytic judgment with calibrated confidence and preserved dissent, gated by a release gate; low-confidence grading stays internal.

6. **Provenance is necessary, not sufficient — a reachable root is not a true root.** *(New, from red-team A.)* Tracing a claim to its origin proves the chain, not the fact. The system separates **root-reachability** (did we find the origin?) from **root-veracity** (is the origin likely correct?) and never lets the first stand in for the second.

7. **Proportionality — the default is light; heavy machinery escalates on stakes.** *(New, from red-team E.)* An always-heavy integrity system trains its users to route around it, so it fails to run when it matters. Effort scales to stakes, irreversibility, and public-facing exposure.

8. **The integrity system must obey its own independence rule.** *(New, from red-team G2/D1.)* A reviewer that is another instance of the producer's architecture running the same checklists is *correlated failure*, not independence. Deterministic checks run outside the LLM; high-stakes review uses a different model family.

---

## 1. Intake Triage (run FIRST — before the mode-selector)

*(New layer, red-team E1/F1.)* Two quick classifications set the weight of everything downstream.

### 1.1 Stakes / reversibility triage → sets the TRACK WEIGHT

| Tier | Test | Track weight |
|---|---|---|
| **LITE** | Low stakes AND easily reversible AND not public-facing (e.g. "which $400 dev GPU") | **Lite track** (§4.0): trace-to-root for the 1–2 load-bearing numbers, verify at vendor source, one-axis grade sufficient, BLUF out. No AHP / pre-mortem / multiverse / hash-vault. |
| **STANDARD** | Consequential but internal/reversible | Full mode track, artifacts as marked "core." |
| **HEAVY** | Irreversible, high-cost, adversarial domain, OR public-facing/publishable (becomes someone's root) | Full track + all "escalation" artifacts + mandatory producer/reviewer split with architectural independence (§7.2). |

**Escalation is one-way and auto-triggered:** any of {irreversibility discovered, spend over threshold, external publication, a load-bearing claim graded Low with no fallback} promotes the task to the next tier and re-opens the gate. A task may never be silently *de*-escalated once a heavy trigger fires.

### 1.2 Root-availability triage → flags the HARD-FAIL class early

For each load-bearing claim, pre-classify whether a root is even reachable in principle:
- **Rootable** — a primary source exists and is reachable → normal track.
- **Consilience-only** — no reachable single root but independent lines exist → consilience path (§5.2.5).
- **Unknowable** — neither reachable root nor independent lines (competitor internals, future reliability of a new product) → **HARD-FAIL class** (§5.3): may enter the decision **only** as an explicitly labeled *assumption/open-question*, never as fact or graded judgment, and the decision's robustness must be tested as if that claim could go either way.

---

## 2. The Mode-Selector (run after triage, before any research)

Classify every task into exactly one mode. Ambiguous tasks decompose into sub-tasks, each classified separately and fused per §5.6.

### 2.0 Source-genre pre-filter (runs BEFORE Q1–Q3) *(New, red-team C1)*
Route by *what the artifact actually is*, not by whether it calls itself a "study" or "report":
- Peer-reviewed / registered / methods-transparent scientific study → **A-track appraisal tools** (GRADE/RoB).
- Commercial / grey / vendor / practitioner artifact (whitepaper, marketing benchmark, analyst report, industry survey, forum post) → **B-track tools** (astroturf/independence-of-testimony/provenance-tiering) **even if it is titled "study" or "report."**
- A single task may contain both genres → decompose (§5.6).

### 2.1 Decision rule (in order)

```
Q0. GENRE pre-filter (§2.0): tag each artifact scientific-study vs grey/commercial/practitioner.

Q1. Are WE generating NEW primary data by running our own instrument
    (survey, experiment, structured interview, benchmark WE run)?
      → YES → go to Q1a
      → NO  → continue
   Q1a. Is the data INTENDED to be published / to become someone else's root?
      → YES → MODE C-PUBLISHABLE (full instrument-validity + AAPOR load)
      → NO  → MODE C-INTERNAL  (B-with-a-measurement-addendum: randomization,
              controls, pre-stated stopping rule — but NOT I-CVI panels / AAPOR)

Q2. Is the deliverable an appraisal/synthesis of OTHERS' already-published
    SCIENTIFIC studies/reports (genre = study per Q0)?
      → YES → MODE A (Evidence Synthesis)
      → NO  → continue

Q3. Are we gathering DIRECT facts + practitioner testimony (spec sheets,
    prices, benchmarks, reviews) into OUR OWN dataset to drive a DECISION?
      → YES → MODE B (Direct-Source Aggregation)
```

**C split resolves the v1 Q1/step-8 contradiction** *(red-team C2)*: "benchmarks WE run" for a decision are **C-internal** (they feed a Mode-B decision matrix as a `measured` provenance-tier cell); only benchmarks intended as a published root are **C-publishable**.

### 2.2 Tells

| Mode | Question shape | Inputs | Deliverable | Woozle risk we most face |
|---|---|---|---|---|
| **A** | "What does the evidence say about X?" | Peer-reviewed studies, reports, prior syntheses | Graded synthesized judgment (SoF) | **Continuing** (amplifying a weak/echoed primary) |
| **B** | "Which X is best / most cost-effective?" | Spec sheets, prices, benchmarks, reviews | Graded decision/recommendation | **Both** (echoed specs + bandwagon) |
| **C-internal** | "Let's measure X to decide" | Our benchmark/instrument, internal data | Measured cells feeding a decision | Minor (internal) — but still can mislead *us* |
| **C-publishable** | "Let's measure X for publication" | Respondents/units, our instrument | Publishable dataset + calibrated findings | **Originating** (minting a false fact) |

### 2.3 Worked examples
- "Summarize evidence on intermittent fasting and mortality." → studies → **A**.
- "Pick most cost-effective inference GPU." → specs + posts + prices → **B**; if we run our workload on it → embed a **C-internal** benchmark cell.
- "Best architecture for feature Y." → **B** (ACH-framed).
- "Survey our 300 users and publish it." → **C-publishable**.
- "Vendor whitepaper claiming 3× throughput." → genre = commercial → **B tools**, *not* A, regardless of the "study" label.

---

## 3. (numbering note) Tracks A/B/C follow. Lite track is §4.0.

## 4.0 The LITE Track *(New, red-team E1)*
For LITE-tier tasks only. Minimal, still-honest pipeline:
1. Identify the 1–2 **load-bearing** facts/numbers.
2. Trace each to its **root** and verify at the primary/vendor source (value + URL + retrieval date; hash optional at LITE).
3. One-axis grade is sufficient (a single reliability/certainty flag), **but** if any load-bearing fact is single-sourced-unverified it must carry the `single-sourced` flag (§5.3-A).
4. Run the **staleness check** (§5.3-F2) — LITE does not exempt currency.
5. BLUF output with FACT/ASSUMPTION/JUDGMENT labels.
6. **Auto-escalate** to STANDARD if any §1.1 heavy trigger fires mid-task.
Lite is *not* a lower-integrity track; it is a smaller surface. The anti-woozle primitives (root, single-source flag, staleness) still run; only the heavy MCDA/instrument machinery is deferred.

---

## 4.1 Track A — Evidence Synthesis (secondary)

**Native disciplines:** PRISMA/Cochrane, GRADE/CERQual, AMSTAR-2, Admiralty, citation-independence, ICD-203.

### Method
1. **Frame with PICO(S)** — pre-specify primary vs secondary outcomes (no later outcome-switching).
2. **Freeze the protocol (PRISMA-P)** before results; declare and justify deviations.
3. **Comprehensive search** — ≥2 databases + grey literature + registries + backward/forward citation-chasing; record exact strings and dates.
4. **Dual independent screening** — two agents, blind to each other; log Cohen's κ (target ≥0.80; floor ≥0.61); pre-agreed adjudication; PRISMA 4-phase flow with exclusions-and-reasons.
5. **De-duplicate to origin** — collapse multiple reports of one trial/dataset; run the Independence Audit (§5.2). **Report effective-N of independent origins, not citation count.** Kills "continuing a woozle."
6. **Per-study reliability appraisal** — RoB 2 / ROBINS-I → Low / Some-concerns / High; incoming *syntheses* via AMSTAR-2. Grade using the **anchored rubric + worked exemplars** (§5.1) and dual-grade a sample for grading-κ (§5.1).
7. **Coordinated-literature / conflict-of-interest check** *(New, red-team F3)* — cluster studies by **common funder / shared lab / shared sponsor**. A body substantially funded by an interested party is treated as a **single-agenda cluster** for effective-N (a vendor's 12 funded studies ≈ 1 origin for independence purposes). This is the A-track analogue of astroturf detection.
8. **Pool + quantify heterogeneity** — random-effects default; report I², τ², Cochran's Q, and a **prediction interval**; explain heterogeneity (pre-specified subgroups/meta-regression) before averaging it away.
9. **Publication/originating-woozle panel** — funnel plot; Egger's (only if ≥10 studies); trim-and-fill *as sensitivity only*; registry + unpublished-data hunt.
10. **Grade the body per outcome (GRADE)** — rubric below; use **CERQual** for qualitative/heterogeneous bodies (GRADE is calibrated to effect-estimate meta-analysis).
11. **Sensitivity / adversarial self-review** — leave-one-out; restrict to low-RoB; "does the conclusion survive dropping the highest-risk study?"
12. **Emit graded judgment** (§5.5) with preserved dissent.

### Grading rubric (GRADE × Admiralty, integrated)
**Per-source, two Admiralty axes (anchored, graded via §5.1 protocol):** reliability **A–F**; claim credibility **1–6** (a "1" requires independence *verified*, else it is circular reporting).

**Per-outcome body certainty (GRADE):** start High (RCT) / Low (observational).
- **Downgrade** (−1/−2 each): (1) risk of bias, (2) inconsistency, (3) indirectness, (4) imprecision — **computed, not asserted**: is OIS met? does the CI cross the MID/decision threshold? *(red-team B3)*, (5) publication bias, **(6) NON-INDEPENDENCE** (circular reporting/double-counting), **(7) QUALIFIER-DRIFT from origin**.
- **Upgrade** (observational, no downgrades): large effect (RR>2/<0.5; +2 if >5/<0.2), dose-response, plausible confounding working *against* the effect.
- **Aggregate rule:** certainty = **lowest surviving domain** (bottleneck). **Single-study cap** *(New, red-team B3)*: a body of n=1 publishes **no higher than Moderate** regardless of RoB. Output {High/Moderate/Low/Very-low}, footnoted per domain.

### Guardrails
Frozen protocol vs final report; re-citation adds *zero* weight; duplicate/ shared-author/ shared-dataset/ **shared-funder** de-dup; two axes never merged; "reputable journal" never auto-upgrades certainty; any single test = sensitivity, not truth; CERQual for qualitative bodies.

---

## 4.2 Track B — Direct-Source Aggregation (decision support)

**Native disciplines:** MCDA (Pugh/AHP/MECE/TCO/pre-mortem), review-integrity & astroturf detection, primary-fact verification, Admiralty, ACH, Superforecasting aggregation, ICD-203/BLUF.

### Method
1. **Pre-register the decision frame** — MECE criteria tree; **weights set FIRST, before any score** (timestamped lock); MoSCoW; AHP pairwise (Saaty 1–9, reject if CR>0.10) when contested. Freeze before gathering.
2. **Knockout gate** — Must-have pass/fail *before* weighted scoring; non-compensatory criteria sit outside the additive model.
3. **Reframe as competing hypotheses (ACH)** — options=hypotheses; score by **diagnosticity**; select the **least-disconfirmed**, not the most-praised.
4. **Verify primary facts at the root** — every load-bearing spec/price from the vendor/manufacturer source, recorded value + URL + retrieval date + **cryptographic hash** (hash-and-vault, Bellingcat/Berkeley Protocol). Discard reviewer-paraphrased numbers that conflict with the datasheet.
5. **Grade practitioner testimony for reliability AND independence** — Source-Integrity Scorecard: hands-on tier (measurement/photo/serial > vendor-claimed > anecdote > estimate) × independence status (organic-verified > disclosed-incentivized > insider/affiliate > undisclosed-paid → reject).
6. **Astroturf/echo detection** — near-duplicate text (>~90% = strongest spam signal); burstiness vs baseline; bimodal 5★/1★; singleton-account clusters / co-review collusion; extreme sentiment + low detail; missing verified-purchase. **Collapse coordinated/duplicate clusters to ONE effective source before counting.**
7. **Separate popularity from merit** — volume/rating/sales-rank recorded as a *demand signal only*, **excluded** from merit score.
8. **Aggregate by weighted consilience** — merit = Σ over *independent* sources of (reliability × certainty); extremize a pooled estimate **only if** the independence gate passes. Fermi-decompose cost-effectiveness estimates; log a Bayesian update trail (prior→posterior + independence check per datum).
9. **Cost = lifecycle (TCO)** — acquisition + implementation + integration + training + ops + downtime/opportunity + decommission over a fixed 3–5yr horizon; build the differentiator, buy the commodity.
10. **Robustness release gate** — perturb each weight ±10/±20%; compute weight-stability interval (min change that flips the winner). **ROBUST** → publish; **FRAGILE/near-tie** → publish as a tie with the deciding assumption named ("X wins IFF cost weighted > reliability"). **Pre-mortem** (T+12mo failure; silent independent write-down before discussion → risk register).
11. **Emit graded recommendation** (§5.5) — decision + calibrated confidence + named "this flips if…" assumption + preserved strongest dissenting hands-on review.

### Grading rubric
- **Score-cell provenance tier:** measured/benchmarked (incl. C-internal) > vendor-claimed > testimony/anecdote > analyst-estimate. Low-tier cells flag the decision soft on that criterion and stay internal.
- **Decision certainty = margin-of-victory + weight-stability interval** (robust vs fragile); AHP adds CR≤0.10; TCO grade = horizon completeness.

### Guardrails
Weights locked (timestamp) before scores; ≤7 criteria; MECE-validated; knockouts outside the additive model; provenance tiering forces trace-to-primary-artifact (a claim in ten blog posts = ONE low-tier source until benchmarked); report rank-stability under criterion add/drop; quarantine (never delete) flagged evidence; actively seek missing negative reviews (review file-drawer).

---

## 4.3 Track C — Original Primary Research

Two sub-modes (§2.1). **C-internal** runs only the *measurement-integrity core* (steps 3–5, 11–12 below + a stopping rule). **C-publishable** runs the full loop — *its output becomes someone's root*, so the entire track is engineered to prevent minting a false fact.

**Native disciplines:** Total Survey Error (Groves/Dillman/AAPOR), psychometrics & validity (Messick/AERA-APA-NCME/Tourangeau/Willis), experimental design & pre-registration (Fisher/Simmons/Nosek/Gelman/Kahneman), ICD-203.

### Loop: Design → Instrument → Pilot → Field → Analyze → Report
**DESIGN**
1. **Pre-register (time-stamped, read-only)** — hypothesis, design, DV operationalization, exact primary analysis, exclusion rules, sample size + derivation, confirmatory/exploratory split. *(C-publishable required; C-internal: pre-state hypothesis + primary metric + stopping rule.)*
2. **Forking-paths inventory** — enumerate every analytic decision + options *before* analysis; unavoidable forks → **multiverse/specification-curve**, report the whole distribution.
3. **Control the counterfactual** — randomization (scheme + seed) + genuine control arm + positive/negative controls (instrument can detect signal and does not manufacture it). **Stopping rule stated in advance** (kills optional stopping). *(Both sub-modes.)*
4. **Blinding matrix** — who is masked at allocation/conduct/scoring/analysis; blind-analysis where possible (tune on label-scrambled data, lock, unblind).
5. **TSE error-budget** — 7 sources (coverage, sampling, nonresponse, adjustment, validity/specification, measurement, processing); budget against the dominant one. **Probability-sampling basis required to license inference**; non-probability samples labeled *descriptive only, error unquantifiable*. *(Both sub-modes measure honestly.)*

**INSTRUMENT** *(C-publishable)*
6. **Construct→question blueprint**; five-sources validity plan (content, response-process, internal-structure, relations, consequences — Messick).
7. **Item-writing hygiene** — one construct per item; kill double-barreled/leading/loaded/presuppositional wording (the survey analogue of *originating* a woozle — baking the conclusion into the question); balanced scales; counterbalance order.
8. **Content validity quantified** — expert panel → I-CVI ≥0.78, Lawshe CVR ≥ critical value.

**PILOT** *(C-publishable)*
9. **Adversarial instrument review + cognitive interviewing** — Willis five probe types on 5–15 respondents, iterative; the designer is the *least* reliable judge of clarity. **Adversarial collaboration:** proponent + skeptic pre-agree what each outcome proves.

**FIELD**
10. **Dillman Tailored Design** — 4–5 timed contacts, small prepaid incentives, personalization, sponsor for trust, mixed-mode. *(C-publishable.)*
11. **Data-quality controls** — screen fraudulent/bot respondents (burstiness, duplicate free-text, straight-lining, deviation); record material connections/incentives (FTC-style). *(Both.)*

**ANALYZE**
12. **Confirmatory vs exploratory ledger** — each claim tagged C (tested) or E (hypothesis-generating; labeled + down-weighted + needs independent replication). Deviations table. *(Both.)*
13. **Reliability report card** — Cronbach's α / McDonald's ω (bands; >.95 flags redundancy); test-retest ICC / weighted κ; inter-rater κ. Reliability ≠ validity. *(C-publishable.)*
14. **Validity argument** — five-sources matrix Absent/Weak/Moderate/Strong; EFA→CFA (CFI/TLI ≥.95, RMSEA ≤.06, SRMR ≤.08); convergent/discriminant (MTMM); known-groups. *(C-publishable.)*
15. **Nonresponse bias analysis** — Bias ≈ (m/n)·(ȳ_resp − ȳ_nonresp); *rate ≠ bias*; compare respondents vs frame/benchmark; early vs late responders. *(C-publishable.)*

**REPORT** *(C-publishable)*
16. **AAPOR disclosure block** (release gate) — sponsor, population, frame+coverage, sample design & selection probabilities, mode(s), dates, n + MoE/CI + design effect, exact wording & order, weighting, outcome rates (publish **RR3 with e-method disclosed**, never RR1 alone). MSE framing: a tight CI reflects *sampling error only*; coverage/nonresponse/measurement bias sit outside it and must be disclosed.
17. **Release gate:** only C-tagged claims meeting the reliability floor AND ≥Moderate validity on load-bearing sources AND surviving the pre-registered analysis (and multiverse, where run) publish. E-tagged and low-confidence stay internal.

### Guardrails
p-hacking, HARKing, forking-paths, optional stopping, selective reporting, observer/expectancy bias, confounding, publication bias (Registered-Reports logic), response-rate fetish, big-N illusion, precision-mistaken-for-accuracy, specification error, leading/acquiescence/social-desirability wording, mode effects, non-probability laundered as generalizable, α-mistaken-for-validity. **The design, not the analyst's virtue, prevents the bias.**

---

## 5. The Shared Spine (all modes)

### 5.1 Two-axis grading — now OPERATIONAL *(red-team B1/B2)*
Every load-bearing claim carries, separately: **source reliability** (Admiralty A–F, per-claim-domain); **claim/evidence certainty** (Admiralty 1–6 *and*, where a body exists, GRADE); **likelihood** for estimative claims (§5.5 lexicon).

**Anchored rubric requirement (fixes "aspirational grading").** Admiralty/GRADE terms ship **only** with:
- an **anchored rubric with a worked exemplar per grade** (what a B-source vs C-source looks like; what "2" vs "3" credibility requires) — the remedy Irwin & Mandel prescribe.
- a **grading inter-rater check:** dual-grade a random ≥10% sample of load-bearing sources; compute grading-κ; **floor ≥0.61** (same as screening). Below floor → the rubric is re-anchored before grades are trusted. Grading that isn't reliability-tested is "vibes with letters" and may not feed the gate.

**Blind-order via role separation (not self-blinding).** *Self-blinding by one agent is theater* — an agent that read the source cannot un-know its venue. Therefore: on STANDARD/HEAVY tasks, **split grading across two roles** — Grader-1 sees only the claim text, venue/author/funder metadata stripped, and assigns credibility 1–6; Grader-2 attaches provenance and assigns reliability A–F. On LITE, drop the blind claim and rely on the **diagonal-clustering detector as post-hoc audit, honestly labeled detection-not-prevention.** Auto-flag any release set clustering on A1/B2/C3 (Baker smell).

### 5.2 Independence / consilience test
For every load-bearing claim:
1. **Backward citation-chase** — follow each cite upstream hop-by-hop until (a) primary data/method or (b) an unsupported assertion. Record edge list `[claim ← A ← B ← ORIGIN]`; stop echoing at the first ungrounded node.
2. **Origin de-dup → effective-N** — collapse cites to roots; report independent-origin count (the "4-million-victims"/Porter-Jick opioid cases).
3. **Independence audit — SEVEN shared-dependency channels** *(expanded, red-team D1).* A corroborating source counts as independent only if clean on all seven: shared **data**; shared **author/lab**; shared **upstream citation**; shared **funder/agenda**; shared **propagation vector** (both scraped from one Wikipedia sentence = citogenesis); **#6 shared-model/shared-corpus** (were both lines produced or mediated by the same model family or the same training crawl? — two "independent" agent summaries can echo because both models absorbed the same source); **#7 temporal-cascade** (did line B appear *only after and downstream of* line A's publication date — the citogenesis timing signature? require dates on all lines).
4. **Qualifier-drift diff** — compare wording at each hop vs origin; flag modal downgrades ("may"→"is"), dropped scope/sample caveats, contextomy. Catches us *originating* a woozle in our own drafts. **Machine-checkable target: drift-diff must be empty for a high-confidence claim.**
5. **Consilience when origin unreachable — disjointness must be ARGUED, not asserted** *(red-team D2).* Require ≥2 lines differing in **method AND data AND investigator**, converging. **Default-skeptical prior: treat error modes as CORRELATED unless disjointness is affirmatively argued** (name each line's failure mode; show by argument or data that the two methods do not fail on the same inputs). Absent that argument, **consilience does NOT upgrade confidence.** Extremize/upgrade only across genuinely independent lines.

### 5.3 The Release Gate — with root-veracity, hard-fail, and staleness
A claim ships as OUR judgment only if it passes ALL. Items marked **[MACHINE]** are checked by a deterministic non-LLM checker (§7.2), not an agent.

- [ ] **[MACHINE] Traced to root** (root reached, root-type recorded) **AND**
- [ ] **Root-veracity established** *(New, red-team A1/A2).* For any load-bearing claim resting on a **single origin**, one of: (a) an independent confirming line (consilience, §5.2.5), or (b) an explicit **`single-sourced, unverified-at-root`** flag that **caps published confidence** — such a claim may not ship above "Low/roughly-even" and may never be labeled FACT. A clean single root is **not** high-confidence by default.
- [ ] **Mechanism = a checked entailment, not a narrative** *(New, red-team A2).* "Why it's true" passes only if ≥1 **entailment was checked against independent data** ("if this mechanism holds, X and Y must also be observed — are they?"). An unchecked causal story is tagged **JUDGMENT, not FACT.** (LLM agents generate plausible mechanisms for false claims; narrative alone is not evidence.)
- [ ] **[MACHINE] Effective-N and independence verified** — 7-channel audit clean; effective-N **≥2** required for any high-confidence claim.
- [ ] **[MACHINE] Qualifier-drift diff = empty** vs origin.
- [ ] Two-axis grade recorded (reliability × certainty); body-certainty where applicable; grading-κ ≥ floor.
- [ ] If origin unreachable, **consilience across argued-disjoint error modes** documented (§5.2.5).
- [ ] **[MACHINE] Staleness / retraction check** *(New, red-team F2).* Vaulting freezes provenance, not currency. Re-validate at publish against a mode-specific TTL: **prices ≤ days, specs ≤ months, literature = query retraction databases at release.** A stale/retracted root fails the gate.
- [ ] Meets the mode-specific confidence floor (A: not Very-low unless flagged; B: ROBUST or fragile-with-named-flip; C-publishable: confirmatory + reliability floor + ≥Moderate validity).
- [ ] Dissent/counter-line preserved.
- [ ] Low-confidence grading kept internal (logged, not published as fact).
- [ ] Calibrated confidence stated (no hedge-mush, no overclaim).

**HARD-FAIL class (cannot be softened) *(New, red-team F1).*** A load-bearing claim with **neither a reachable root NOR argued independent consilience** cannot publish as any grade of fact **or** judgment. It enters the decision only as a labeled **assumption/open-question**, and the decision's robustness must be tested **as if that claim could go either way** (wire into §4.2-step-10 sensitivity). This closes the v1 "publish with a downgrade" escape hatch for the unknowable case.

**All other fails → hold, or publish with an explicit downgrade + stated limitation.** The gate blocks *both* continuing and originating a woozle — and now blocks the *true-looking single root*, which the v1 gate did not.

### 5.4 Trace-to-root + mechanism
"Supported" = traced to the primary source (root that holds the justification) AND a **checked** reason it's true (data/method/entailment, §5.3). A chain dead-ending at an assertion is ungrounded regardless of how authoritative the intermediaries look ("dead-end authority").

### 5.5 Analytic-judgment output format (BLUF/Minto + ICD-203 + IPCC)
1. **BLUF** — one-sentence governing judgment first.
2. **2–4 MECE key judgments**, each **dual-tagged**: `[claim] — probability_term (numeric band); confidence High/Mod/Low, because [1-line basis]`. Never blend probability and confidence.
3. **Evidence** under each; each load-bearing claim shows root_source + independence flag + (single-sourced flag if applicable).
4. **FACT / ASSUMPTION / JUDGMENT labels** on every load-bearing sentence — so our inference is never re-cited downstream as sourced fact.
5. **Traceable account** — evidence type/amount/quality/consistency; how conflicting lines were reconciled.
6. **Dissent register** — preserved minority view, who holds it, the indicator that would vindicate it.
7. **"So what"** — explicit implication.

**Estimative lexicon (fixed 7 rungs, ODNI):** almost-no-chance 01–05 · very-unlikely 05–20 · unlikely 20–45 · roughly-even 45–55 · likely/probable 55–80 · very-likely 80–95 · almost-certain 95–99. Reject free-text probability synonyms.
**Analytic-confidence rubric (7 factors → H/M/L):** source reliability; corroboration+independence; expertise; peer-review/collaboration; task complexity; time pressure; structured-method-actually-used. Confidence is *not* probabilistic and never merged with likelihood.

### 5.6 Fusion protocol for mixed/decomposed tasks *(New, red-team C3)*
When a task decomposes (e.g. a Mode-B recommendation embedding a Mode-A literature sub-task):
1. Each sub-task output enters the parent as a **graded input at its own confidence** — **never upgraded by inclusion.**
2. When sub-tasks **disagree**, resolve by the independence/diagnosticity logic (§5.2): the line with **argued-disjoint error modes** wins; do not average.
3. The parent judgment's confidence is **capped at the lowest load-bearing sub-task's confidence**, unless genuine consilience across independent sub-tasks affirmatively raises it.
4. An embedded sub-claim may **never** be re-cited as if the whole parent recommendation validated it (anti "the B recommendation proves the A claim"). The seam is where woozles re-enter; it is now explicitly guarded.

---

## 6. Concrete artifacts to build

| # | Artifact | Key fields | Used in |
|---|---|---|---|
| 0 | **Intake triage card** *(new)* | stakes/reversibility tier {LITE/STANDARD/HEAVY} + escalation triggers; root-availability {rootable/consilience-only/unknowable→hard-fail} | all |
| 1 | **ACH matrix** | rows=evidence (reliability-grade + root-ID); cols=hypotheses/options; cells C/I/N-A *across* rows; per-row diagnosticity; per-col Inconsistent tally; conclusion=least-disconfirmed + rejected + why | A, B |
| 2 | **Admiralty 6×6 grid + anchored rubric** *(expanded)* | separate `{reliability A–F, credibility 1–6}`; **per-grade worked exemplar**; role-split blind-order; grading-κ sample; diagonal-clustering (Baker) detector | all |
| 3 | **GRADE/CERQual evidence profile / SoF** | per outcome: #studies&design · RoB · inconsistency · indirectness · imprecision (**OIS/MID computed**) · pub-bias · **non-independence** · **qualifier-drift** · upgrades · effect+CI · **certainty** · **single-study cap** · footnote-per-domain | A |
| 4 | **Citation-chain ledger + effective-N table** | claim · citing node · that node's support · hop-to-root · root-type {primary/method/assertion/dead-end} · reached-origin Y/N; cites→roots → effective-N vs raw | all |
| 5 | **Independence audit matrix (7 channels)** *(expanded)* | rows=sources; cols=data/author/upstream-cite/funder/propagation/**shared-model-corpus**/**temporal-cascade**; independent only if all "no" | all |
| 6 | **Qualifier-drift diff** | origin wording vs ours, highlighting modal/scope changes; **empty = pass** | all (esp. C) |
| 7 | **Consilience worksheet** *(strengthened)* | each line: method/data/investigator/**named error-mode**; **disjointness argument (default: correlated)**; convergent only if disjointness argued | all |
| 8 | **Key Assumptions Check** | Assumption · Why-believed · Confidence H/M/L · What-would-falsify · Supported Y/N · If-false-does-conclusion-collapse | A, B, C |
| 9 | **Mode-B decision matrix** | Option × [criterion: weight%, score 1–5, weighted, provenance-tier, source-URL/hash]; weights sum 100%, ≤7 criteria, **weights locked (timestamp) before any score** | B |
| 10 | **MoSCoW knockout checklist** | Must-have pass/fail; any fail eliminates pre-scoring, logged | B |
| 11 | **TCO worksheet** | acquisition/implementation/integration/training/ops/downtime/decommission × Y1–Y5 + NPV; direct/indirect flag | B |
| 12 | **AHP pairwise-weight sheet** | n×n reciprocal (Saaty 1–9), eigenvector weights, auto CR, hard CR≤0.10 gate | B |
| 13 | **Sensitivity/robustness report** | per-weight ±10/±20%; weight-stability interval; ROBUST/FRAGILE; rank-stability under criterion add/drop; **hard-fail-claim two-way test** | B |
| 14 | **Pre-mortem protocol** | T+12mo failure; silent independent write-down; merge → risk+mitigation register | B, C |
| 15 | **Source-Integrity Scorecard** | hands-on tier · independence status {organic/disclosed-incentivized/insider/affiliate/undisclosed-reject} · track-record · duplicate-hash · burst-cluster-id · rating-deviation · reliability A–F · certainty 1–6 | B |
| 16 | **Astroturf red-flag checklist** | near-duplicate; burst-vs-baseline; bimodal 5★/1★; singleton/new-account cluster; co-review collusion; extreme-sentiment+low-detail; missing verified-purchase; undisclosed #ad | B |
| 17 | **Vendor-fact verification + hash-vault + TTL** *(expanded)* | claim · reviewer-reported · primary value · URL · retrieval date · hash · **TTL/staleness re-check date** · status {verified/conflict/unverifiable/stale} | B, Lite |
| 18 | **Pre-registration template** | status · hypothesis · DV/operationalization · conditions & assignment · exact primary analysis · outlier/exclusion rules · sample size + derivation · secondary/exploratory; time-stamped read-only | C-pub (C-int: lite version) |
| 19 | **21-word disclosure block** | "We report how we determined our sample size, all data exclusions, all manipulations, and all measures" + 6-req checklist | B, C |
| 20 | **Instrument-review checklist** | construct→question blueprint · item-hygiene rows · CVI/CVR sheet · Willis 5-probe bank + per-item problem log | C-pub |
| 21 | **Five-sources validity matrix** | content/response-process/internal-structure/relations/consequences × evidence · method · result · grade Absent/Weak/Mod/Strong · threat-if-missing | C-pub |
| 22 | **TSE error-budget + AAPOR disposition/disclosure block** | 7 error sources × threat/mitigation/residual/bias-direction/how-checked; disposition→RR3(e-disclosed)/COOP1/REF1/CON1; disclosure release-gate | C |
| 23 | **Forecast/calibration scorecard + proxy-resolution** *(expanded)* | Brier + Murphy decomposition; per-agent calibration curve; Bayesian update log; **proxy-resolution sources: later replications, post-hoc root discovery, reviewer-caught errors** | B, C, all confidence labels |
| 24 | **Dual-uncertainty judgment block** | BLUF · MECE dual-tagged judgments · FACT/ASSUMPTION/JUDGMENT · traceable account · dissent register · "so what" | all |
| 25 | **Release-gate checklist** | the §5.3 pass-all list, [MACHINE] items marked | all |
| 26 | **ICD-203 nine-standard checklist** | source-quality · uncertainties expressed+explained · fact-vs-assumption-vs-judgment · alternatives · relevance/"so what" · logical argumentation · consistency/change-from-prior · accuracy · effective visuals | all |
| 27 | **Root-veracity & single-source card** *(new)* | root-reachability Y/N · root-veracity method {consilience / checked-entailment / single-sourced-flag} · mechanism entailment checked Y/N · confidence cap applied | all |
| 28 | **Fusion ledger** *(new)* | sub-task · mode · own-confidence · conflict-with · resolution (diagnosticity/independence) · parent-confidence-cap applied Y/N | mixed tasks |
| 29 | **Weakest-load-bearing-input statement** *(new, red-team G3)* | the single weakest cell/source the conclusion rests on; artifact-completeness explicitly NOT a pass criterion | all reviewer output |

---

## 7. How it wires into our agents

### 7.1 As a `research-integrity` skill
Runs **intake triage (§1)** then the **mode-selector (§2)** as entry point; routes to Lite / A / B / C-internal / C-publishable; exposes artifacts (§6) as fillable templates; enforces the **release gate (§5.3)** as a hard pre-publish check with deterministic [MACHINE] predicates; emits the **dual-uncertainty judgment block (#24)**. Loads on any research/analysis/reporting/recommendation deliverable.

### 7.2 Workflow shapes that enforce it
- **Producer/Reviewer split with ARCHITECTURAL INDEPENDENCE (HEAVY, mandatory)** *(red-team A3/G2).* The reviewer must be a **different model family and/or config** than the producer — not another instance of the same architecture (same corpus, same blind spots = illusory independence, the D1 problem applied to ourselves). The reviewer re-runs the independence audit, checks qualifier-drift, challenges the least-disconfirmed conclusion, verifies each load-bearing claim to root, and **states the weakest load-bearing input (#29)** — passing is forbidden on artifact-completeness alone ("beautifully-documented garbage" test). Reviewer has standing to fail the gate.
- **Deterministic (non-LLM) gate checker** *(red-team A3/G2).* All **[MACHINE]** predicates — hash present for every priced spec, effective-N ≥2, drift-diff empty, weights-lock-timestamp precedes first score, TTL not expired — are checked by **rules code, not an LLM.** LLMs never self-certify the machine-checkable items.
- **Gate-pass-rate alarm** *(red-team A3).* Log gate-pass rate. A near-100% pass rate means the gate is rubber-stamping; it trips an alarm and forces rubric/reviewer recalibration.
- **Adversarial verify / dissent institution.** C: adversarial-collaboration pair (proponent + skeptic pre-agree what each outcome proves). B: pre-mortem with silent independent write-down (blocks the woozle-in-the-room). A: devil's-advocate on the hypothesis set ("which hypothesis did we NOT consider?").
- **Completeness critic.** Re-reads the request line-by-line, checks ICD-203 nine standards (#26), confirms dissent preserved and low-confidence grades kept internal.
- **Independent-method verifier.** Verifies load-bearing numbers by a *different route* than the one that produced them (brute-force vs clever; bottom-up rebuild of a top-down figure; a second independent source) — catches wrong thinking, not just typos.

### 7.3 Enforcement points (gates)
1. **Intake gate** — triage (§1) + mode-selector (§2) must run before any research; genre pre-filter applied; mixed tasks decomposed with a fusion ledger (#28).
2. **Weights/protocol lock gate** — A protocol / B weights timestamped *before* evidence; C pre-registration read-only *before* data. Enforced by [MACHINE] timestamp check.
3. **Grading gate** — no load-bearing claim proceeds without two-axis grade (anchored rubric + grading-κ) + 7-channel independence audit + effective-N.
4. **Release gate** — §5.3, [MACHINE] items by the deterministic checker, judgment items by the architecturally-independent reviewer; hard-fail class cannot be softened.

### 7.4 Calibration feedback loop — with proxy-resolution *(red-team G1)*
Log every published probabilistic judgment. Where ground truth arrives, score it (Brier + Murphy, #23) and down-weight poorly-calibrated agents/sources in future aggregation (GJP track-record weighting). **Because most research/synthesis claims never resolve against reality, add proxy-resolution:** score against **later independent replications, post-hoc primary-source discovery, and reviewer-caught errors.** State honestly: **for never-resolving claims the long-run defense is the producer/reviewer split and the release gate, not calibration** — calibration is *a* defense, not *the* defense.

---

## 8. Rejected / partially-rejected critiques (with reason)

- **[PARTIALLY REJECTED] B3 "domain-splitting games the bottleneck."** The concern that "catastrophic on one domain vs on all seven land at the same grade" is *by design* — a single fatal flaw should cap the grade regardless of other strengths (a bottleneck is not an average, and that is the point). We adopt the *actionable* half (single-study cap + computed imprecision) but reject adding an anti-"domain-splitting" mechanic: the GRADE domains are fixed and not analyst-addable, so there is nothing to split. No change beyond the single-study cap.
- **[NOTED, NOT A SPEC CHANGE] "26 artifacts look authoritative regardless of input (G3)."** Correct and important, but the fix is behavioral, not structural: it is handled by the **weakest-load-bearing-input statement (#29)** and the reviewer duty in §7.2, plus the proportional Lite track (§4.0) that stops most tasks from generating the full 29-artifact edifice at all. We add the artifact and the duty; we do not add a further meta-artifact (which would itself be more paperwork).
- **[ACCEPTED with scope note] D1 shared-model dependency.** Fully adopted as channels #6/#7. Scope note: channel #6 can over-fire (nearly all modern web text is model-touched), so it is a *flag-and-argue* channel, not an auto-reject — it demands an independence argument, matching the §5.2.5 default-skeptical treatment.

---

## Open questions before build

1. **Grading-κ cost.** Dual-grading ≥10% of sources doubles appraisal cost on that sample. Is ≥0.61 the right floor for LITE (or does LITE skip grading-κ entirely, accepting single-grader risk)?
2. **Reviewer model diversity.** Which specific *different model family* backs the HEAVY-tier reviewer, and is a rules-only checker sufficient for the [MACHINE] predicates or do some need a second LLM? (Cost + availability tradeoff.)
3. **TTL defaults.** Concrete TTLs per claim class (prices/specs/literature) need to be set with domain owners; retraction-database coverage varies by field.
4. **Channel-#6 firing rate.** Needs an empirical pilot — if "shared-model/corpus" flags fire on nearly everything, the independence-argument burden may need a materiality threshold.
5. **Effective-N ≥2 for high-confidence.** Does a single *gold-standard* primary source (e.g. a pre-registered RCT we fully verified) ever merit high confidence at effective-N=1, or is the single-source cap absolute? (Tension between §5.3 single-source cap and rare high-quality solo evidence.)
6. **C-internal / C-publishable reclassification.** What triggers promotion of a C-internal benchmark to C-publishable mid-stream (e.g. someone later cites it externally), and can we retroactively impose the full validity load?
7. **Grading role-split staffing.** The two-grader blind-order (§5.1) adds an agent per load-bearing source batch — acceptable at STANDARD, or reserve strict role-split for HEAVY only?

---

## 9. Delivery model & decision-tagging (dual-purpose: skill-first, app-later)

**This system ships in two forms that share ONE engine (this spec's decision tree). Build in order:**

1. **PRIMARY — the `research-integrity` skill** (build first). A portable skill (`SKILL.md` + artifact templates) that runs in **any agent context**: Claude Code (`.claude/skills/`, project or user-level), **Cowork**, and ad-hoc agent invocations. It encodes the intake triage → mode-selector → per-track steps → shared spine → artifacts, and drives the producer/reviewer split via the subagents/workflows available in each context. This is what makes the agents work for us *now*.
2. **LATER — the web app.** A UI that renders the identical decision tree as an **enforced** flow (asks one question at a time, per §0/§1/§2), gates on the release-gate checks, and stores the artifacts. The app is a front-end on the same engine, not a re-implementation.

### 9.1 Advisory-in-skill vs. enforced-in-app (the enforcement gap, stated honestly)
Consistent with this platform's Excellence-Pass principle (instructions transfer the *process*; structure *enforces* it):
- **In the skill**, the gates are **advisory + best-effort structural**: the producing agent self-applies the checklists, a **separate reviewer subagent** (distinct role prompt; different model/config where the context allows) re-checks, and the deterministic `[MACHINE]` predicates run as tool/code checks where possible. An agent *can* skip them — a periodic agent-retro loop catches misses.
- **In the app**, the same gates are **hard-enforced**: you cannot mark a claim published until root-veracity, independence/effective-N, qualifier-drift, and dissent checks are green. Same checks, stronger binding.
- **Design rule:** every gate in this spec must be expressible as a checklist the skill can run *and* a predicate the app can enforce — no gate may depend on the app existing.

### 9.2 The 7 open questions — tagged + recommended defaults (so nothing blocks the skill build)
Each is `[ASK-PER-TASK]` (the flow/app surfaces it in context, only when the tier warrants) or `[GLOBAL-CONFIG]` (a settings default). Defaults below are what the skill uses today; the app later makes the per-task ones interactive.

1. **Grading-κ cost** — `[GLOBAL-CONFIG by tier]` · *Default:* LITE skips grading-κ (single-grader accepted — low-stakes/reversible); STANDARD dual-grades a ≥10% sample; HEAVY dual-grades all load-bearing sources.
2. **Reviewer model diversity** — `[GLOBAL-CONFIG]` · *Default (skill):* reviewer = a fresh subagent with a distinct role prompt + rules-only checks for `[MACHINE]` predicates. *Upgrade path:* route HEAVY-tier review to a genuinely different model family once infra allows. (The app enforces.)
3. **TTL defaults** — `[GLOBAL-CONFIG]` · *Default:* prices 7 days · specs 90 days · literature 12 months · security advisories 24h. Domain owners tune.
4. **Channel-#6 firing rate** — `[ASK-PER-TASK / pilot]` · *Default:* treat "shared-model/corpus" as flag-and-argue (not auto-reject); require the independence argument only for **load-bearing** claims until a pilot sets a materiality threshold.
5. **Effective-N=1 high confidence** — `[ASK-PER-TASK]` · *Default:* single-source cap holds (max **Moderate**) — BUT a fully-verified gold-standard primary (pre-registered RCT / primary regulatory filing / raw dataset we checked) may be promoted to **High** via an **explicit, logged per-claim override** the reviewer signs. Cap by default; override is deliberate, never silent.
6. **C-internal → C-publishable reclassification** — `[ASK-PER-TASK / trigger]` · *Default:* promotion trigger = any external citation OR a decision to publish. On promotion the full validity load applies **going forward**; internally-collected data is labeled *"provisional — not collected under publishable controls"* and **cannot** retroactively claim publishable rigor (re-run or retro-validate to earn it).
7. **Grading role-split staffing** — `[GLOBAL-CONFIG by tier]` (ties to #1) · *Default:* LITE none; STANDARD single grader with a self-blind-order pass; HEAVY strict two-agent role-split.

### 9.3 Build order for the skill (what to author first)
1. `SKILL.md` = the intake triage + mode-selector + the shared-spine gates + the tier defaults above.
2. The **highest-leverage artifacts** as fillable templates: ACH matrix (#1), GRADE/SoF profile (#3), citation-chain ledger + effective-N (#4), independence audit (#5), Mode-B decision matrix (#9), pre-registration (#18), and the report structure (BLUF/Minto).
3. Wire into the research charters (the council's market-evidence seat `market-insight`, where the `blackraptor-council` pack is installed, and any research task) and the standard research-workflow shape (batched fan-out → producer/reviewer split → completeness critic → graded judgment). *(Cross-pack name appears here only as build-order commentary — guarded by "where installed", not a dispatch.)*
4. Everything else in §6 is added as tasks demand (proportionality — don't build all 29 up front).