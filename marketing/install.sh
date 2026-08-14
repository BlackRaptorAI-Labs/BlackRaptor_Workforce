#!/usr/bin/env bash
# Vendor the BlackRaptor Marketing Team into a repo's .claude/ directory.
# Usage: ./install.sh /path/to/target-repo
set -euo pipefail

TARGET="${1:?usage: ./install.sh /path/to/target-repo}"
SRC="$(cd "$(dirname "$0")/marketing" && pwd)"

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
if [ -f "$SRC/CLAUDE.md" ]; then
  if [ -f "$TARGET/CLAUDE.md" ]; then
    cp "$SRC/CLAUDE.md" "$TARGET/.claude/BlackRaptor-Marketing-CLAUDE.md"
    echo "note: $TARGET/CLAUDE.md exists — carrier saved to .claude/BlackRaptor-Marketing-CLAUDE.md; append it to your CLAUDE.md so the claims-gate rule + Core contract load."
  else
    sed 's|\${CLAUDE_PLUGIN_ROOT}/|.claude/|g' "$SRC/CLAUDE.md" > "$TARGET/CLAUDE.md"
    echo "note: installed the marketing carrier as $TARGET/CLAUDE.md (loads at workspace root)."
  fi
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

echo "Installed: 15 marketing agents + 9 marketing skills + 9 shared Core skills (18 total) into $TARGET/.claude/"
echo "Next: open the repo in Claude Code and say \"set up the marketing context\"."
