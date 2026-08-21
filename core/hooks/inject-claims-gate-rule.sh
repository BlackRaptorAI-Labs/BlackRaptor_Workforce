#!/bin/bash
# BlackRaptor Core — claims-gate pointer (Release 3 item 2, decision D-03). The claims gate moved to
# core so EVERY install is gated by construction (reliability required for a safety gate; conditional
# detection rejected — Cowork detection is unreliable and could silently miss). LEAN: this injects a
# ONE-SENTENCE pointer only; the full claims-gate rule loads on demand in the compliance-claims-gate
# skill and the claims-gate agent (token discipline — heavy content on-demand, not always-on).
# Agent-facing instruction; never shown verbatim to the user; adds NO user-facing strings.
cat <<'CTX'
{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"External-facing marketing copy must be reviewed by the isolated claims-gate agent before delivery — see the compliance-claims-gate skill for the full rule and proof standards."}}
CTX
