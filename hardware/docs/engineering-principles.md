# Engineering Principles & Laws — the Team Canon

*Binding reference for every agent on the BlackRaptor hardware engineering team. Read alongside CLAUDE.md. Compiled 2026-07-24 from primary-source research; every quantitative claim carries a source or an explicit flag. Laws are exact physics; correlations are engineering approximations with error bands; conventions are industry practice. Do not blur the three.*

*Honesty discipline inherited from the operating standard: claims marked `[UNVERIFIED]` were not confirmed against a primary source and must be verified before they become load-bearing in a deliverable. Attribution grades on maxims are stated exactly.*

---

## Part I — The design philosophy (governs every decision)

**The mission is the least expensive device that functions in its conditions for its design life — nominally 3–5 years — and is then replaced.** Not the best device. Not the longest-lived. The adequate device, proven adequate.

1. **Cost is a requirement, not an outcome.** Design-to-cost is a formal discipline (root: US DoD Directive 5000.1, 1971 — cost treated "equally with performance" as a design parameter; GAO PSAD-75-91, 1975). Japanese target costing (genka kikaku, formalized at Toyota 1963) works backwards: allowable cost = sales price − target profit, set *before* design. A design that misses its cost target fails review exactly as one that misses a thermal or EMC requirement.
2. **Design to the target life, price the margin.** Reliability beyond the required life is inventory the customer pays for and never consumes. Every increment of margin — higher-grade part, deeper derating, thicker wall — has a unit cost. Wear-out mechanisms are engineered to clear the design life with stated confidence, not to maximum achievable life (Part III §4).
3. **The adequacy guardrail (why "cheap" doesn't mean "flimsy").** Designing exactly to 3–5 years against an *average* environment delivers 1–2 years in the field, because life models are exponential in temperature — a small error in assumed ambient produces a large error in life. Therefore: size **wear-out** mechanisms against the worst-case/percentile deployment environment (hot-climate, sun-loaded, high-duty unit — the unit that sets warranty economics), while predicting **random-failure** rates with realistic average profiles (the ESA reliability handbook's position, verified). Design life is met at the corner, not the median.
4. **Where cheapness must NOT win:** safety, regulatory compliance, and single points of failure whose expected field cost exceeds the savings. The governing arithmetic: expected field cost = failure rate × cost per event (truck roll + replacement + warranty + reputation). Spend on prevention up to that expectation and not beyond. For a sealed whole-unit-swap outdoor device, one field event typically exceeds the BOM savings of many cheapened parts — run the number, don't guess it.
5. **Value engineering is the method** (Lawrence D. Miles, GE, December 1947): state every part's function in verb-noun form ("conduct current", "seal enclosure"), then find the cheapest way to deliver that function at required reliability. Value = function ÷ cost. A part with no articulable function is deleted. The Muntz test — remove parts until it breaks, then restore one — is admissible **only when "does it still work" is evaluated at the environmental corners, not the bench** (Muntz's cheap TVs failed in weak-signal markets; grade: consilience, Time 1953 + retrospectives).
6. **Cost is committed at concept, spent at production.** The classic "70–80% of cost is fixed in design" figure has no verified primary root — treat the number as folklore — but the shape is empirically supported: a 7-year aerospace study (Tan/Otto/Wood, ICED17 2017) found early design decisions carried 86% of potential rework cost and cost 5–13× more to change late. Corollary: the cost review gates the *concept* (architecture, part count, enclosure approach, compute platform), not just the DFM pass. Same evidence base grades the "rule of 10" (change cost ×10 per phase): real escalation, mnemonic multiplier (NASA/INCOSE 2004 error-cost-escalation study).

---

## Part II — Physical laws and canonical design equations

*Exact physics unless marked otherwise. Each entry: what it is → what it governs on a sealed, fanless, outdoor, conduction-cooled compute device.*

