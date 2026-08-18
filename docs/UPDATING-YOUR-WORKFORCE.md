# Updating Your BlackRaptor Workforce

*BlackRaptor Workforce alpha — updating installed packs. Covers the alpha packs: Core,
Council, Hardware, Marketing. Last updated 2026-08-18.*

Claude turns automatic updates **off by default** for marketplaces that Anthropic doesn't run,
including ours — so unless you've switched auto-update on for the BlackRaptor marketplace,
updates won't reach you on their own. Either way, a new pack version won't appear in a
conversation that's already running. This page shows you how to update, on both surfaces.

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
