#!/usr/bin/env bash
# development-team-agents installer — copies the kit into your repository.
# Usage: ./install.sh /path/to/your/repo
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${1:?Usage: ./install.sh /path/to/your/repo}"

[ -d "$DEST/.git" ] || { echo "ERROR: $DEST is not a git repo." >&2; exit 1; }

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$DEST/.development-team-agents-backup/$STAMP"

copy() { # src dest
  mkdir -p "$(dirname "$2")"
  if [ -e "$2" ] && ! cmp -s "$1" "$2"; then
    mkdir -p "$BACKUP/$(dirname "${2#"$DEST"/}")"
    cp "$2" "$BACKUP/${2#"$DEST"/}"
    echo "  backed up: ${2#"$DEST"/}"
  fi
  cp "$1" "$2"; echo "  installed: ${2#"$DEST"/}"
}

echo "[1/5] Agents -> .claude/agents/"
for f in "$SRC"/agents/*.md; do copy "$f" "$DEST/.claude/agents/$(basename "$f")"; done

echo "[2/5] Hook, settings, skill, commands -> .claude/"
copy "$SRC/claude/hooks/protect-tier3.py" "$DEST/.claude/hooks/protect-tier3.py"
chmod +x "$DEST/.claude/hooks/protect-tier3.py"
if [ -e "$DEST/.claude/settings.json" ]; then
  cp "$SRC/claude/settings.json" "$DEST/.claude/settings.json.development-team-agents"
  echo "  NOTE: .claude/settings.json exists — wrote settings.json.development-team-agents; merge the hooks block manually."
else
  copy "$SRC/claude/settings.json" "$DEST/.claude/settings.json"
fi
for d in "$SRC"/skills/*/; do
  name="$(basename "$d")"; [ -d "$d" ] || continue
  # copy the WHOLE skill dir (SKILL.md + references/ + scripts like validate_verdict.py),
  # not just SKILL.md — otherwise a skill's referenced files never install.
  mkdir -p "$DEST/.claude/skills/$name"
  cp -R "$d". "$DEST/.claude/skills/$name/"
  echo "  installed: .claude/skills/$name/ (full)"
done
for f in "$SRC"/commands/*.md; do copy "$f" "$DEST/.claude/commands/$(basename "$f")"; done

echo "[2b/5] Operating context -> .claude/blackraptor-workforce.md (+ CLAUDE.md @-import)"
# CLAUDE.md integration (@-import — MEASURED to load on client 2.1.170+, ALPHA-2). The pack's operating
# context lives at .claude/blackraptor-workforce.md as a MARKED SECTION so packs MERGE (engineering +
# marketing can both vendor into one repo); the existing CLAUDE.md gets exactly ONE idempotent @-import line.
if [ -f "$SRC/CLAUDE.md" ]; then
  WF="$DEST/.claude/blackraptor-workforce.md"; touch "$WF"
  if ! grep -qF "<!-- BEGIN blackraptor-engineering -->" "$WF"; then
    { echo "<!-- BEGIN blackraptor-engineering -->"; sed 's|\${CLAUDE_PLUGIN_ROOT}/|.claude/|g' "$SRC/CLAUDE.md"; echo "<!-- END blackraptor-engineering -->"; } >> "$WF"
  fi
  touch "$DEST/CLAUDE.md"
  grep -qF '@.claude/blackraptor-workforce.md' "$DEST/CLAUDE.md" || printf '\n@.claude/blackraptor-workforce.md\n' >> "$DEST/CLAUDE.md"
  echo "  operating context imported via @.claude/blackraptor-workforce.md in CLAUDE.md"
fi

echo "[3/5] CI workflow + PR template -> .github/"
copy "$SRC/github/change-record-required.yml" "$DEST/.github/workflows/change-record-required.yml"
copy "$SRC/github/pull_request_template.md" "$DEST/.github/pull_request_template.md"
echo "  NOTE: CODEOWNERS not auto-installed (create your second-approver code-owner team first)."
echo "        Template at: $SRC/github/CODEOWNERS.template"

echo "[4/5] Governance docs + eval convention -> docs/"
for f in change-record-template.md branch-protection-checklist.md gate-enforcement-map.md AGENT-RETROS.md agent-operating-standard.md; do
  copy "$SRC/docs/$f" "$DEST/docs/$f"
done
copy "$SRC/TEAM.md" "$DEST/docs/TEAM.md"   # the roster / gates / RACI charter the agents cite
copy "$SRC/docs/workflow-diagram.png" "$DEST/docs/workflow-diagram.png"
# CONTRIBUTING.md (the Tier 1/2/3 rules the agents cite) — don't clobber an existing one.
if [ -e "$DEST/CONTRIBUTING.md" ]; then
  copy "$SRC/CONTRIBUTING.md" "$DEST/CONTRIBUTING.md.development-team"
  echo "  NOTE: CONTRIBUTING.md exists — wrote CONTRIBUTING.md.development-team; merge the Tier-1/2/3 section."
else
  copy "$SRC/CONTRIBUTING.md" "$DEST/CONTRIBUTING.md"
fi
for f in "$SRC"/agent-evals/*.md; do
  [ -e "$f" ] && copy "$f" "$DEST/docs/agent-evals/$(basename "$f")"
done
mkdir -p "$DEST/docs/change-records"

echo "[5/5] Done. Next: work through CUSTOMIZATION.md (placeholders, Tier-3 paths,"
echo "roster trim, GitHub setup, hook test). Backups (if any): $BACKUP"
