#!/bin/bash
# BlackRaptor Marketing — always-on claims-gate routing rule (A1).
# Delivered via a UserPromptSubmit hook (a real plugin surface that loads on the marketplace install
# path) because a plugin-root CLAUDE.md carrier does NOT load there (measured — SPEC §2 P11).
# EMPIRICAL LIMIT (SPEC §2 P11): this rule reliably reaches the session (flips P1), but it does NOT
# guarantee an *isolated* dispatch for a trivial single asset — the model tends to self-review. The
# GUARANTEED isolated gate is the marketing-campaign skill workflow. This rule is the best-effort
# always-on reminder for ad-hoc single assets.
cat <<'CTX'
{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"BlackRaptor Marketing standing rule — the CLAIMS GATE. Any external-facing marketing asset produced in this session (landing page, ad, email, blog post, headline, social post, video script, one-pager, or ANY published copy) must be reviewed by the separate `claims-gate` agent BEFORE it is delivered: dispatch `claims-gate` as its own subagent (via the Task tool) — it is an isolated reviewer that did NOT write the copy — and present the copy together with its per-claim verdict. Do NOT satisfy this by running the compliance-claims-gate SKILL yourself on copy this same context wrote; that is self-review, not a gate. If you are unable to dispatch the isolated `claims-gate` agent, say so explicitly and do NOT present the copy as gate-cleared. (For a full multi-asset campaign, the `marketing-campaign` skill makes this dispatch a mandatory step.)"}}
CTX
