# BlackRaptor Workforce — Private Alpha

Welcome, and thank you for testing this.

**BlackRaptor Workforce** is a set of specialist agent packs with read-only review gates that block work until it meets the standard. You install it into Claude Code and get governed teams — engineering, an executive council, marketing, hardware — that draft and review work while you make the decisions.

This is a **private alpha**. That means a few real things:

- Parts of it will break, feel rough, or surprise you. That is expected.
- Your reports change the product — usually within days, not months.
- Nothing here is final: names, wording, behavior, and docs are all still moving.

You are one of a small number of invited testers. Please keep the repo and your access private during the alpha (see `docs/ALPHA-AGREEMENT.md` — one short page).

---

## 1. Install

1. **Accept the GitHub invitation** to the private `BlackRaptorAI/blackraptor` repo (you'll install using your own GitHub login).
2. In Claude Code, add the marketplace:
   ```
   /plugin marketplace add BlackRaptorAI/blackraptor
   ```
3. Install the **starter recipe** — most people begin here:
   ```
   /plugin install blackraptor-engineering@blackraptor
   /plugin install blackraptor-council@blackraptor
   ```
   `blackraptor-core` installs automatically with either team — you don't install it directly.

   Add these when they're relevant to what you're testing:
   ```
   /plugin install blackraptor-marketing@blackraptor    # when testing publishing/marketing flows
   /plugin install blackraptor-hardware@blackraptor      # if you design physical devices
   ```
4. **Verify** what you have:
   ```
   claude plugin list
   ```
   You should see the packs you installed, each `enabled`, plus `blackraptor-core`.

**If anything seems off, run `workforce-doctor` and paste its output into your defect report.** It's a read-only health check (packs present, versions consistent, the marketing hook wired for your client) — say "run workforce-doctor" in a session.

If anything in these four steps is confusing or fails — that itself is the most valuable thing to report (see §3, item 1).

### How to install, by situation

- **(a) Just you (user scope).** The two commands above (`marketplace add` + `plugin install`) install at the user level — they're available in every repo you open. CLI installs also show up in Cowork automatically; you don't install separately there.

- **(b) A whole team, standardized on one repo (the way to standardize a team on one repo).** Commit a `.claude/settings.json` to the shared repo so everyone who opens it gets the same packs. *(This mechanism is under test in the alpha — see the checklist below.)*
  ```json
  {
    "extraKnownMarketplaces": {
      "blackraptor": { "source": { "source": "github", "repo": "BlackRaptorAI/blackraptor" } }
    },
    "enabledPlugins": {
      "blackraptor-engineering@blackraptor": true,
      "blackraptor-council@blackraptor": true
    }
  }
  ```
  Each collaborator still needs read access to the private repo (they install under their own GitHub auth).

- **(c) Vendored into a repo's `.claude/` (no marketplace).** For a repo that should carry the agents directly, run the pack's `install.sh` — **available for the Engineering and Marketing packs only**:
  ```
  ./engineering/install.sh /path/to/your/repo
  ./marketing/install.sh   /path/to/your/repo
  ```
  Each appends one idempotent `@.claude/blackraptor-workforce.md` line to your `CLAUDE.md` (your existing content is preserved; both packs merge into that one file).

---

## 2. What to exercise hardest (in priority order)

Please spend your time roughly in this order. Items 1 and 2 are where we most need field truth.

1. **The fresh-install path itself.** You just did it. Report *any* friction, error message, or moment where you weren't sure what to do next — however small.
2. **Ad-hoc single-asset marketing gating** *(our top field question)*. With the marketing pack installed, ask for **one** marketing asset *outside* the campaign workflow — e.g. "draft a headline for X" or "write one LinkedIn post." Then tell us:
   - Did a claims-gate / compliance rule **surface** at all?
   - Was a **separate, isolated `claims-gate` agent dispatched** to review it, or did the session **review its own draft** inline?
   This distinction is exactly what we're trying to measure — please be precise about which happened.
3. **Gates blocking work.** Did any reviewer gate ever **block or flag** something you did? If so, was it **right** to? A gate that blocks correctly is the product working; a gate that blocks wrongly is a defect we need.
4. **A real task end-to-end with the Engineering pack** — something you'd actually do, start to finish.
5. **A Council session on a real business question** — convene the council on something you genuinely care about.
6. **Docs & README clarity** — anything unclear, missing, or wrong.

### Two specific checks we need confirmed

- **Project-scope `settings.json` install (§1b).** At least **two testers**, please commit the `.claude/settings.json` block above to the **private** `BlackRaptorAI/blackraptor`-based workflow and confirm collaborators actually get the packs on opening the repo. Report exactly what happened (worked / partial / failed, and any prompt or error).
- **Marketing hook in Cowork.** With the marketing pack installed, does the claims-gate hook **fire in a Cowork session** (not just the CLI)? Report **yes/no + the Cowork app version**.

---

## 3. How to report

Two structured forms (New Issue → pick the template) plus free-form issues are all fine:

- **Session report** — one per meaningful session. What you did, what fired, what felt wrong. This is the backbone of the alpha.
- **Defect** — file any time something breaks or behaves wrong. One per defect.

**Honest negativity is explicitly welcome.** "This wasted my time," "I didn't understand what it was doing," "I turned it off after five minutes" are all valid, useful reports. We would much rather hear it now than have you be polite.

---

## 4. What we collect (and don't)

Plain English:

- **What we collect:** only what **you type into the issue forms**, and any transcript excerpt **you choose** to paste in. That's it.
- **What we never collect:** nothing automatically. No telemetry, no usage tracking, no prompt or output content, no background phone-home. The code is in this repo — you can read every line.
- **What it's used for:** fixing defects and improving the packs, docs, and install experience.

You share a transcript only when you decide to; leaving it out never makes a report less welcome.

---

## 5. Weekly 30-minute call (optional, and the most useful thing you can give)

Once a week, optional, 30 minutes: you talk, we listen. It is by far the highest-signal feedback we get.

**Book here:** {{BOOKING_LINK}}

Entirely optional — skipping it never affects your access or standing in the alpha.

---

## 6. Support

- Open a **Defect** issue (fastest — it goes straight into the fix queue), or
- Email **tom.hanks@paragonenergy.ai**.

Thank you. You're shaping what this becomes.
