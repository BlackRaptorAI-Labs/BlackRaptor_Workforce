#!/usr/bin/env bash
# Vendor the BlackRaptor Marketing Team into a repo's .claude/ directory.
# Usage: ./install.sh /path/to/target-repo
set -euo pipefail

TARGET="${1:?usage: ./install.sh /path/to/target-repo}"
SRC="$(cd "$(dirname "$0")" && pwd)"

[ -d "$TARGET" ] || { echo "target repo not found: $TARGET" >&2; exit 1; }

mkdir -p "$TARGET/.claude/agents" "$TARGET/.claude/skills" "$TARGET/.claude/context" "$TARGET/.claude/docs"

cp "$SRC"/agents/*.md "$TARGET/.claude/agents/"
cp -R "$SRC"/skills/* "$TARGET/.claude/skills/"
# The excellence-pass skill cites docs/agent-operating-standard.md — ship it so the
# reference resolves (the dev and HW kits already do).
cp "$SRC"/docs/*.md "$TARGET/.claude/docs/"

# Carry licensing with the vendored copy (Apache-2.0 §4).
cp "$SRC/LICENSE" "$TARGET/.claude/BlackRaptor-Marketing-LICENSE"
cp "$SRC/NOTICE"  "$TARGET/.claude/BlackRaptor-Marketing-NOTICE"

# A1: deliver what the marketplace path now uses. The always-on claims-gate rule lives on loaded
# surfaces: the compliance-claims-gate SKILL + producer descriptions (copied above with agents/skills)
# AND — for the marketplace path — a UserPromptSubmit hook (a plugin-only surface). A vendored install
# has no plugin hook registration, so carry the CLAUDE.md carrier to the workspace root, where a
# project CLAUDE.md DOES load, and ship the hook files for a maintainer who wires them into settings.
# CLAUDE.md integration (@-import — MEASURED to load on client 2.1.170+, ALPHA-2). The pack's operating
# context (Core contract + the always-on claims-gate rule) lives at .claude/blackraptor-workforce.md as a
# MARKED SECTION so packs MERGE (engineering + marketing can both vendor into one repo); the existing
# CLAUDE.md gets exactly ONE idempotent @-import line. Retires the legacy .claude/BlackRaptor-Marketing-CLAUDE.md.
if [ -f "$SRC/CLAUDE.md" ]; then
  WF="$TARGET/.claude/blackraptor-workforce.md"; touch "$WF"
  if ! grep -qF "<!-- BEGIN blackraptor-marketing -->" "$WF"; then
    { echo "<!-- BEGIN blackraptor-marketing -->"; sed 's|\${CLAUDE_PLUGIN_ROOT}/|.claude/|g' "$SRC/CLAUDE.md"; echo "<!-- END blackraptor-marketing -->"; } >> "$WF"
  fi
  touch "$TARGET/CLAUDE.md"
  grep -qF '@.claude/blackraptor-workforce.md' "$TARGET/CLAUDE.md" || printf '\n@.claude/blackraptor-workforce.md\n' >> "$TARGET/CLAUDE.md"
  echo "note: marketing operating context added to .claude/blackraptor-workforce.md and imported via @.claude/blackraptor-workforce.md in CLAUDE.md."
fi
if [ -d "$SRC/hooks" ]; then
  mkdir -p "$TARGET/.claude/hooks"; cp -R "$SRC"/hooks/. "$TARGET/.claude/hooks/"
  echo "note: hook scripts copied to .claude/hooks/ — register UserPromptSubmit → .claude/hooks/inject-claims-gate-rule.sh in your settings to get the always-on claims-gate rule on this vendored path."
fi

# Don't clobber an existing configured Marketing Intelligence Core.
if [ -f "$TARGET/.claude/context/marketing-context.md" ]; then
  echo "keeping existing marketing-context.md (template not copied)"
else
  cp "$SRC/context/marketing-context.md" "$TARGET/.claude/context/marketing-context.md"
fi

# Vendored installs have no ${CLAUDE_PLUGIN_ROOT}; point references at .claude/.
# Portable in-place rewrite: plain `sed` to a temp file (no `-i`), so it behaves
# identically on BSD/macOS and GNU/Linux (the old `sed -i ''` errored on GNU sed
# and left a half-installed repo under `set -e`).
find "$TARGET/.claude/agents" "$TARGET/.claude/skills" -name "*.md" -print0 |
  while IFS= read -r -d '' f; do
    sed 's|\${CLAUDE_PLUGIN_ROOT}/|.claude/|g' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
  done

echo "Installed: 15 marketing agents + 9 marketing skills + 10 shared Core skills (19 total) into $TARGET/.claude/"
echo "Next: open the repo in Claude Code and say \"set up the marketing context\"."
