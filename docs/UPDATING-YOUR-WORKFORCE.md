# Updating Your BlackRaptor Workforce

*BlackRaptor Workforce alpha — updating installed packs. Covers the alpha packs: Core,
Council, Hardware, Marketing. Last updated 2026-08-18.*

Claude turns automatic updates **off by default** for marketplaces that Anthropic doesn't run,
including ours — so unless you've switched auto-update on for the BlackRaptor marketplace,
updates won't reach you on their own. Either way, a new pack version won't appear in a
conversation that's already running. This page shows you how to update, on both surfaces.

## 2.0.0 — what changed, and what you must update

**2.0.0 is a breaking release across all five packs.** Nothing you have installed stops working,
but two things you may have written yourself will need updating.

**Gates are strict by design.** `CONCERNS` with a list of conditions is the common verdict on sound work — `PASS` is not the default and a `CONCERNS` is not a sign something is wrong with your change. Read the conditions, meet the ones that matter, and record the decision.

### 1. The gate verdict block changed shape

If you keep Change Records, the machine `verdict` blocks in them are now validated against a new
schema and **existing blocks will fail** until re-emitted. What changed:

| Field | Was | Is |
|---|---|---|
| `confidence` | `"high"` / `"medium"` / `"low"` | an **integer 0-10** |
| `standards` | did not exist | **required** — each entry gives the designation, edition, clause, how you reached the text, and the date you verified it; or the single literal `"none: practice applied: <x>"` |
| `evidence` | an array of strings | a **string** |
| `verdict` | included `N/A` | `N/A` **removed** — a gate that does not apply emits no block, and the Change Record row carries the N/A |

You do not need to rewrite old records unless CI re-validates them. New reviews produce the new
shape automatically. If you copied the Change Record template into your repo, take the updated one.

### 2. A new Stop hook validates gate verdicts in your session

Core now ships a `Stop` hook. When a turn dispatched a gate agent, the turn does not end until that
gate's verdict block validates. Before this, the validator only ever ran in a CI workflow you had to
install yourself — so on a marketplace install nothing checked the contract at all.

**If it gets in your way, turn it off:** set `BR_VERDICT_HOOK=off` in your environment. When
disabled, the hook writes one line to stderr. Interactive sessions show it; `claude -p` does not
surface hook stderr, so on that path check the `BR_VERDICT_HOOK` variable instead. It fails open on its own
errors and never blocks the same turn twice.

### 3. Two gate seats moved (Engineering pack)

A gate that can edit what it judges is not a gate, so two seats were split:

- **Schema sign-off** moved from `data-engineer` to the new read-only **`schema-reviewer`**.
- **Test/coverage sign-off** moved from `qa-test-engineer` to the new read-only **`test-auditor`**.

`data-engineer` and `qa-test-engineer` are unchanged as producers and keep their tools. **If you
dispatch gates by name, update those two call sites.** `seat-list.md` in the pack is already updated.

### 4. Some seats can now run their own arithmetic

