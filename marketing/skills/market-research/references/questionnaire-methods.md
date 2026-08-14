# Questionnaire & Interview Methods

Established, citable methodologies. Use these instead of first-pass instinct. Every method below traces to a published source a client can verify.

## 1. Survey design principles (Dillman's Tailored Design Method)

From Dillman, Smyth & Christian, *Internet, Phone, Mail, and Mixed-Mode Surveys: The Tailored Design Method* (Wiley):

- One construct per question; never double-barreled ("Is the product easy and affordable?" = two questions).
- Behavior over intent: ask what respondents DID ("In the last 12 months, did you…") before what they WOULD do — stated intent systematically overestimates action.
- Neutral wording; no leading frames; balanced scales (equal positive/negative options, labeled endpoints, 5 or 7 points).
- Question order matters: easy/engaging first, sensitive/demographic last; earlier questions prime later answers — randomize blocks where order could bias.
- Pre-test with 5–10 target respondents (cognitive interviewing: "what did you think that question was asking?") before fielding.
- Keep B2B instruments under ~10 minutes; completion quality degrades after that.

## 2. Sampling & bias controls

- Define the frame first: who exactly qualifies (screener questions with disqualifying logic, not self-ID alone).
- Name the biases in the report: selection bias (who saw the survey), non-response bias (who ignored it), survivorship (only current customers), social desirability (compliance topics especially).
- Minimum cells: don't report a segment cut below n≈30 without flagging it; directional only below that.
- Panels (Prolific, Respondent.io, Wynter for B2B messaging) vs. own-list vs. community intercepts — each has a known bias profile; state which was used and why.

## 3. Pricing research hierarchy (cheapest → most rigorous)

Use the cheapest method that can support the decision at stake:

1. **Direct WTP interview questions** — qualitative anchor only; people misreport WTP. Good for range discovery, never for setting price.
2. **Van Westendorp Price Sensitivity Meter** — the exact 4 questions (verified wording): "At what price would it be so cheap you'd question the product's quality?" (too cheap) / "At what price would you consider it a great value bargain?" (cheap) / "At what price does it start to feel expensive but still worth considering?" (expensive) / "At what price would it become too expensive to consider?" (too expensive). Strength: simple, no advanced methodology needed, easy to graph in a spreadsheet. Weakness: measures perception in isolation, not a real purchase choice; the acceptable-range intersection can be unstable with small samples; not built for bundled/multi-feature offers — use conjoint there instead.
3. **Gabor-Granger** — sequential purchase-intent at set price points; yields a demand curve for a FIXED offer. Good for testing specific candidate price points.
4. **MaxDiff** — forced trade-off ranking of features/messages; best-in-class for prioritizing what to include in a tier or which message resonates most. Not a pricing method per se but the standard for feature/message prioritization.
5. **Conjoint analysis (CBC)** — respondents choose between full product profiles (features × price); yields willingness-to-pay per attribute and simulated market share. The rigorous standard for packaging + pricing together. Needs larger samples (n≈200+ per segment) and specialist tooling (Sawtooth, Conjointly).

Rule: report which rung was used and what the next rung up would cost/add. Never present Van Westendorp output as if it were conjoint-grade evidence.

## 4. Interview methods

- **The Mom Test** (Fitzpatrick): talk about their life, not your idea; ask about specifics in the past, not opinions about the future; the product pitch invalidates the interview. No "would you use/pay for X?" — instead "what do you currently do/pay when Y happens?"
- **Jobs-to-be-Done / Outcome-Driven Innovation** (Christensen; Ulwick): interview for the job ("what were you trying to accomplish when you hired/fired the last solution?"), capture desired outcomes as measurable statements, then survey to score importance × satisfaction — the gap is the opportunity.
- **Switch interviews** (Moesta): reconstruct the timeline of an actual purchase/switch — first thought, passive looking, active looking, deciding — to find real buying triggers.
- Record, transcribe, code into patterns; quotes are evidence, one vivid quote is an anecdote.

## 5. Publishing & fielding workflow (honest capability statement)

Agents DESIGN instruments; publishing and fielding require tools and human action:

1. Draft instrument + screener + bias notes → human review.
2. Build in a forms/survey tool (Google Forms, Typeform, Tally, SurveyMonkey, or panel-native like Prolific/Conjointly) — the agent can produce the exact question-by-question build spec, and can build it directly if a forms MCP/browser tool is connected and the human approves.
3. Recruit: own list (CAN-SPAM rules apply — human approves the send), panel (budget required — state est. cost per complete), or community (each community's promo rules apply; founder-voice ask, mod permission where required).
4. Field, monitor completion quality (speeders, straight-liners flagged), close, analyze against the pre-registered analysis plan.

Never claim a survey was "published" unless the tool interaction actually happened and a human approved it.
