# Porting the Council to Other Platforms

The Council's agent files are plain markdown, but it is only *faithful* on a
runtime that gives **each seat its own separated context** — on Claude Code that's
the sub-agent mechanism (the main-session `council` skill spawns each seat as its
own sub-agent; no agent holds the `Agent` tool — in subagent context the
`Agent`/Task tools are stripped, so orchestration stays in the human's main
session). It runs wherever that exists: **Claude Code today**, and **Cowork only where
Cowork runs plugin sub-agents** (install the `blackraptor-council` plugin — see
the marketplace install steps in the top-level `README.md`). **It must never be
flattened into a single chat prompt** —
one context playing ten roles ships a degraded council wearing the name, and we
don't do that. So "does it run in Cowork?" reduces to "does this Cowork session
support plugin sub-agents?"; if not, use it in Claude Code.

## What a faithful port MUST preserve

1. **Separated contexts.** Each seat runs as its own agent with its own
   context. One context window playing ten roles is not a council.
2. **Independent parallel drafts.** Seats answer without seeing each
   other's drafts. Independence before synthesis prevents anchoring.
3. **Anonymized cross-review** on consequential questions: drafts
   circulate with seat identity stripped.
4. **The challenge protocol.** The convener (the main-session `council` skill
   on Claude Code; the equivalent orchestrator node on other platforms)
   interrogates every draft (evidence, confidence, counter-case,
   falsifiability, customer, cost) and returns deficient work — before synthesis.
5. **Human-in-the-loop gates.** growth-engine's spend/claims approvals
   and ethics-governance's BLOCK verdicts must reach a human and halt
   until answered. If your runtime can't pause for a human, don't port
   the executor seat.
6. **The output contract** (`COUNCIL.md` §3), including "What You Lose"
   and confidence labels.
7. **Grounding.** Load `BUSINESS-CONTEXT.md` into every seat's context;
   refuse to run without it.

## How the pieces map

| This package | OpenAI Agents SDK | CrewAI | LangGraph |
|---|---|---|---|
| Agent .md body (below frontmatter) | Agent `instructions` | Agent role/goal/backstory + system prompt | Node system prompt |
| Frontmatter `tools` | Hosted/function tools (read-only + web search for advisors) | Tools list | Tool bindings |
| Frontmatter `model` tiering | Per-agent model choice | Per-agent LLM | Per-node model |
| the `council` skill (convener; runs in the main session) | Orchestrator agent + handoffs | Hierarchical process manager | Supervisor node + conditional edges |
| Independent drafts | Parallel runs, no shared thread | Async tasks, no context sharing | Parallel branches, merged after |
| HITL gates | Human approval tool / interrupt | Human-in-the-loop task | `interrupt()` before the gated node |

## Porting steps

1. Strip the YAML frontmatter from each agent file; the body is the
   system prompt (it is platform-agnostic by design).
2. Recreate the tool policy: advisors get read-only + web research;
   only growth-engine gets write/draft tools, behind a human gate.
3. Implement the convener's flow (the `council` skill on Claude Code; an
   orchestrator/supervisor node on other platforms): ground → select seats →
   context packets → parallel drafts → challenge protocol → (anonymized review)
   → synthesis → decision-ready view.
4. Keep model tiering: strongest model for the convener (the `council` skill /
   orchestrator node), finance, ethics-governance, fundraising-ir.
5. Test with a real question and check the output contract survived:
   steelman both ways, confidence labels, What You Lose, dissent
   register.

## What NOT to build

- A single-prompt "act as my board of advisors" version. One context
  cannot keep advisors honestly independent — the seats converge and the
  challenge protocol becomes self-review theater.
- A version where the orchestrator auto-decides. The human decides;
  that's load-bearing.
- A growth-engine that can spend or publish without a human approval
  step.

Share working ports back via GitHub (see CONTRIBUTING.md). Keep the
NOTICE attribution with every port.