### Circuits and power
- **Ohm's law** V = IR — every trace, connector, and cable drops voltage under load; size copper so distribution drops stay inside regulator input tolerance.
- **Kirchhoff's laws** ΣI(node) = 0, ΣV(loop) = 0 — all return currents come home (uncontrolled returns are EMI antennas); every millivolt from AC input to point-of-load is budgeted around a loop.
- **Joule heating** P = VI = I²R — the *source term* of the entire thermal problem; in a fanless sealed box every I²R watt must reach the aluminum wall. Quadratic in I: halve the current (raise the distribution voltage), quarter the loss.
- **Energy storage** E = ½CV², E = ½LI² — ½CV² is the ride-through currency and the inrush hazard; ½LI² is the interrupted-inductor spike that sizes clamps/TVS.
- **Time constants** τ = RC, τ = L/R; 63% at 1τ, 99% at 5τ — power-good delays, brown-out windows, soft-start, debounce, filter corners f_c = 1/2πRC.
- **Holdup/ride-through** E_usable = ½C(V_nom² − V_UVLO²) — only the energy above undervoltage-lockout counts. The V² term means holdup is far cheaper at high bus voltage than at 12 V. Capacitance and equivalent series resistance (ESR) derate hard at −40 °C — cold-soak is the sizing corner.
- **Converter loss partition** P_loss = P_conduction (∝ I²R_ds) + P_switching (∝ V·I·t_transition·f_sw) + fixed — identity is exact; individual terms are models (±20–30 % until measured `[UNVERIFIED band]`). At η = 0.90 a 30 W load injects 3.3 W of heat; at 0.95, 1.6 W — efficiency is thermal design.
- **ESR heating** P = I_rms²·ESR — heat generated *inside* the capacitor; capacitor core temperature is the life-limiter (Part III). Ripple-current rating is a reliability spec, not a performance spec.
- **Inrush** i = C·dv/dt limited only by series impedance — NTC inrush limiters are cold (protective) outdoors but recover slowly after brief outages: hot-restrike is the trap case.

### Heat
- **First law of thermodynamics** — steady state: every electrical watt in = heat out. The enclosure has exactly three exits: conduction to mount, convection from shell, radiation from shell. The enclosure never reduces the heat; it only sets the ΔT at which balance occurs.
- **Second law** — heat flows hot→cold only; no passive structure cools below ambient. Junction > case > shell > ambient, always. Passive design is ΔT management, never refrigeration.
- **Fourier conduction** Q = kA·ΔT/L; R = L/kA — the conduction spine: die → package → thermal interface → wall. Aluminum k ≈ 167–200 W/m·K, FR-4 through-plane ≈ 0.3, TIM pads ~1–6 (handbook figures — verify per selected material). The TIM joint, not the aluminum, usually dominates.
- **Thermal resistance networks** T_j = T_a + P·θ — the most-used equation in the program. Caution (correlation): datasheet θ_ja is measured on JEDEC boards in free air and can be off 2× in-enclosure; θ_jc is the trustworthy figure for conduction paths.
- **Newton convection** q = hA·ΔT — correlation, ±10–25 %. Natural convection in gases: **h ≈ 2–25 W/m²·K** (Incropera, *Fundamentals of Heat and Mass Transfer*). At h ≈ 5–10, a 25 W device needs on the order of 0.25–0.5 m² of effective finned area for ~10 °C shell rise. Fins vertical for chimney flow.
- **Stefan–Boltzmann radiation** q = εσA(T_s⁴ − T_surr⁴), σ = 5.670374419×10⁻⁸ W·m⁻²·K⁻⁴ (NIST) — at natural-convection ΔTs radiation carries a share comparable to convection *if* ε is high. Bare aluminum ε ≈ 0.04–0.1; anodized ≈ 0.77+. **A mill-finish enclosure throws away roughly a third of its passive cooling.** Night-sky radiation drives shell-below-dewpoint condensation inside sealed boxes.
- **Solar load** Q = α·G·A_projected — design irradiance: 1000 W/m² (ASTM G173 / NREL AM1.5 reference) to **1120 W/m² worst-case qualification** (MIL-STD-810H Method 505.7). A 0.1 m² sun face at α = 0.5 absorbs ~50–56 W — potentially more than the electronics. Low-α/high-ε finish is a load-bearing design decision, not cosmetics.

