---
name: experimentation
description: >
  This skill should be used when the user asks to "run an A/B test", "design an experiment",
  "is this result significant", "test this landing page", "which variant won", or wants
  message testing, conversion experiments, or campaign lift measurement. It enforces
  trustworthy-experimentation discipline: pre-registered hypotheses, power analysis,
  validity checks, and honest interpretation.
metadata:
  version: "1.1.0"
---

# Experimentation & A/B Testing

## Purpose

Most A/B "wins" are noise read as signal. This skill encodes the discipline from Kohavi, Tang & Xu, *Trustworthy Online Controlled Experiments* (Cambridge University Press) — the standard reference — adapted for B2B traffic realities.

## Design (before anything runs)

1. **Pre-register**: hypothesis, single primary metric (an Overall Evaluation Criterion), guardrail metrics (things that must not degrade), minimum detectable effect (MDE), significance level (default α=0.05) and power (default 80%).
2. **Power analysis**: compute required sample size BEFORE launching. Use the script pattern:
   `python3 -c "from statsmodels.stats.power import NormalIndPower; from statsmodels.stats.proportion import proportion_effectsize; es=proportion_effectsize(0.05,0.06); print(NormalIndPower().solve_power(es, alpha=0.05, power=0.8, alternative='two-sided'))"`
   Report the run-time implication honestly: at X visitors/week, this test needs Y weeks. If Y is absurd, say so and switch methods (below).
3. **Unit of randomization**: visitor/account, consistent across the funnel; in B2B, randomize by ACCOUNT not by person to avoid contamination.
4. Run full weeks (day-of-week effects); no stopping early on a good-looking day.

## Validity checks (run on every test)

- **Sample Ratio Mismatch (SRM)**: if the observed split deviates from the planned ratio beyond chance (chi-square p < 0.001), the test is INVALID — diagnose before reading any result. Verified example from Kohavi's published work: a 176-vs-124 split on a nominal 50/50 design already carries p≈0.003 — a deviation that small can still be a disqualifying SRM. Microsoft reported SRM in roughly 6% of mature experiments; treat any SRM as a signal of a skewed population (bot traffic is a common cause) before trusting any headline metric.
- **No peeking**: repeatedly checking significance inflates false positives — verified math: with one decision metric the false-positive rate is ~5%, with two metrics checked it's ~10%, with three ~14%; checking daily over two weeks of continuous monitoring can push a nominal 5% error rate up toward ~17%. Either fix the sample size/horizon in advance, or use sequential/alpha-spending methods designed for continuous monitoring.
- **Twyman's Law**: any result that looks too good is most likely a bug or instrumentation error — investigate before celebrating.
- **Segment fishing**: post-hoc segment "wins" are hypothesis-generating only; they require a new confirmatory test (multiple-comparisons problem).
- **Novelty/primacy effects**: check whether the effect decays over the run.

## Low-traffic B2B alternatives (when classic A/B can't power)

State plainly when traffic can't support a test, then choose:

- **Bigger swings**: test radically different pages/offers (larger MDE = smaller sample needed).
- **Message testing via panel** (e.g., MaxDiff or forced-choice on target-titled respondents) instead of live-traffic testing.
- **Painted-door / smoke tests**: measure clicks on a not-yet-built offer — disclose honestly after click ("coming soon — join the list").
- **Sequential geographic or cohort rollouts** with pre/post comparison — label the causal weakness.
- **5-second tests / preference tests** for creative direction — directional only.

## Interpretation & reporting

Report: effect size with confidence interval (not just p-value), absolute and relative lift, guardrail status, validity checks passed, and the decision. A non-significant result is "we couldn't detect an effect of size X," never "no difference." Failed tests get reported as prominently as wins — a team that only reports wins is lying to itself.

## Integration

Experiment results feed the analytics-attribution-engineer's proof gate: a measured lift becomes an external claim ONLY after it clears the compliance-claims-gate with audited data.
