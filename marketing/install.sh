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

# --- R3 vendoring (D-02 BUNDLING, version-aware): merge the shared blackraptor-core into the flat
# .claude/ so this vendored install is SELF-CONTAINED (no marketplace). Core is read at install time
# from the sibling core/ dir ($SRC/../core) — the single source, NOT a duplicate shipped in this pack
# (the "core-skill edit never touches a team pack" criterion holds; bundling happens on the user's
# machine). Version-aware: copy core only if absent or OLDER; never downgrade a newer core; identical =
# no-op (safe for multi-pack vendoring into one .claude/ and for re-runs). The ${CLAUDE_PLUGIN_ROOT}
# rewrite below covers the bundled core .md files too (they land before it runs).
CORE="$SRC/../core"
if [ -d "$CORE" ]; then
  CORE_VER=$(grep -m1 '"version"' "$CORE/.claude-plugin/plugin.json" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
  MARK="$TARGET/.claude/.blackraptor-core-version"
  HAVE=$([ -f "$MARK" ] && cat "$MARK" || echo "")
  if [ -z "$HAVE" ] || { [ "$HAVE" != "$CORE_VER" ] && [ "$(printf '%s\n%s\n' "$HAVE" "$CORE_VER" | sort -V | tail -1)" = "$CORE_VER" ]; }; then
    cp "$CORE"/agents/*.md "$TARGET/.claude/agents/" 2>/dev/null || true
    cp -R "$CORE"/skills/* "$TARGET/.claude/skills/"
    mkdir -p "$TARGET/.claude/hooks"; [ -d "$CORE/hooks" ] && { cp -R "$CORE"/hooks/. "$TARGET/.claude/hooks/"; chmod +x "$TARGET/.claude/hooks/"*.sh 2>/dev/null || true; }
    [ -d "$CORE/docs" ] && cp "$CORE"/docs/*.md "$TARGET/.claude/docs/" 2>/dev/null || true
    printf '%s\n' "$CORE_VER" > "$MARK"
    # Wire the two core UserPromptSubmit hooks into project settings so they FIRE on this vendored path
    # (no plugin hook registration here). Safe JSON merge via python3; idempotent.
    python3 - "$TARGET/.claude/settings.json" <<'PY'
import json, os, sys
p = sys.argv[1]; d = {}
if os.path.exists(p):
    try: d = json.load(open(p))
    except Exception:
        print("  NOTE: .claude/settings.json is not parseable JSON — skipped auto-wiring the core hooks;"
              " add UserPromptSubmit -> .claude/hooks/inject-onboarding-rule.sh + inject-claims-gate-rule.sh manually.")
        sys.exit(0)
h = d.setdefault("hooks", {}).setdefault("UserPromptSubmit", [])
for s in ("inject-onboarding-rule.sh", "inject-claims-gate-rule.sh"):
    c = ".claude/hooks/" + s
    if not any(c in json.dumps(e) for e in h):
        h.append({"hooks": [{"type": "command", "command": c}]})
json.dump(d, open(p, "w"), indent=2)
PY
    echo "note: bundled blackraptor-core $CORE_VER into .claude/ (was: ${HAVE:-absent}); core hooks wired into .claude/settings.json"
  else
    echo "note: kept existing blackraptor-core $HAVE (>= $CORE_VER being installed; never downgraded)"
  fi
fi

# Vendored installs have no ${CLAUDE_PLUGIN_ROOT}; point references at .claude/.
# Portable in-place rewrite: plain `sed` to a temp file (no `-i`), so it behaves
# identically on BSD/macOS and GNU/Linux (the old `sed -i ''` errored on GNU sed
# and left a half-installed repo under `set -e`).
find "$TARGET/.claude/agents" "$TARGET/.claude/skills" -name "*.md" -print0 |
  while IFS= read -r -d '' f; do
    sed 's|\${CLAUDE_PLUGIN_ROOT}/|.claude/|g' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
  done

echo "Installed: 11 marketing agents + 7 marketing skills + the bundled blackraptor-core (agents + skills + hooks) into $TARGET/.claude/ — self-contained."
echo "Next: open the repo in Claude Code and say \"set up the marketing context\"."