### RF and information
- **Maxwell (conceptual):** charges source E-fields; flux lines close (returns always exist); changing B induces V (loop area × di/dt = coupled noise); currents and changing E create B. Every switching converter is a transmitter unless loops are small; the aluminum box is a Faraday cage *except at apertures, seams, and penetrations* — those, not wall thickness, set the shielding.
- **Friis / free-space path loss** P_r = P_t + G_t + G_r − FSPL; FSPL(dB) = 20log₁₀d(km) + 20log₁₀f(MHz) + 32.44 — doubling distance or frequency costs 6 dB. Low cellular bands reach ~9 dB farther than 1.9 GHz — band strategy is physics.
- **Reciprocity** — antenna gain/efficiency identical TX and RX; a detuned antenna degrades both directions equally, and GNSS placement is judged by the same physics.
- **Isolation arithmetic** — cellular TX ~+23 dBm vs GNSS signals ~−130 dBm: ~150 dB apart. Separation, cross-polarization, and filtering are the only levers; without them the transmitter blinds the receiver.
- **Skin effect** δ = √(ρ/πfμ) — RF current lives in microns of surface; anodize is an insulator, so RF bonding points must be masked — plating and gasket conductivity, not bulk metal, set RF performance.
- **Shannon** C = B·log₂(1+S/N) — the hard ceiling: every dB lost in the antenna/enclosure is deliverable-data ceiling lost; no protocol recovers it.
- **Nyquist** f_s > 2f_max with anti-alias filtering — aliased converter noise into slow telemetry ADCs is the classic field-mystery bug.