The four hardware analysis seats and the four council numbers seats now hold `Bash` (the hardware
seats also hold `Write`, restricted to the program's `sim/` directory). Every figure they compute
carries its script and inputs and is **re-executed by a context that did not produce it** before it
is used. If your workflow assumed these seats were read-only, they are not any more — the write
target is charter-restricted, but the grant is real.

### 5. The retired-claims list moved (Marketing pack)

`claims-gate` no longer carries the banned-claims list in its body; it reads **§4b of your
`MARKETING-CONTEXT.md`**. If you maintain that file, add the §4a/§4b tables from the template — the
gate returns COULD NOT ASSESS for the retired-claims check if it cannot find the register, rather
than guessing.

## 2.1.0 — what changed, and what you must update

### 1. `product-marketing` moved from the Engineering pack to the Marketing pack

If you have an **engineering-only install** (no Marketing pack), you no longer have this agent.
Release notes, positioning, and regulated-claim review for shipped features now route to the
Marketing pack's `product-marketing` agent when that pack is installed alongside; otherwise the
main session drafts the comms itself and you gate them before anything ships. If you dispatch it by
name in a script or a Change Record template, install `blackraptor-marketing` or update the call
site to the guarded fallback.

### 2. The DRAFT/GATED file convention is now mechanical (Marketing pack)

Marketing asset producers (and `product-marketing`, `product-docs-writer`) write an asset as
`<name>.DRAFT.md`; it becomes `<name>.md` only once the isolated `claims-gate` agent has written a
validating `<name>.verdict.md` (PASS or CONCERNS, no BLOCK-graded claim). Two new controls enforce
it, both scoped to a directory your session has marked with a `.br-assets` file (written by the
`marketing-core` and `marketing-campaign` skills) — outside a marked directory neither one does
anything:

- A **PreToolUse hook** refuses an ungated `Write`/`Edit` of the final `.md` inside a marked
  directory. **Kill switch:** `BR_CLAIMS_HOOK=off`.
- The existing verdict `Stop` hook additionally blocks the turn if you wrote a `.DRAFT.md` under a
  marked directory and never dispatched `claims-gate` afterward in the same session. Same kill
  switch as before, `BR_VERDICT_HOOK=off`, covers this check too.

If either hook gets in your way on a non-marketing directory, that is a bug — this class of
false block is exactly what the scoping is designed to prevent, so please report it.

### 3. The verdict hook now waits for a subagent still running in the background

Claude Code (measured on `claude_code_version` 2.1.258) can run a subagent dispatch in the
background and hand you its result later as a notification, instead of always waiting for it
inline. The verdict `Stop` hook did not know about that second path: it looked only at the
dispatch's immediate tool result, so a gate seat that was still finishing in the background looked
to the hook like a seat that never produced a verdict at all. The hook now also reads a
backgrounded seat's completed notification, and if the seat has not finished yet when your turn is
about to end, it blocks with a plain reason — "gate seat still running; wait for its result before
ending the turn" — rather than treating an in-progress dispatch as a missing one. No schema change,
no new kill switch: `BR_VERDICT_HOOK=off` still turns this check off along with the rest of the
verdict hook.

---

## The one rule to remember

**A session keeps the pack versions it started with.** Updating doesn't retroactively change a
conversation already in progress — the same way a phone app finishes what it's doing and
applies its update on the next launch. On the command line you can pull changes into a running
session with `/reload-plugins`; in the Claude app, and any time you want certainty, just
**start a fresh session** after updating.

## Updating in the Claude app (Cowork)

1. Open the plugin settings (Settings → Plugins / Extensions).
2. Find the **blackraptor marketplace** entry and refresh/update it first. This re-reads the
   catalog. The per-pack **Update** buttons may stay grayed out until you do this step.
3. Update each BlackRaptor pack that shows an update: Core, Council, Hardware, Marketing.
4. **Start a new conversation.** The new session picks up the new versions; existing
   conversations keep the old ones.

## Updating on the command line (Claude Code)

Run these in order — the refresh must come first, or the update check can compare against a
stale catalog and report you are already current:

```bash
claude plugin marketplace update blackraptor
claude plugin update blackraptor-core@blackraptor
claude plugin update blackraptor-council@blackraptor
claude plugin update blackraptor-hardware@blackraptor
claude plugin update blackraptor-marketing@blackraptor
```

Then either run `/reload-plugins` in your session or — for certainty — restart it (exit and
start `claude` again).

If you installed a pack at **project scope** (tied to one repository), update it from inside
that project folder and add `--scope project` to the update command.

## How to check what you're running (about 10 seconds)

In a **fresh** session, say:

> run workforce-doctor

The doctor reports each installed pack and its version — compare those against the latest
release's `CHANGELOG.md` (shipped inside each pack) or the release announcement to see if
you're current. In a Cowork session it also reports the timestamp of the
session's pack snapshot, so you can see how old your session's copy is. If the doctor ever
reports **STALE SNAPSHOT — CANNOT CERTIFY**, that means packs were added or removed after your
session started — start a fresh session and run it again.

## Troubleshooting

- **The Update button is gray.** Refresh the *marketplace* entry first (step 2 above), then
  check the pack again. If the marketplace refresh itself fails or the buttons stay gray,
  remove and re-add the blackraptor marketplace. **Note: removing a marketplace also
  uninstalls the packs you installed from it** — after re-adding it, reinstall Core, Council,
  Hardware, and Marketing, then start a fresh session.
- **The command line says "already at latest" but you know there's a release.** Usually the
  marketplace refresh was skipped — run `claude plugin marketplace update blackraptor` and try
  again. If the refresh reports a failure, remove and re-add the marketplace — remember this
  uninstalls your packs, so reinstall them afterward.
- **An open conversation is acting like the old version.** It is — sessions keep their startup
  versions. Start a fresh conversation (or use `/reload-plugins` on the command line).
- **The doctor says STALE SNAPSHOT.** Working as intended: packs were added or removed after
  your session started. Start a fresh session.

## What's in each release

Each pack ships a `CHANGELOG.md` describing what changed. Every release bumps the pack
version — **we treat any content change as requiring a version bump**, so the version number
is your reliable signal of what you're running. If you ever suspect a pack changed without a
version bump, tell us: that's a defect on our side and we want to hear about it.
