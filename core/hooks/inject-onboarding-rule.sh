#!/bin/bash
# BlackRaptor Core — welcome/onboarding trigger (R15). Delivered as a SessionStart hook (moved from
# UserPromptSubmit — a real plugin surface that fires once per session, not every
# turn, on the marketplace install path, unlike a plugin-root CLAUDE.md carrier — SPEC §2 P11). It
# backstops the in-skill R3/R7 triggers, which alone did not fire on greetings / team-shaped asks in
# Cowork (Release 2.1 live-test finding).
#
# SAFETY (R15.3): FILE CHECKS ONLY (plus the one marker write below) — no network. FAIL-OPEN — any
# error emits NOTHING and exits 0, so a broken hook can never block the session.  The injected text
# is an agent-facing INSTRUCTION (never shown verbatim to the user) and adds NO user-facing strings —
# W1 and the button labels live in the context-onboarding skill (Release-2 rev-5 Appendix A), unchanged.
#
# STATE (checked at the working project root): a context file counts as REAL only if it exists and
# its first line is NOT the template marker. Onboarded (real context + USER-PREFS.md) => inject
# nothing (silent, zero noise in steady state).
#
# PACK-CONTEXT MARKER: a user-scope install fires this hook in EVERY project the user ever
# opens, including ones this pack has nothing to do with. Before this fix a totally unrelated repo
# re-offered the fresh-project welcome every session, forever — there was no record that the offer
# had already been made and presumably not wanted. `.claude/.br-onboarding-offered` is written the
# first time the fresh-project branch fires in a given project directory; its presence silences that
# branch on every later session in the SAME directory. The other two branches (context or prefs
# present but not both — genuine in-progress setup) are unaffected and keep nudging normally.
#
# KILL SWITCH (2.3.0): BR_HOOKS=off turns this hook off with every other core hook (br-hooks-env.sh).
HERE="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
if [ -f "$HERE/br-hooks-env.sh" ]; then
  . "$HERE/br-hooks-env.sh"
  br_hook_disabled "" "onboarding SessionStart hook" "the first-run welcome will not be offered this session." && exit 0
fi
{
  MARKER='<!-- TEMPLATE — not onboarded -->'
  is_real() { [ -f "$1" ] || return 1; IFS= read -r first < "$1" 2>/dev/null || return 1; [ "$first" != "$MARKER" ]; }

  ctx=0
  for pat in BUSINESS-CONTEXT.md MARKETING-CONTEXT.md PROGRAM-CONTEXT-*.md; do
    for g in $pat; do is_real "$g" && ctx=1; done
  done
  prefs=0; [ -f USER-PREFS.md ] && prefs=1

  offered_marker=".claude/.br-onboarding-offered"

  instr=""
  if [ "$ctx" = 1 ] && [ "$prefs" = 1 ]; then
    instr=""   # ONBOARDED — inject nothing
  elif [ "$ctx" = 0 ] && [ "$prefs" = 0 ]; then
    if [ -f "$offered_marker" ]; then
      instr=""   # already offered once in this project and not taken up — stay silent forever
    else
      instr="BlackRaptor Workforce onboarding (R15): this looks like a fresh project — no filled context file and no USER-PREFS.md were found at the project root. On the user FIRST message this session, open the first-run welcome via the context-onboarding skill: greet with the W1 welcome and the Set up now / Later choice before other substantive work. Honor Later per R7.1 — if the user already chose Later in a PRIOR session in this project, do NOT re-open the flow; proceed and mark any business assumptions with the ASSUMED provenance label. If this is instead an existing engineering repo with substantial content, offer the R10 review-and-fill-gaps pass rather than the full welcome. This is guidance to you (the agents), not text to show the user verbatim."
      mkdir -p .claude 2>/dev/null && : > "$offered_marker" 2>/dev/null
    fi
  elif [ "$ctx" = 1 ] && [ "$prefs" = 0 ]; then
    instr="BlackRaptor Workforce onboarding (R15): a filled context file exists but USER-PREFS.md is missing. Before substantive work, offer the defaults-first settings round from the context-onboarding skill. Honor Later; do not re-open in the same session if declined. Guidance to you (the agents), not user-facing text."
  else
    instr="BlackRaptor Workforce onboarding (R15): USER-PREFS.md exists but no filled context file was found for the pack in use. Before substantive work, run the context interview via the context-onboarding skill (shared core block, then the installed pack extension), writing to the project root. Honor Later; do not re-open in the same session if declined. Guidance to you (the agents), not user-facing text."
  fi

  if [ -n "$instr" ]; then
    printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$instr"
  fi
} 2>/dev/null || true
exit 0