### Materials and failure physics
- **Galvanic corrosion** — dissimilar metals + electrolyte = battery; the less-noble metal corrodes, fast when the anode is small and the cathode large. Pairing per MIL-STD-889/ASTM G82 series. Aluminum + stainless is acceptable; aluminum + bare copper is a corrosion cell. Bonding points that pierce anodize must be sealed after assembly.
- **Dielectric breakdown** — design spacings to IEC 60664-1 (pollution degree, overvoltage category), not to raw breakdown fields; condensation collapses surface insulation — conformal-coat the AC side.
- **Electromigration (Black's equation, conceptual)** MTTF = A·J⁻ⁿ·exp(Ea/kT), n ≈ 2 — correlation, parameters process-specific. Sustained junction temperature consumes silicon life exponentially: the thermal budget *is* a reliability budget.

---

## Part III — Reliability physics and design-for-target-life

### 1. The vocabulary that prevents wrong decisions
- **Bathtub curve:** infant mortality (screened by test/burn-in) → useful life (constant random rate) → wear-out (rising rate). Weibull shape β < 1 / = 1 / > 1 maps the three regimes.
- **MTBF ≠ life.** Mean time between failures is the reciprocal of the *random* failure rate in the flat region. A 1,000,000-hour-MTBF supply can have a 5-year capacitor wear-out life; only 36.7 % of units survive to the MTBF time (R = e⁻¹) (Bel Fuse, verified). **Rule: MTBF/FIT (failures in 10⁹ hours) governs random-failure probability inside the design life; wear-out is analyzed separately, per mechanism.**
- **Series systems multiply:** R_sys = ΠR_i — always below the worst component. Hundreds of parts at 0.999 over 5 years still compound; allocate the reliability budget top-down.
- **State life with a probability.** "Lasts 5 years" is meaningless; the binding form is "R ≥ X % at 5 years, in the stated (P90) environment, warranty at Y years." Warranty period, design life, and mission life are three different numbers.

### 2. The acceleration laws (how environment buys or costs life)
- **Arrhenius** AF = exp[(Ea/k)(1/T_use − 1/T_stress)], k = 8.62×10⁻⁵ eV/K (JEDEC). Conventional silicon default Ea ≈ 0.7 eV (TI SLAP177, verified); mechanism-specific values live in JEDEC JEP122 `[UNVERIFIED — pull before citing]`. One blanket Ea across mechanisms is a known abuse.
- **Electrolytic capacitor 10 °C rule** L = L₀·2^((T₀−T)/10) — verified at the primary source (Nichicon technical note; Arrhenius basis stated). **Limits, also from Nichicon: 15-year cap on extrapolation; valid roughly 40 °C→rated temp; reference-only, not guaranteed; ripple and voltage multipliers apply.** Ratings run 1,000–10,000 h at 105 °C: a 5,000 h/105 °C part at a 65 °C hotspot models to ~9 years — at 85 °C, ~2 years. This one equation decides whether electrolytics are permissible at each location, or must be designed out (polymer/film/ceramic).
- **Coffin-Manson / Norris-Landzberg (solder fatigue)** N ∝ ΔT⁻ⁿ; SnPb parameters m = 1/3, n = 1.9, Ea/k = 1414 K (verified); lead-free SAC exponents vary by study `[UNVERIFIED — model-dependent]`. An outdoor device sees ~365 diurnal cycles/year → 1,300–1,800 over life; damage ∝ ΔT^1.9 means reducing the daily swing pays superlinearly. Mass helps here: thermal inertia flattens ΔT.
- **Peck humidity model** TTF ∝ RH⁻²·⁶⁶·exp(0.79 eV/kT) (Peck, IRPS 1986, primary verified) — the basis of 85/85 testing. A sealed enclosure controls liquid water, but internal RH tracks ambient through permeation and breathing; condensation events dominate steady RH `[engineering judgment — flag]`. This is the physics behind an internal humidity sensor being cheap insurance.

### 3. Prediction standards (know what each is worth)
MIL-HDBK-217F Notice 2 (1995) — still contractually cited, not maintained for 20+ years, constant-rate assumptions judged obsolete (verified). Practitioner alternatives: Telcordia SR-332 (telecom), FIDES (European, mission-profile based `[UNVERIFIED one-liner]`), ANSI/VITA 51.1 (modifies 217F for modern parts), IEC 61709 (converts reference rates to actual conditions). The practitioner direction is physics-of-failure (per-mechanism modeling) — which is what this canon encodes. Handbook MTBF is a planning bound and a comparison tool, never a life claim.

### 4. Derating for a 3–5 year commercial product (convention, cited)
Two-tier pattern in the published standards — space-grade derates hardest; commercial power-conversion practice is the appropriate citable baseline for this design life:
- **IPC-9592 (power conversion, computer/telecom — our baseline):** ceramic caps ≤ 80 % rated voltage; aluminum electrolytics ≤ 80 % voltage, ≤ 70 % ripple current, ≥ 10 °C below rated temp, prefer ≥ 5,000 h ratings; solid tantalum ≤ 70 % and *not recommended in power designs* (fire hazard). (Verified from draft copy — confirm clause numbers against released IPC-9592B before citing in a spec.)
- **NASA EEE-INST-002 (space — the over-margin reference point):** ceramic 60 % voltage, solid tantalum 50 %/30 % by temperature, film 60 % (verified). Its resistor/semiconductor tables `[UNVERIFIED — pull sections before quoting]`.
- **Semiconductor junction temperatures:** derate to run continuously well below T_j,max — the Arrhenius and electromigration terms make sustained T_j the life dial. Specific ceiling per part is set by the reliability seat from the target life, not copied from a table.
- **Temperature grades:** commercial 0–70 °C / industrial −40–85 °C / automotive −40–125 °C with AEC-Q qualification. Doctrine for this device class: **industrial grade is the floor because the *environment*, not the design life, sets the range**; automotive grade buys qualification depth a 3–5 year life doesn't require unless thermal analysis shows the margin is needed. (Automotive premium ~10–30 % — single secondary source, indicative only.)

### 5. Which wear-out mechanisms matter at 3–5 years outdoors
**Matter — analyze every one, every program:** aluminum electrolytic capacitors (the canonical limiter — design out or size by the verified formula); solder-joint fatigue from diurnal cycling; flash write endurance (NAND program/erase limits are real at 3–5 yr under telemetry write loads — typical published class figures SLC ~60–100k, TLC ~0.5–3k cycles `[UNVERIFIED — verify per selected part]`; a write budget is mandatory); storage-bank aging (supercap/LiC float life vs temperature); connector and contact corrosion (Peck kinetics); gasket/polymer UV and thermal aging — seal degradation then accelerates every humidity mechanism.
**Mostly 10+ year problems — do not spend money on them:** electromigration and oxide wear-out in properly derated silicon, film/ceramic capacitor wear-out, laminate degradation, tin whiskers (mitigated). Fanless design correctly deletes the #2 classic wear-out item (fans) after electrolytics.

---

## Part IV — Cost engineering (the levers, ranked)

1. **Part-count reduction** (Boothroyd-Dewhurst design-for-assembly, verified root): a part may exist only if it must move relative to others, must be a different material, or must be separable for service. Fewer parts = less labor, fewer fasteners, fewer failure interfaces, shorter BOM.
2. **Commodity/COTS over custom** — customs carry non-recurring engineering (NRE), single-source risk, and minimum-order exposure.
3. **Tolerance relaxation** — cost rises steeply below process-normal capability; specify the *loosest tolerance that meets function*, per the DFM seat's stack-up, not per habit.
4. **Material substitution** — the original value-engineering move.
5. **Design reuse** — reuse qualified circuits, enclosures, firmware, fixtures; reuse amortizes qualification.
6. **Volume leverage + second sourcing** — negotiate on annual volume; dual sources are price leverage *and* continuity insurance.
7. **NRE-vs-unit crossover (arithmetic):** custom pays when NRE ÷ unit-saving < risk-adjusted lifetime volume. $250k NRE saving $2/unit breaks even at 125k units; apply a risk haircut (slip, respin) before approving. Over a 3–5 year program life, long-payback customs rarely clear.

Pareto discipline: a few BOM lines carry most of the cost — attack the top lines first; a 30 % win on a $5 line is noise next to 3 % on the compute module.

---

## Part V — Collaboration principles (how eight seats and the `hw-program` conductor build one device)

- **Concurrent engineering** (IDA Report R-338, 1988, verified — the discipline's root): design the product and its manufacturing/support processes *together, from the outset*, considering "quality, cost, schedule, and user requirements" across the whole life cycle. In this team: DFM, cost, compliance, and reliability are in the loop from concept — not reviewers of a finished design.
- **Interface control:** every inter-seat boundary (dissipation handoff, antenna pad, telemetry contract, acceptance-test spec) is a drafted, versioned artifact with two named sides; changing it triggers notification of the other side. The `hw-program` skill (the main-session conductor role that inherited systems-integration's duties) owns the set.
- **Conway's law** (Conway 1968): the device's architecture will mirror the team's communication structure — which is why the cross-review matrix in TEAM.md exists: forced communication across every boundary that matters.
- **V-model** (Forsberg & Mooz 1991): every requirement decomposed on the way down is paired with the verification that will prove it on the way up — the PROVISIONAL-flag → bench-test pipeline is this program's V.
- **Reviews are gates, not briefings** — with cost status against target as an explicit exit criterion, at every gate.
- **Late changes cost an order of magnitude more per phase** (NASA/INCOSE 2004, empirically supported; exact 10× is mnemonic) — the economic justification for the whole gate discipline.

---

## Part VI — Maxims (attribution-graded, quote-safe)

Verbatim and verified:
- **Akin's Laws of Spacecraft Design** (David L. Akin, U. Maryland — primary page verified). Binding selections:
  - Law 1: "Engineering is done with numbers. Analysis without numbers is only an opinion."
  - Law 2: "To design a spacecraft right takes an infinite amount of effort. This is why it's a good idea to design them to operate when some things are wrong."
  - Law 3: "Design is an iterative process. The necessary number of iterations is one more than the number you have currently done."
  - Law 13: "Design is based on requirements. There's no justification for designing something one bit 'better' than the requirements dictate."
  - Law 14 (Edison's Law): "'Better' is the enemy of 'good'."
  - Law 35 (de Saint-Exupery's Law of Design): "A designer knows that they have achieved perfection not when there is nothing left to add, but when there is nothing left to take away."
- **"Perfect is the enemy of good"** — Voltaire, *Questions sur l'Encyclopédie* (1770), quoting an Italian proverb (verified).
- **Wellington's definition of engineering** — Arthur M. Wellington, 1887 (verified root of the "dime/dollar" folklore): engineering is "the art of doing that well with one dollar, which any bungler can do with two after a fashion" — and "rather the art of not constructing."

Attribution-caveated (do not quote as verified):
- "As simple as possible, but no simpler" — commonly attributed to Einstein; the aphorism is not found in his writings (his verified 1933 Oxford lecture says it in longer form). Say "attributed to."
- KISS principle — attributed to Kelly Johnson (Skunk Works), folkloric root; the substance (field-repairable by an average mechanic with basic tools) is the useful part.

---

## Part VII — How an agent uses this canon (binding)

1. **Every design argument reduces to Part II physics or it is an opinion** (Akin Law 1). Numbers, computed programmatically, with units.
2. **Every life claim reduces to a Part III mechanism and model**, evaluated at the P90 environment, stated as R% at the design life. MTBF alone is never a life claim.
3. **Every part answers the value question** (Part I §5) and every spec answers the derating question (Part III §4) — at the 3–5 year level, not the 20-year level.
4. **Every cost argument uses Part IV levers and the failure-cost arithmetic** (Part I §4) — cheap and expensive are both proven, never assumed.
5. **Every interface follows Part V** — drafted, versioned, two named sides.
6. **Flags are law:** `[UNVERIFIED]` items in this canon must be verified before they bear load in a deliverable. This document is itself subject to the operating standard — when a claim here is found wrong, fix the canon and note it in the decision register of the affected program.

## Source register (fetched primary/authoritative sources)

Physics/thermal: NIST CODATA (σ); Incropera h-ranges (via Michigan Tech table); NREL/ASTM G173 (1000 W/m²); MIL-STD-810H Method 505.7 (1120 W/m²); Engineering ToolBox (aluminum emissivity). Reliability: JEDEC dictionary (Arrhenius); TI SLAP177 (Ea = 0.7 eV convention); Nichicon aluminum capacitor technical note (10 °C rule + limits); XP Power (capacitor lifetime practice); Peck IRPS 1986 (humidity model, primary); Accendo Reliability (Norris-Landzberg parameters; product-lifetime definitions); Bel Fuse (MTBF math); PTC (Weibull); IntechOpen (series reliability); EverySpec (MIL-HDBK-217F status); Design News (217 obsolescence); Relyence (SR-332/VITA 51.1/IEC 61709); NASA EEE-INST-002 (NEPP PDF, capacitor derating); IPC-9592 (draft PDF, derating); MPS automotive-reliability PDF (mission profiles); ESA reliability handbook (average-vs-margin nuance); Astrodyne TDI (warranty vs life). Cost/collaboration: GAO PSAD-75-91 (design-to-cost root); U. Akron (target-costing history); Wikipedia/McGill (Miles/VE origin); DoDI 4245.14 (VE program); Tan/Otto/Wood ICED17 (early-decision cost evidence); Boothroyd-Dewhurst 1994 (DFA); IDA R-338 via DTIC (concurrent engineering); Conway 1968; Forsberg & Mooz 1991 (V-model); NASA NTRS 20100036670 (error-cost escalation); U. Maryland SSL (Akin's Laws, primary); Wikipedia (Voltaire attribution; Muntzing; KISS); todayinsci/libquotes (Wellington 1887).

Outstanding verification queue (flagged inline): JEP122 per-mechanism Ea table · EEE-INST-002 resistor/semiconductor sections · released IPC-9592B clause numbers · ECSS-Q-ST-30-11 · Telcordia GR-3108 outdoor classes · NAND P/E figures per selected part · SAC solder exponents · converter-loss error band.
