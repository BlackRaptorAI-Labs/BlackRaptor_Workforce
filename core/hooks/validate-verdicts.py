#!/usr/bin/env python3
"""Stop-hook helper: validate every gate verdict emitted this turn, AND (the 2.1.0 claims-gate change) catch a
DRAFT written under a marketing-asset directory with no later claims-gate dispatch in the session.

Invoked by validate-verdicts.sh with the path to validate_verdict.py as argv[1] and the Stop-hook
payload on stdin. Prints a `{"decision":"block", ...}` object when either check fails, and nothing
at all otherwise.

FAIL CLOSED (D-267, D-268). This hook guards a gate, so an error on its path never ends a turn quietly. An error
that is not handled where it happens reaches the one guard in main(), which prints a block: "the verdict check crashed
(<ExceptionType> at <function>): this turn is not gated; report it". The block is bounded like every other: the first
MAX_STOP_BLOCKS Stops of a turn block, then a "Verdict check FAILED" systemMessage puts the failure on record, so a
broken hook can neither pass a turn silently nor loop. A Stop call whose payload cannot be read, or that names no
transcript, or whose transcript cannot be read, blocks the same way. Only a call that is not a Stop hook at all stays
silent: empty stdin, a payload with no sign of a Stop event, and the snapshot recorder's own work (a snapshot error is a
systemMessage; the Stop check then falls back to counting files it cannot compare as changed). The owner's way out
is the announced kill switch (BR_VERDICT_HOOK=off or BR_HOOKS=off), never a silent error. Informational hooks
(session contract, onboarding, upgrade notice) stay fail-open; they cannot affect a PASS.
DEADLINE (D-278): the hook arms an alarm at HOOK_BUDGET_S (870 s of hooks.json's 900; 12 s of 20 for a snapshot call). Reaching it
blocks: "the verdict check ran out of time (<step>): this turn is not gated; report it", bounded like the crash block. The shell wrapper
kills the helper a few seconds later if it cannot answer at all.
SKIPS ARE SAID (D-279): a check that has to skip itself (the disk check on a large tree with no git) adds a systemMessage naming what is
not checked, every time.
It blocks when (a) it successfully read a gate's output and neither the gate's
inline text nor a verdict file it wrote validates, (b) it saw a `*.DRAFT.md` written under a
`.br-assets`-marked directory with no `claims-gate` dispatch anywhere after it in the same
transcript, or (c) any error, crash or missing input on the path of either check (D-267). The second check is what makes the DRAFT/GATED convention (`compliance-claims-gate`
skill) mechanical rather than checklist-only, extending this hook rather than adding a second
Stop hook (the 2.1.0 claims-gate change §3(c)) — scoped to marked directories only, so an engineering or council
session sees zero blocks from it.

CHECK 1 LOOKS IN TWO PLACES (D-57, GO-BLOCK-P2-BUILD-v1-AMENDMENT-5 §1). Some gate names — most
notably `ethics-governance` — serve two roles: a standalone artifact gate that returns an inline
fenced ```verdict block, and a council seat (COUNCIL.md §3a) that instead writes
`council/<slug>.verdict.md` and returns prose. The same agent name cannot be told apart by name
alone, so for every dispatch of a GATES member Check 1 looks, in order: (a) an inline fenced
```verdict block in the subagent's own returned text; failing that, (b) a `council/<slug>.verdict.md`
write in the transcript (any GATES member may be dispatched as a seat); failing that and only for
`claims-gate`, (c) a `<name>.verdict.md` write beside a `<name>.DRAFT.md` write. All file content is
read from the transcript's own `Write` tool-call input, never from disk, so a stale file on disk
cannot satisfy it. No exemption exists for a council context and seats get no second inline block —
if none of (a)/(b)/(c) validates, the turn blocks naming the gate and every location checked.

A DISPATCH'S "RETURNED TEXT" IS NOT ALWAYS ITS `tool_result` (D-65, GO-BLOCK-P2-BUILD-v1-AMENDMENT-8
§1). When this was measured (client 2.1.258; our own measurement, not a documented guarantee), Claude Code launched every Agent/Task dispatch in the background unless the call sets
`run_in_background: false`; a backgrounded dispatch's `tool_result` is a fixed async-launch stub
("Async agent launched successfully ...") and the gate's real text arrives later as a `system` event,
`subtype: "task_notification"`, carrying the same `tool_use_id`. So for (a) above, the text tried is,
in order: (i) a `task_notification` event matching the dispatch's `tool_use_id`, its `summary` field,
or — if `summary` is absent or empty and `output_file` exists — the last assistant text in that file;
(ii) otherwise the `tool_result`, as before. A `tool_result` that is the async-launch stub is never
treated as returned text. If a dispatch has a stub result and no completed notification yet, the turn
BLOCKS with "<slug>: gate seat still running; wait for its result before ending the turn" rather than
falling through to (b)/(c) or silently permitting — a still-running gate is not the same as one whose
text simply failed to validate.

THE TRANSCRIPT FILE STORES THE NOTICE IN TWO OTHER SHAPES (D-164, 2.8.2, measured on client transcripts).
The `system`/`task_notification` event appears in the stream output, not in the transcript file this hook
reads. The file holds the notice as text, `<task-notification>` with `<tool-use-id>`, `<status>`,
`<result>` (the seat's returned text) and `<output-file>`: (1) when it lands inside the dispatching
turn, an `attachment` of type `queued_command` (commandMode `task-notification`); (2) when it lands
after that turn ended, a `user` event with `origin.kind` `task-notification`. Reading only the system
event made every backgrounded seat look "still running" after it had returned. Both shapes are read
now, `<result>` first. Shape (2) is not a human message (the client marks it "NOT USER INPUT"), so it
does not start a turn: the seats it reports are checked in the turn where their notice lands.

A MEASURED VERDICT MUST POINT AT A REAL RUN (D-146, 2.7.0). For every verdict block that validates, if
its `evidence` opens with MEASURED, at least one backticked span in it must match the `command` of a
Bash `tool_use` anywhere in this SESSION: the main transcript (every turn so far, not only this one) and
every `subagents/agent-*.jsonl` beside it. Whole session, because a test gate cites the run another
gate made, in an earlier turn or a sibling subagent. Match (D-179, 2.8.2): the span is split into
simple commands (on ; && || | and newlines, redirections such as `2>&1` dropped), and EVERY simple
command in the span must carry exactly the tokens of a simple command that Bash call ran: its first
token and every argument token, nothing missing and nothing added. The span must also be at least 8
characters after whitespace collapse. So a one-letter span, or a span that pads a real `ls` with an
unrun `python3 -m pytest`, does not match. No match blocks with "MEASURED command not executed in this
session". A non-zero exit is counted, never blocked: a mutation run is supposed to go red.

A VERDICT FILE A BASH COMMAND TOUCHED IS UNVERIFIED (D-175, 2.8.2). Check 1c reads a verdict file's
content from the Write call that made it. Any Bash `tool_use` in the turn (main session or a dispatched
subagent) whose command names a `*.verdict.md` marks that file unverified: with no Write or Edit of it
this turn it is reported exactly as "verdict file not produced by a gate dispatch this turn"; with one,
its content is read back from disk, since the shell may have changed it. A `$name` in a longer path (a
shell loop) is matched as `*` against the files on disk. A name that is only a placeholder
(`<slug>.verdict.md`, `{slug}.verdict.md`, `$slug.verdict.md`) or a bare `.verdict.md` is text about
verdict files, not a file, and is skipped (D-215, 2.8.3); a file a shell writes is still caught on disk. Read verdict files with the Read tool, not
`cat`; running the validator on a file you wrote with Write is fine (the file is read back and checked).
Checks 1b and 1c read a backgrounded dispatch's returned text from its stored notice, as check 1 does.

FILES ARE CHECKED ON DISK, NOT ONLY IN THE COMMAND TEXT (D-190, 2.8.2). A name built at run time
(`'sec.verdict'+'.md'`, `${F}ict.md`, `$(printf verdict)`) or an archive extract writes a verdict file no
text match sees. So the same script also runs as a snapshot hook: at turn start (UserPromptSubmit) and after
every Bash result (PostToolUse, matcher Bash) it records every `*.verdict.md` (any case) and every plain
`.md` under a `.br-assets`-marked folder (relative path and sha256; `.git`, `node_modules` and virtualenvs
skipped) in a file beside the transcript. At Stop, a file that appeared or changed since turn start with
no Write or Edit of it in the turn is "not produced by a gate dispatch" (a verdict file) or a DRAFT/GATED
promotion (a marked `.md`), and the turn blocks naming it. With no turn-start snapshot (an upgrade
mid-session, a test harness), the baseline is the files git reports clean plus the files older than the
turn's first user message. The command-text match stays as the early check.

A QUALITY PASS IS CHECKED BY THIS HOOK'S OWN TEST RUN (D-222, 2.8.3; replaces the output reading of D-216). Text
an agent writes cannot prove what it ran (audit 5 K1: `pytest ; echo '99 passed'`). When the turn holds a PASS from
test-auditor or completion-auditor, the hook runs the project's test command itself: `test_cmd` in
.claude/workforce-installed.json (recorded by /workforce-init), from the repo root, with NO_COLOR=1, FORCE_COLOR=0,
CI=1, under `test_timeout` seconds (default 300, at most 600; the whole hook has 870 of hooks.json's 900 seconds, D-278). For a known runner
it adds the runner's machine report (pytest --junitxml, jest/vitest JSON, go test -json, node --test junit, mocha
JSON, bun junit, dotnet trx, maven surefire) written to a folder this hook owns under the plugin data folder; a
command with no machine report is refused before it runs (D-234, below). The PASS counts only if the run exits 0
and shows at least 1 passed and 0 failed or
errored; the gate's printed output is never read for it. One run per input state per session, cached under the
plugin data folder (D-236, below). On macOS the run is wrapped in sandbox-exec so a test
cannot write the enforcement files. Messages: "no test command recorded; run /workforce-init", "test run exceeded
N s; raise test_timeout or split the suite", "the hook's test run did not pass (exit N, P passed, F failed)",
"the hook's test run printed no test summary and wrote no report". When the recorded runner names test paths, at
least one must reach the change (D-218): a changed file, its folder, or a file importing a changed module directly
or through one package `__init__.py` / `index.ts` / `index.js` re-export (D-226). The change is `git diff HEAD`
plus untracked files, or, on a clean tree, the branch against origin/HEAD, the upstream merge base, or
main/master/trunk/develop (D-226). A test file counts as changed only when the change adds a test case to it, so
touching or renaming the cited test is not "the change" (D-227). Without git the check is skipped and the clean
line says so. A non-quality gate's MEASURED evidence keeps the session-match rule above, which shows a command
ran, not what it proved; there a path may differ only in form (absolute or repo-relative, a leading `./`, the
last two segments) and a `<name>` placeholder stands for one token, and a span that matches nothing names the
nearest command that ran (D-225).

THE HOOK'S RUN IS NOT THE PROOF, CI IS (D-233 to D-238, 2.8.3, Amendment 6). The tests the hook runs are code the
agent can write, and so are the files that steer the runner (audit 6 M1: a conftest.py that rewrites the report,
an `addopts` that deselects the failing tests, a wrapper script that prints "3 passed"). So: RUNNER_CONTROL lists
those inputs, and before the run can carry a PASS they must equal what a person accepted, the runner_config of
this repo's tamper baseline (plugin mode, written by /workforce-init at install, --upgrade and
--accept-runner-config) or the merge base with the base branch (copy mode, weaker) (D-233); a test command with
no machine report cannot carry a PASS at all, and `npm/pnpm/yarn test` counts only when the package.json test
script is one known runner command (D-234); a forge written in a test file still passes, a known limit with a
fixture, and CI=1 stays in the run's env because CI is the reference (D-235); the cache key adds the test
command, its timeout, the runner config and every git-ignored file's path, size and mtime (none cached past
2,000), while files outside the repo stay out of it (D-236). A completion-auditor dispatch whose prompt opens
with LADDER_MARK runs the check ladder and owes no verdict, and none it returns counts (D-237). A MEASURED span
may shorten a path with a leading `…/` or `.../`, use `<name>` for one path segment, and name a script by its
basename when the run reached it through a shell variable (D-238).

THE ENVIRONMENT THE RUN LOADS (D-243 to D-249, 2.8.3, Amendment 7). Audit 7 P1: a `.pth` and a plugin placed in the
repo's `.venv` (which the walk skips) forged a PASS through an in-repo interpreter. So the startup files of every
in-repo environment join the runner config: each site-packages' *.pth, sitecustomize.py, usercustomize.py and
[pytest11] entry points, each node_modules' install state, and files a jest/vitest/mocha config names inside
node_modules; and setup.py and the pytest11 entry-point tables (D-243). Anything else the run loads can still fake
a pass, a known limit with a fixture (D-244). A repo with no accepted runner config is recorded by the hook itself
once, with a warning, when the sandbox protects the install record or the baseline already has an entry for the
path (D-245). `uv run`/`poetry run` and the like are read through, and test_cmd may be a list whose every entry
must pass (D-246). A MEASURED path needs one literal folder; basename alone only through a variable (D-248). A
cached run serves only later Stops of the same turn, for 10 minutes (D-249). (D-247 is the installer's.)

CI IS THE JUDGE (D-250 to D-257, 2.8.3, Amendment 8). After the local run passes, a quality PASS stands only on the
engineering pack's workforce-proof workflow for the exact HEAD: its head-suite and base-suite check runs (app
github-actions, the run's own check suite, the workflow file matching the recorded hash) concluded success. Still
running, unpushed, a dirty tree, or gh missing, offline or signed out: INCOMPLETE, not a block; a failed job: block.
No GitHub remote: INCOMPLETE; `ci_judge: false` (--no-ci-judge) keeps the local judge and says it can be faked.
`--ci-status` prints what the doctor reports. See ci_judge() and the measured facts it rests on.

FAIL CLOSED, OWNER APPROVAL (D-258 to D-266, 2.8.3, Amendment 9). Audit 8V V1: an error inside the quality-PASS
check, the tamper check and a dozen helpers left the PASS standing. Every judging path now records the error in FAULTS
and main() blocks on it ("<check> could not run (<Type>): this gate is not passed"); the sites that cannot touch a
verdict say why where they catch (D-259). The first Workforce pull request and a base with no tests end INCOMPLETE for
the owner's review (D-261); every workforce-proof run for the commit must be complete (D-262); `--ci-status` reads the
approval settings with an admin login (D-260, D-263). Workforce uses no code-owners file: the owner approves every
pull request (D-258).

ENFORCEMENT FILES ARE COMPARED WITH A PROTECTED BASELINE (D-231, 2.8.3). In plugin mode /workforce-init records
the sha256 of every file in .claude/hooks, every sandbox denyWrite file and the hooks block of
.claude/settings.json in tamper-baseline.json under the core plugin's data folder (CLAUDE_PLUGIN_DATA, inside
~/.claude/plugins/, which the sandbox keeps every agent's shell out of). Every Stop compares, after any test run,
and a difference blocks: "enforcement file changed this session: <file>; run /workforce-init --upgrade to restore,
or --accept-changes if you made it". A repo with no baseline (copy mode, an older install) is not checked.

A GATE IS JUDGED ON ITS LATEST RETURN (D-208, 2.8.3). A gate whose block failed is often resumed with
SendMessage and asked to correct it. The SendMessage `tool_result` is only "Resuming agent ..." (its
`toolUseResult.resumedAgentId` names the agent); the corrected text arrives as a task notice whose
`<tool-use-id>` is the SendMessage call's id. Each gate agent (by agentId) is judged on its latest
return in the turn that carries a ```verdict block: the dispatch's own return, then each resume's, in
transcript order. A later valid return clears an earlier invalid one; a later invalid return still
blocks; a resume with no return yet is "still running". A return is judged whole, as before: every
block in it must validate. A gate dispatched in an earlier turn and resumed in this one is judged here.
When a gate has more than one return, the clean-turn line names the earlier ones ("<slug>: latest of N
returns; earlier: FAIL, FAIL"; D-214, 2.8.3), so a verdict a resume replaced stays on record. The note covers
returns from earlier turns of the session, and an earlier block that failed validation reads "invalid" (D-219).

EVERY STOP IS JUDGED (D-209, 2.8.3; replaces the loop guard of D-164). A Stop that arrives with
`stop_hook_active` (the turn is continuing because this hook blocked) is judged like any other, so a
"fixed" re-emit is checked. While problems remain the hook blocks again, at most 3 times per turn (the
count is kept in the `.br-snapshot.json` beside the transcript, keyed by session and turn). On the 4th
Stop with problems it does not block: it prints the problems as a `systemMessage` that begins "Verdict
check FAILED and was not fixed:", so the failure is on record. When the only problem is a gate still
running, the line reads "Verdict check INCOMPLETE: <gate> still running at turn end" instead (D-220). Claude Code's own cut-off after 8
consecutive blocks stays a backstop.

COMMANDS ARE SPLIT ON NEWLINES (D-210, 2.8.3). A multi-line Bash command is several simple commands: a
newline separates them (a backslash-newline joins two lines), before any matching. A heredoc body is text, not
a command that ran, unless the heredoc feeds sh, bash, zsh, python or node (D-217).
"""

from __future__ import print_function

import glob
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback

# D-192 (2.8.2, audit 3 G9): the gate roster is read from verdict-schema.json (`gates`, beside the validator),
# the one list verify.sh, this hook and validate_verdict.py share. `council_seats` may also sign a verdict
# block (the council skill validates them); a project adds gates in .claude/gates-allow.txt. Filled in main().
GATES, SEATS = set(), set()
ROSTER_FAULT = [None]      # D-259: the schema could not be read; a turn that dispatched an agent is then not gated

# D-259 (Amendment 9, U1): FAIL CLOSED. A helper on a judging path that hits an error records it here instead of
# quietly falling back; main() turns every entry into a blocking problem line, so an error can never leave a PASS
# standing or skip a block. Sites that cannot affect a verdict (a cache, a temp folder, a line that is not JSON) say
# so where they catch. An error that nothing here catches reaches the guard in main() (D-268), which blocks.
FAULTS = []


def fault(check, exc):
    msg = "%s could not run (%s): this gate is not passed" % (check, type(exc).__name__)
    if msg not in FAULTS:
        FAULTS.append(msg)


# D-278 (Amendment 11, Z1): THIS HOOK DECIDES BEFORE THE CLIENT'S TIMEOUT. Claude Code cancels a hook that outlives its timeout and
# lets the turn end, silently (audit 10V, measured on client 2.1.296). hooks.json gives the Stop call 900 s and the snapshot calls
# (UserPromptSubmit, PostToolUse) 20 s, so the hook arms its own alarm below both. Reaching it blocks (Stop) or says so (snapshot);
# the shell wrapper's watchdog (validate-verdicts.sh, 885 s and 17 s) is the backup if this process cannot answer at all.
# BR_HOOK_BUDGET_S can only LOWER the budget (the fixtures and the scratch live proof use it).
HOOK_BUDGET_S = 870
SNAPSHOT_BUDGET_S = 12
_BUDGET = {"deadline": None, "step": "the verdict check"}


class BudgetExceeded(BaseException):
    """The hook's own deadline. A BaseException, so no `except Exception` on a judging path can swallow it; only main() catches it."""


def step(name):
    _BUDGET["step"] = name


def time_left():
    d = _BUDGET["deadline"]
    return 1e9 if d is None else d - time.time()


def _on_alarm(_signum, _frame):
    raise BudgetExceeded(_BUDGET["step"])


def _arm_budget(snapshot):
    cap = SNAPSHOT_BUDGET_S if snapshot else HOOK_BUDGET_S
    try:
        env = float(os.environ.get("BR_HOOK_BUDGET_S") or 0)
    except ValueError:   # D-286 (b): an unreadable BR_HOOK_BUDGET_S is ignored; the shipped budget applies
        env = 0
    b = min(cap, env) if env > 0 else cap
    _BUDGET["deadline"] = time.time() + b
    _BUDGET["step"] = "the verdict check"
    try:
        signal.signal(signal.SIGALRM, _on_alarm)
        signal.setitimer(signal.ITIMER_REAL, b)
    except (AttributeError, ValueError, OSError):   # D-278: no SIGALRM here (not Unix, or not the main thread): the wrapper's watchdog is the only deadline
        pass


def _disarm_budget():
    _BUDGET["deadline"] = None
    try:
        signal.setitimer(signal.ITIMER_REAL, 0)
    except (AttributeError, ValueError, OSError):   # D-278: nothing was armed
        pass


def load_roster(validator, project_dir):
    """(gates, seats, allowed) from the schema beside the validator and the project's allow file."""
    try:
        sch = json.load(open(os.path.join(os.path.dirname(validator), "verdict-schema.json"), encoding="utf-8"))
        gates, seats = set(sch.get("gates") or []), set(sch.get("council_seats") or [])
    except Exception as exc:   # D-270 (closed): ROSTER_FAULT; a turn that dispatched an agent is not gated
        gates, seats = set(), set()
        ROSTER_FAULT[0] = "the gate roster (verdict-schema.json) could not be read (%s): this turn's gates are not passed" % type(exc).__name__
    allowed = set()
    try:
        allowed = {l.strip() for l in open(os.path.join(project_dir, ".claude", "gates-allow.txt"), encoding="utf-8")
                   if l.strip() and not l.startswith("#")}
    except FileNotFoundError:   # D-270 (normal): no project gate list; only the shipped roster
        pass                   # no project gate list: only the shipped roster
    except Exception as exc:   # D-270: a gate list that exists and cannot be read could hide a project gate
        fault("the project gate list (.claude/gates-allow.txt)", exc)
    return gates | allowed, seats

# The fixed prefix of a backgrounded Agent/Task dispatch's async-launch tool_result (D-65). Never
# treated as a gate's returned text, whether or not a task_notification has arrived yet.
STUB_PREFIX = "Async agent launched"

# Gates whose PASS rests on a run (validate_verdict.py QUALITY_GATES): a CITED PASS from one names the
# command the completion audit ran, and that command must have run in this session (D-201).
QUALITY_GATES = frozenset(("test-auditor", "completion-auditor"))   # a subset, not the roster (D-192)
LADDER_MARK = "MODE: ladder-only (no verdict)"   # D-237: honoured on a completion-auditor dispatch only


def ladder_only(slug, inp):
    """True for a completion-auditor dispatch whose prompt opens with LADDER_MARK: it runs the check ladder and owes
    no verdict, and any verdict block it returns is ignored (D-237)."""
    if slug != "completion-auditor" or not isinstance(inp, dict):
        return False
    first = next((ln.strip() for ln in str(inp.get("prompt") or "").splitlines() if ln.strip()), "")
    return first == LADDER_MARK

# The validator's own fence rule (validate_verdict.py FENCE), used here only to read each block's
# `agent` for the author check (D-112, R22). Validity is still judged by the validator itself.
FENCE = re.compile(r"^[ \t]*```verdict[ \t]*\n(.*?)\n[ \t]*```", re.S | re.M)

# D-270: an unreadable transcript line of this turn that looks like a dispatch or a result of one.
CALL_LINE = re.compile(r'tool_use|tool_result|toolUseResult|task_notification|subagent_type')

# A *.verdict.md path named in a Bash command (D-175).
VERDICT_REF = re.compile(r"[^\s'\"<>|;&()=`]*\.verdict\.md(?![\w.-])")   # a $name or ${name} in it is globbed as *; the name ends at .md, not .md.bak or .mdx (D-280)

# Check 3 match (D-179): simple commands, redirections dropped, compared token for token.
REDIRECT = re.compile(r"(?<!\S)[0-9]*(?:&>>?|>>?&?|<)\s*[^\s;|&<>]+")
CMD_SEP = {";", "&&", "||", "|", "&", "|&"}


def _simple_commands(text):
    """[(token, ...)] for each simple command in a shell text, redirections dropped (D-179)."""
    text = REDIRECT.sub(" ", text.replace("\n", " ; "))
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=";&|")
        lex.whitespace_split = True
        toks = list(lex)
    except ValueError:   # D-286 (b): a command that will not tokenise is split on spaces; the MEASURED check counts non-zero exits and never blocks on them, so this cannot hide a failure
        toks = text.split()
    out, cur = [], []
    for t in toks + [";"]:
        if t in CMD_SEP:
            if cur:
                out.append(tuple(cur))
            cur = []
        elif t not in ("(", ")", "{", "}"):
            cur.append(t)
    return out


PH_TOKEN = "__BR_PLACEHOLDER__"
PH_SPAN = re.compile(r"(?<!\S)<[A-Za-z][\w.-]*>(?!\S)")
PH_SEG = re.compile(r"<[A-Za-z][\w.-]*>")          # D-238: a placeholder inside a token stands for one path segment
SEG_TOKEN = "__BR_SEG__"
PATH_WILD = re.compile(r"^(?:\u2026|\.\.\.)/")       # D-238: a leading `…/` or `.../` stands for any path prefix
SCRIPT_RUNNERS = {"sh", "bash", "zsh", "dash", "node", "deno", "bun", "ruby", "perl", "tsx", "ts-node"}


def _cite(span):
    """The simple commands of a cited span, whole-token placeholders as PH_TOKEN and in-token ones as SEG_TOKEN."""
    return _simple_commands(PH_SEG.sub(SEG_TOKEN, PH_SPAN.sub(PH_TOKEN, span)))


NEVER = re.compile(r"(?!)")


def _path_pattern(c):
    """A cited token with `…/` in front or a placeholder segment, as a regex an executed token must match (D-238).
    D-248: the cited directory must be there, so at least one directory segment is literal; `…/probe.py` or
    `<dir>/check.py` names a basename only and matches nothing (a run through a shell variable is _cmd_eq's case)."""
    wild = PATH_WILD.match(c)
    if not wild and SEG_TOKEN not in c:
        return None
    rest = c[wild.end():] if wild else c
    if not any(p and SEG_TOKEN not in p for p in rest.split("/")[:-1]):
        return NEVER
    body = "/".join(re.escape(part).replace(re.escape(SEG_TOKEN), "[^/]+") for part in rest.split("/"))
    return re.compile(("(?:.*/)?" if wild else "") + body + r"\Z")


def _tok_eq(c, r, project_dir=None):
    """A cited token equals an executed one when they differ only in path form (D-225): a leading `./`, absolute vs
    repo-relative, or the cited path shortened to the executed path's last two segments. A `<name>` placeholder in
    the span stands for any one token, or inside a path for one segment, and a leading `…/` for any prefix (D-238)."""
    if c == r or c == PH_TOKEN:
        return True
    pat = _path_pattern(c)
    if pat is not None:
        rn = r[2:] if r.startswith("./") else r
        return bool(pat.match(rn) or pat.match(r))
    if "/" not in c or "/" not in r:
        return False
    cn, rn = (c[2:] if c.startswith("./") else c), (r[2:] if r.startswith("./") else r)
    if cn == rn:
        return True
    if os.path.isabs(cn) == os.path.isabs(rn):
        return False
    rel, ab = (cn, rn) if os.path.isabs(rn) else (rn, cn)
    if project_dir and os.path.normpath(os.path.join(project_dir, rel)) == os.path.normpath(ab):
        return True
    return os.path.isabs(rn) and rel.count("/") == 1 and "/".join(ab.rstrip("/").split("/")[-2:]) == rel


def _script_index(t):
    """The index of the script a `bash x.sh`, `python3 -I x.py` or `node x.js` command runs, else None (D-238)."""
    if not t:
        return None
    head = os.path.basename(t[0])
    if not (head in SCRIPT_RUNNERS or PYTHONS.match(head)):
        return None
    for i in range(1, len(t)):
        if t[i] in ("-m", "-c", "-e", "-W", "-X", "--eval", "-p"):
            return None
        if not t[i].startswith("-"):
            return i
    return None


def _cmd_eq(c, r, project_dir=None):
    """Token for token (D-179, D-225). The script a cited interpreter command runs matches by basename only when the
    run named it through a shell variable or substitution the hook cannot expand (D-238, D-248): `bash
    …/scratchpad/mutants.sh <dir>` is `bash $S/mutants.sh $S`. Never another runner or basename; a literal path must
    match the cited one, directory included."""
    if len(c) != len(r):
        return False
    si = _script_index(c)
    for i, (x, y) in enumerate(zip(c, r)):
        if _tok_eq(x, y, project_dir):
            continue
        if i == si and i == _script_index(r) and i > 0 and ("$" in y or "`" in y) and _tok_eq(c[0], r[0], project_dir):
            bx, by = x.rstrip("/").split("/")[-1], y.rstrip("/").split("/")[-1]
            if bx and bx == by and SEG_TOKEN not in bx and PH_TOKEN not in bx:
                continue
        return False
    return True


def span_matches(span, cmd, project_dir=None):
    """True when every simple command in a MEASURED span is, token for token, a simple command that the
    executed Bash command ran (D-179), tokens compared by meaning (D-225, D-238). The 8-character floor applies only
    when the span is not itself one executed simple command token for token (D-195): `go test` or `pytest`, run and
    cited exactly, matches."""
    ran = _simple_commands(cmd)
    cited = _cite(span)
    if not cited or not all(any(_cmd_eq(c, r, project_dir) for r in ran) for c in cited):
        return False
    return len(cited) == 1 or len(" ".join(span.split())) >= 8


def nearest_command(span, cmds, project_dir=None):
    """The executed simple command closest to a span that matched none (D-225): most tokens equal in place, then the
    same first token. For the block message, so the gate can copy the command it ran."""
    cited = _cite(span)
    best, score = None, 0
    for cmd in cmds:
        for r in _simple_commands(cmd):
            for c in cited:
                sc = sum(1 for x, y in zip(c, r) if _tok_eq(x, y, project_dir)) + (2 if c[:1] == r[:1] else 0)
                if sc > score:
                    best, score = r, sc
    return " ".join(best) if best and score >= 3 else None


HEREDOC = re.compile(r"<<(-)?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
HEREDOC_RUNS = {"sh", "bash", "zsh", "python", "python3", "node"}   # a heredoc fed to these runs its body (D-217)


def _strip_heredoc_bodies(cmd):
    """The command with each heredoc body removed, unless the heredoc feeds a shell or interpreter (D-217): the
    body of `cat > run.sh <<'EOF'` is text written to a file, not a command that ran."""
    out, waiting = [], []      # waiting: [(word, keep_body, dash)] for the heredocs opened on earlier lines
    for line in cmd.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if waiting:
            word, keep, dash = waiting[0]
            if (line.lstrip("\t") if dash else line).strip() == word:
                waiting.pop(0)
                continue
            if keep:
                out.append(line)
            continue
        out.append(line)
        for m in HEREDOC.finditer(line):
            seg = re.split(r"[;&|()]", line[:m.start()])[-1].split()
            while seg and ENV_ASSIGN.match(seg[0]):
                seg.pop(0)
            head = os.path.basename(seg[0]) if seg else ""
            keep = head in HEREDOC_RUNS or re.fullmatch(r"python3(\.\d+)?", head) is not None
            waiting.append((m.group(3), keep, bool(m.group(1))))
    return "\n".join(out)


def _flat(cmd):
    """A Bash command as one line for matching: heredoc bodies that do not run dropped (D-217), backslash-newlines
    joined and newlines turned into command separators (D-210)."""
    return " ".join(_strip_heredoc_bodies(cmd).replace("\\\n", " ").replace("\n", " ; ").split())


# D-216: a quality gate's PASS rests on a passing test result this turn, read from what the run printed.
ENV_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
PYTHONS = re.compile(r"^(python|python3|python3\.\d+|py)$")
ONE_WORD_RUNNERS = {"pytest", "jest", "vitest", "mocha"}
TWO_WORD_RUNNERS = {("go", "test"), ("cargo", "test"), ("dotnet", "test"), ("mvn", "test"), ("./mvnw", "test"),
                    ("gradle", "test"), ("./gradlew", "test"), ("bun", "test"), ("node", "--test"), ("deno", "test"),
                    ("npx", "jest"), ("npx", "vitest"), ("npx", "mocha"), ("npx", "pytest")}
SCRIPT_HEADS = {"make", "just", "task", "tox", "nox"}
ENV_RUNNERS = {"uv", "poetry", "pipenv", "hatch", "pdm", "rye"}   # D-246: `uv run pytest` runs pytest


def _canon(tokens):
    """(runner, args) for a simple command: VAR=value words and an `env` prefix dropped, `python`/`python3`/`py -3`
    read as one interpreter, `npm run test` read as `npm test`. The runner is a tuple; args keep their order."""
    t = list(tokens)
    if t and t[0] == "env":
        t.pop(0)
    while t and ENV_ASSIGN.match(t[0]):
        t.pop(0)
    if len(t) > 2 and os.path.basename(t[0]) in ENV_RUNNERS and t[1] == "run":
        t = t[2:]                                # D-246: the wrapper's own flags go too; a flag with a value does not
        while t and t[0].startswith("-") and t[0] != "--":     # parse, so the command stays unknown (fails closed)
            t.pop(0)
        if t[:1] == ["--"]:
            t.pop(0)
    if not t:
        return (), []
    if "/" in t[0] and not t[0].startswith("./"):
        t[0] = os.path.basename(t[0])          # `/usr/bin/python3 -m pytest` is `python -m pytest` (D-222)
    if PYTHONS.match(t[0]):
        rest = t[1:]
        if t[0] == "py" and rest[:1] == ["-3"]:
            rest = rest[1:]
        if rest[:1] == ["-m"] and len(rest) > 1:
            return ("python", "-m", rest[1]), rest[2:]
        return ("python",), rest
    if t[0] in ("npm", "pnpm", "yarn"):
        if t[1:3] == ["run", "test"]:
            return (t[0], "test"), t[3:]
        if t[1:2] in (["test"], ["t"]):
            return (t[0], "test"), t[2:]
    if tuple(t[:2]) in TWO_WORD_RUNNERS:
        return tuple(t[:2]), t[2:]
    return (t[0],), t[1:]


def _is_known_runner(runner):
    return (runner in TWO_WORD_RUNNERS or (len(runner) == 1 and runner[0] in ONE_WORD_RUNNERS)
            or runner == ("python", "-m", "pytest") or (len(runner) == 2 and runner[1] == "test"
                                                         and runner[0] in ("npm", "pnpm", "yarn")))


# Summary readers (D-216): each returns (passed, failed) for the runner lines it finds in a run's output, or None.
# Since D-222 they read only the hook's own test run; since D-234 a command with no machine report is refused before
# it runs, so no PASS rests on them (read_report keeps them as its fallback).
ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07]*\x07")   # colour and other escape codes (D-224)
_PYTEST_WORDS = r"(?:passed|failed|errors?|skipped|xfailed|xpassed|deselected|warnings?|reruns?)"
_PYTEST_LINE = re.compile(r"^(?:=+\s*)?((?:\d+ " + _PYTEST_WORDS + r",? ?)+)(?: in [\d.]+s\b.*?)?(?:\s*=+)?\s*$")


def _read_pytest(text):
    lines = [l.strip() for l in text.splitlines()]
    hits = [l for l in lines if _PYTEST_LINE.match(l) or re.match(r"^=*\s*no tests ran\b", l)]
    if not hits:
        return None
    last = hits[-1]
    n = lambda w: sum(int(x) for x in re.findall(r"(\d+) " + w + r"\b", last))
    return n("passed"), n("failed") + n("errors?")


def _read_go(text):
    ok = [l for l in text.splitlines() if re.match(r"^ok\s+\S+", l)]
    fail = [l for l in text.splitlines() if re.match(r"^(--- FAIL:|FAIL\b)", l)]
    passes = [l for l in text.splitlines() if re.match(r"^\s*--- PASS:", l)]
    if not (ok or fail or passes):
        return None
    return len([l for l in ok if "[no tests to run]" not in l]) + len(passes), len(fail)


def _read_regex(pattern, passed_g, failed_gs, last=False):
    rx = re.compile(pattern, re.M)

    def read(text):
        ms = list(rx.finditer(text))
        if not ms:
            return None
        ms = ms[-1:] if last else ms
        val = lambda m, g: int(m.group(g)) if g in m.groupdict() and m.group(g) else 0
        return (sum(val(m, passed_g) for m in ms), sum(val(m, g) for m in ms for g in failed_gs))
    return read


def _read_jest(text):
    ms = re.findall(r"^\s*Tests:\s+(.*\d+ total)", text, re.M)
    if not ms:
        return None
    n = lambda w: sum(int(x) for x in re.findall(r"(\d+) " + w + r"\b", ms[-1]))
    return n("passed"), n("failed")


def _read_vitest(text):
    ms = re.findall(r"^\s*Tests\s+(.*)\(\d+\)\s*$", text, re.M)
    if not ms:
        return None
    n = lambda w: sum(int(x) for x in re.findall(r"(\d+) " + w + r"\b", ms[-1]))
    return n("passed"), n("failed")


def _read_maven(text):
    ms = re.findall(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+)(?:, Skipped: (\d+))?", text)
    if not ms:
        return None
    run, fl, er, sk = (int(x or 0) for x in ms[-1])
    return run - fl - er - sk, fl + er


SUMMARY_READERS = [
    ("pytest", _read_pytest), ("go test", _read_go), ("jest", _read_jest), ("vitest", _read_vitest),
    ("node --test", _read_regex(r"^# pass (?P<passed>\d+)\s*$|^# fail (?P<failed>\d+)\s*$", "passed", ["failed"])),
    ("node --test spec", _read_regex(r"^\u2139 pass (?P<passed>\d+)\s*$|^\u2139 fail (?P<failed>\d+)\s*$", "passed", ["failed"])),
    ("mocha", _read_regex(r"^\s*(?P<passed>\d+) passing\b|^\s*(?P<failed>\d+) failing\b", "passed", ["failed"])),
    ("bun test", _read_regex(r"^\s*(?P<passed>\d+) pass\s*$|^\s*(?P<failed>\d+) fail\s*$", "passed", ["failed"])),
    ("cargo test", _read_regex(r"^test result: \w+\. (?P<passed>\d+) passed; (?P<failed>\d+) failed", "passed", ["failed"])),
    ("dotnet test", _read_regex(r"(?:Passed|Failed)!\s*-\s*Failed:\s*(?P<failed>\d+),\s*Passed:\s*(?P<passed>\d+)", "passed", ["failed"])),
    ("maven/surefire", _read_maven),
]


def project_summary_readers(project_dir):
    """Readers a project adds in .claude/test-summary-patterns.txt: one regex per line with named groups `passed`
    and `failed` (a Tier-3 file; D-216)."""
    out = []
    try:
        lines = open(os.path.join(project_dir, ".claude", "test-summary-patterns.txt"), encoding="utf-8").read().splitlines()
    except OSError:   # D-270 (closed): no project readers, so an unrecognised run summary blocks as 'printed no test summary'
        return out
    for l in lines:
        if l.strip() and not l.lstrip().startswith("#"):
            try:
                re.compile(l)
            except re.error:   # D-270 (closed): an invalid reader pattern reads nothing, so an unrecognised run summary blocks
                continue
            if "(?P<passed>" in l:
                out.append(("project: " + l[:40], _read_regex(l, "passed", ["failed"])))
    return out


def run_is_green(output, is_error, readers=()):
    """(green, passed, failed) for a test run's result (D-216): not is_error, and the runner summary lines in its
    output show at least 1 passed and 0 failed or errored. No summary found: (False, None, None)."""
    found, passed, failed = False, 0, 0
    output = ANSI.sub("", output or "").replace("\r\n", "\n")   # D-224: a coloured summary reads like a plain one
    for _name, read in list(SUMMARY_READERS) + list(readers):
        r = read(output)
        if r is not None:
            found = True
            passed += r[0]
            failed += r[1]
    if not found:
        return False, None, None
    return (not is_error and passed >= 1 and failed == 0), passed, failed


# D-222 (Amendment 4, K1): a quality PASS is checked by this hook's OWN run of the project's test command. What a gate
# printed is never read for it: the run's exit code and the runner's machine report (written to a folder this hook
# owns, outside the repo) decide. One run per tree state per session (cached under the plugin data folder).
INSTALLED_REC = os.path.join(".claude", "workforce-installed.json")
TEST_TIMEOUT_DEFAULT, TEST_TIMEOUT_MAX = 300, 600      # D-278: the whole hook has HOOK_BUDGET_S (870 s) of hooks.json's 900 s; the test run gets at most 600 of it
CACHE_SKIP = {".ruff_cache", "htmlcov", ".coverage"}


def install_record(project_dir):
    try:
        rec = json.load(open(os.path.join(project_dir, INSTALLED_REC), encoding="utf-8"))
        return rec if isinstance(rec, dict) else {}
    except Exception:  # D-259 (closed): an empty record has no test command, which blocks a quality PASS
        return {}


def repo_top(project_dir):
    try:
        p = subprocess.run(["git", "-C", project_dir, "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=10)
        if p.returncode == 0 and p.stdout.strip():
            return os.path.realpath(p.stdout.strip())
    except Exception as exc:   # D-259 (closed): a fault: paths keyed by the root would be wrong
        fault("the repo root lookup (git rev-parse)", exc)    # D-259: paths keyed by the root would be wrong
    return os.path.realpath(project_dir)


def plugin_data_dir():
    """The core plugin's data folder (CLAUDE_PLUGIN_DATA, under ~/.claude/plugins/, which the sandbox keeps every agent
    out of), or the same path derived from CLAUDE_PLUGIN_ROOT (<config>/plugins/cache/<market>/<plugin>/<version>).
    None outside plugin mode."""
    d = os.environ.get("CLAUDE_PLUGIN_DATA")
    if d:
        return d
    m = re.match(r"^(.*)/plugins/cache/([^/]+)/([^/]+)/[^/]+/?$", os.path.realpath(os.environ.get("CLAUDE_PLUGIN_ROOT") or "/-"))
    if m:
        return os.path.join(m.group(1), "plugins", "data", re.sub(r"[^A-Za-z0-9_.-]", "-", "%s-%s" % (m.group(3), m.group(2))))
    return None


def tree_state(root):
    """sha256 over every tracked and untracked (not ignored) file's path and content; None when it cannot be read."""
    try:
        p = subprocess.run(["git", "-C", root, "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                           capture_output=True, timeout=30)
        names = sorted(set(x.decode("utf-8", "replace") for x in p.stdout.split(b"\0") if x)) if p.returncode == 0 else None
    except Exception:          # D-259 (b): only a cache key; the walk below gives one too, never a verdict
        names = None
    if names is None:
        names = []
        for dp, dn, fn in os.walk(root):
            dn[:] = [x for x in dn if x not in SNAP_SKIP and x not in CACHE_SKIP]
            names += [os.path.relpath(os.path.join(dp, f), root) for f in fn]
            if len(names) > SNAP_LIMIT:
                return None
        names.sort()
    h = hashlib.sha256()
    for rel in names:
        parts = rel.split("/")
        if any(x in SNAP_SKIP or x in CACHE_SKIP for x in parts) or rel.endswith(".pyc"):
            continue
        h.update(rel.encode("utf-8", "replace") + b"\0")
        try:
            with open(os.path.join(root, rel), "rb") as fh:
                h.update(hashlib.sha256(fh.read()).digest())
        except OSError:   # D-270 (closed): an unreadable file hashes as 'missing', which changes the cache key and re-runs the tests
            h.update(b"missing")
    return h.hexdigest()


def _pkg_test_script(root):
    try:
        return str((json.load(open(os.path.join(root, "package.json"), encoding="utf-8")).get("scripts") or {}).get("test") or "")
    except Exception:          # D-259 (closed): no script means no machine report, which blocks the PASS
        return ""


# D-233 (Amendment 6, N1): the inputs that steer the test runner. They are ordinary repo files an agent can write, and
# the hook's own run executes them, so before a quality PASS can stand on that run they must match what a person last
# accepted: the protected baseline (plugin mode) or the base branch (copy mode). workforce_init.py holds the same
# list and the same reading (runner_control_hashes); keep the two in step.
RUNNER_CONTROL = {
    "names": ("conftest.py", "pytest.ini", ".pytest.ini", "pytest.toml", ".pytest.toml", "sitecustomize.py",
              "usercustomize.py", "setup.py"),                                       # at any depth
    "suffixes": (".pth",),                                               # at any depth
    "prefixes": ("jest.config.", "vitest.config.", "vitest.workspace.", "vite.config.", ".mocharc", "karma.conf.",
                 "playwright.config."),                                  # at any depth
    "sections": {"pyproject.toml": "tool.pytest", "setup.cfg": "tool:pytest", "tox.ini": "pytest"},   # that part only
    "package.json": ("scripts: test*, pretest*, posttest*", "jest", "mocha", "ava", "vitest"),         # those keys only
    "test_cmd": "every repo file named as an argument in test_cmd (test files aside)",
}
RC_WALK_LIMIT = 200000          # files walked before the check gives up (it then blocks, never passes)
RC_SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".tox", ".mypy_cache"}


def _rc_section(text, want):
    """The lines of the INI/TOML sections a runner reads (pyproject: `[tool]` and `[tool.pytest*]`, plus top-level
    dotted keys naming pytest); "" when there are none."""
    out, keep, top = [], False, True
    for line in text.splitlines():
        st = line.strip()
        m = re.match(r"^\[\[?\s*([^\]]+?)\s*\]\]?\s*(#.*)?$", st)
        if m:
            top = False
            name = re.sub(r"[\s\"']", "", m.group(1))
            keep = (name == want if want != "tool.pytest" else (name == "tool" or name == want or name.startswith(want + ".")))
        elif top and want == "tool.pytest" and "pytest" in st:
            keep = True
        if keep and st:
            out.append(line.rstrip())
        if top:
            keep = False
    return "\n".join(out)


def _rc_package(raw):
    try:
        d = json.loads(raw.decode("utf-8", "replace"))
    except ValueError:   # D-270 (closed): an unreadable package.json is hashed whole
        return raw.decode("utf-8", "replace")      # unreadable: the whole file counts
    if not isinstance(d, dict):
        return raw.decode("utf-8", "replace")
    sc = d.get("scripts") if isinstance(d.get("scripts"), dict) else {}
    sub = {"scripts": dict((k, v) for k, v in sc.items() if re.match(r"^(pre|post)?test", str(k)))}
    sub.update((k, d[k]) for k in ("jest", "mocha", "ava", "vitest") if k in d)
    return json.dumps(sub, sort_keys=True) if (sub["scripts"] or len(sub) > 1) else ""


# D-243 (Amendment 7, R1): what an in-repo environment loads before any test runs. The general walk skips RC_SKIP, so
# virtualenvs and node_modules are read here instead, file by file: an ordinary package install changes none of these
# unless it ships a startup file or a pytest plugin. Anything else inside them can still fake a pass (D-244).
SITE_STARTUP = ("sitecustomize.py", "usercustomize.py")          # plus every *.pth at the top of site-packages
SITE_LIMIT = 5000                                                # site-packages entries read for entry points
NODE_STATE = (".package-lock.json", ".modules.yaml", ".yarn-state.yml")   # npm, pnpm, yarn install state
JS_HOOK_KEYS = ("setupFiles", "setupFilesAfterEnv", "globalSetup", "globalTeardown", "reporters", "reporter",
                "testRunner", "require")
JS_CONFIGS = ("jest.config.", "vitest.config.", "vitest.workspace.", "vite.config.", ".mocharc")


def _site_dirs(venv):
    out = []
    for pat in ("lib/python*/site-packages", "lib64/python*/site-packages", "Lib/site-packages"):
        for d in sorted(glob.glob(os.path.join(venv, pat))):
            if os.path.isdir(d) and os.path.realpath(d) not in [os.path.realpath(x) for x in out]:
                out.append(d)
    return out


def _has_pytest11(raw):
    return re.search(rb"^\s*\[\s*pytest11\s*\]", raw or b"", re.M) is not None


def _js_refs(text, is_json):
    """The strings a jest/vitest/mocha config gives its setup, global setup, reporter and runner keys."""
    out = []
    if is_json:
        try:
            todo = [json.loads(text)]
        except ValueError:   # D-270 (b): a runner config that does not parse is not run by the runner either; the file itself is hashed
            todo = []
        while todo:
            x = todo.pop()
            if isinstance(x, dict):
                for k, v in x.items():
                    if k in JS_HOOK_KEYS:
                        for s in (v if isinstance(v, list) else [v]):
                            s = s[0] if isinstance(s, list) and s else s
                            if isinstance(s, str):
                                out.append(s)
                    else:
                        todo.append(v)
            elif isinstance(x, list):
                todo.extend(x)
        return out
    keys = "|".join(JS_HOOK_KEYS)
    for m in re.finditer(r"\b(?:%s)\b[\"']?\s*[:=]\s*(\[[^\]]*\]|[\"'][^\"'\n]+[\"']|[^\s,#\[{]+)" % keys, text):
        v = m.group(1)
        out += re.findall(r"[\"']([^\"'\n]+)[\"']", v) if v[:1] in "[\"'" else [v]
    for m in re.finditer(r"^\s*(?:%s)\s*:\s*\n((?:\s*-\s*\S+\s*\n?)+)" % keys, text, re.M):   # YAML lists
        out += [x.strip("'\"") for x in re.findall(r"-\s*(\S+)", m.group(1))]
    return out


def _js_target(root, cdir, s):
    """The file inside a node_modules folder that a config string names, or None (repo files and built-ins)."""
    s = s.replace("<rootDir>/", "").replace("<rootDir>", "")
    if "node_modules/" in s:
        p = os.path.normpath(os.path.join(root if s.startswith("node_modules/") else cdir, s))
    elif s and not s.startswith((".", "/", "<")) and re.match(r"^(@[\w.-]+/)?[\w.-]+(/[\w./-]*)?$", s):
        p, d = None, cdir
        while True:
            c = os.path.join(d, "node_modules", s)
            if os.path.exists(c) or os.path.exists(c + ".js"):
                p = c
                break
            if os.path.realpath(d) == os.path.realpath(root) or os.path.dirname(d) == d:
                break
            d = os.path.dirname(d)
        if p is None:
            return None
    else:
        return None
    if os.path.isdir(p):
        try:
            main = json.load(open(os.path.join(p, "package.json"), encoding="utf-8")).get("main") or "index.js"
        except FileNotFoundError:   # D-270 (normal): no package.json in that package folder; index.js is the default entry
            main = "index.js"
        except Exception as exc:   # D-259 (closed): a fault in the hook (the installer has no fault list and records index.js)
            if "fault" in globals():        # D-259: the hook (the installer has no fault list and records index.js)
                globals()["fault"]("the runner-config read of %s" % os.path.join(p, "package.json"), exc)
            main = "index.js"
        p = os.path.normpath(os.path.join(p, str(main)))
    for c in (p, p + ".js", p + ".cjs", p + ".mjs", os.path.join(p, "index.js")):
        if os.path.isfile(c):
            return c
    return None


def env_control_hashes(root, venvs, node_dirs, js_configs):
    """{key: sha256} for the startup files of every in-repo environment (D-243): in each site-packages every *.pth,
    sitecustomize.py, usercustomize.py and every *.dist-info or *.egg-info entry_points.txt with a [pytest11] section;
    in each node_modules folder its install state file; and every file a jest, vitest or mocha config names inside
    node_modules. `js_configs` is [(repo path, bytes)]."""
    sha = lambda b: hashlib.sha256(b).hexdigest()
    top = os.path.realpath(root)
    rel = lambda p: (os.path.relpath(p, root).replace(os.sep, "/") if os.path.realpath(p).startswith(top + os.sep)
                     else os.path.realpath(p))                     # an environment outside the repo: its full path
    out = {}

    def put(path, label):
        try:
            with open(path, "rb") as fh:
                b = fh.read()
        except OSError:   # D-270 (closed): a file not read is left out of the hashes, and a changed set differs from the baseline, which blocks
            return None
        out["%s (%s)" % (rel(path), label)] = sha(b)
        return b
    for v in sorted(set(venvs)):
        for sp in _site_dirs(v):
            try:
                entries = sorted(os.listdir(sp))
            except OSError:   # D-270 (b): a folder or file the hook cannot read is one the interpreter cannot read either
                continue
            for e in entries:
                if e.endswith(".pth") or e in SITE_STARTUP:
                    put(os.path.join(sp, e), "environment startup file")
            for e in (entries if len(entries) <= SITE_LIMIT else []):
                if e.endswith((".dist-info", ".egg-info")):
                    ep = os.path.join(sp, e, "entry_points.txt")
                    try:
                        with open(ep, "rb") as fh:
                            raw = fh.read()
                    except OSError:   # D-270 (b): a folder or file the hook cannot read is one the interpreter cannot read either
                        continue
                    if _has_pytest11(raw):
                        out["%s (pytest plugin entry point)" % rel(ep)] = sha(raw)
    for nm in sorted(set(node_dirs)):
        for f in NODE_STATE:
            if os.path.isfile(os.path.join(nm, f)):
                put(os.path.join(nm, f), "install state")
    for crel, raw in js_configs:
        cdir = os.path.dirname(os.path.join(root, crel))
        text = raw.decode("utf-8", "replace")
        if crel.rsplit("/", 1)[-1] == "package.json":
            try:
                d = json.loads(text)
                text = json.dumps(dict((k, d[k]) for k in ("jest", "mocha", "vitest") if isinstance(d, dict) and k in d))
            except ValueError:   # D-270 (b): a package.json that does not parse is not read by the runner; the whole file is hashed
                text = "{}"
        for s in _js_refs(text, crel.endswith(".json")):
            t = _js_target(root, cdir, s)
            if t and os.path.realpath(t).startswith(os.path.realpath(root) + os.sep):
                put(t, "named by %s" % crel)
    return out


def _cmd_venvs(root, test_cmd):
    """The virtualenvs the test command's interpreter or runner lives in, inside the repo or not (`/x/venv/bin/python
    -m pytest`): audit 7 forged through one outside the repo too. A folder counts when it holds pyvenv.cfg."""
    out = []
    for t in _simple_commands(test_cmd or ""):
        for tok in t:
            if "/" in tok and re.match(r"^(python(\d(\.\d+)?)?|py\.?test)$", tok.rsplit("/", 1)[-1]):
                d = os.path.dirname(os.path.dirname(os.path.join(root, tok)))
                if os.path.isfile(os.path.join(d, "pyvenv.cfg")):
                    out.append(os.path.realpath(d))
    return out


def _rc_pytest11(text, base):
    """pyproject.toml: the pytest11 entry-point tables and any line naming pytest11; setup.cfg: an entry_points section
    that names pytest11 (D-243)."""
    out, keep, sec = [], False, []
    for line in text.splitlines():
        st = line.strip()
        m = re.match(r"^\[\[?\s*([^\]]+?)\s*\]\]?\s*(#.*)?$", st)
        if m:
            name = re.sub(r"[\s\"']", "", m.group(1))
            if base == "setup.cfg":
                if keep and any("pytest11" in x for x in sec):
                    out += sec
                sec, keep = [], name in ("options.entry_points", "entry_points")
            else:
                keep = name in ("project.entry-points.pytest11", "tool.poetry.plugins.pytest11")
        if base == "setup.cfg":
            if keep and st:
                sec.append(line.rstrip())
        elif st and (keep or "pytest11" in st):
            out.append(line.rstrip())
    if base == "setup.cfg" and keep and any("pytest11" in x for x in sec):
        out += sec
    return "\n".join(out)


def _env_dirs(dp, dn, venvs, node_dirs):
    """Note the environment folders among a directory's children before the walk drops them (D-243)."""
    for x in dn:
        p = os.path.join(dp, x)
        if x in (".venv", "venv"):
            venvs.append(p)
        elif x == "node_modules":
            node_dirs.append(p)
        elif x == ".tox":
            try:
                venvs.extend(os.path.join(p, e) for e in sorted(os.listdir(p)) if os.path.isdir(os.path.join(p, e)))
            except OSError:   # D-270 (b): a .tox folder the hook cannot list is not searched for environments
                pass


def runner_control_hashes(root, test_cmd, names=None, read=None, env=True):
    """{key: sha256} for every runner-control input present (D-233): the file path, or for a shared file the path
    plus the part read. `names`/`read` read another tree (copy mode: the merge base); by default the work tree is
    walked, the RC_SKIP folders aside, and with `env` the in-repo environments are read too (D-243; copy mode passes
    False: they are not in git, so the base branch has none). None when the walk passes RC_WALK_LIMIT."""
    venvs, node_dirs = [], []
    if names is None:
        names, n = [], 0
        for dp, dn, fn in os.walk(root):
            if "pyvenv.cfg" in fn and dp != root:
                venvs.append(dp)
                dn[:] = []
                continue
            _env_dirs(dp, dn, venvs, node_dirs)
            dn[:] = [x for x in dn if x not in RC_SKIP]
            n += len(fn) + len(dn)
            if n > RC_WALK_LIMIT:
                return None
            names += [os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/") for f in fn]
    if read is None:
        def read(rel):
            try:
                with open(os.path.join(root, rel), "rb") as fh:
                    return fh.read()
            except OSError:   # D-270 (closed): a file not read at the base differs from the work tree, which blocks
                return None
    sha = lambda b: hashlib.sha256(b.encode("utf-8") if isinstance(b, str) else b).hexdigest()
    if isinstance(test_cmd, (list, tuple)):              # D-246: every recorded command
        test_cmd = " ; ".join(str(x) for x in test_cmd)
    named = set()
    for t in _simple_commands(test_cmd or ""):
        for tok in t[1:] + t[:1]:
            for v in (tok, tok.split("=", 1)[-1]):
                v = v[2:] if v.startswith("./") else v
                if os.path.isabs(v):
                    v = os.path.relpath(v, root) if os.path.realpath(v).startswith(root + os.sep) else ""
                if v and not v.startswith("..") and not TEST_FILE.search(v):
                    named.add(os.path.normpath(v).replace(os.sep, "/"))
    out, js_configs = {}, []
    for rel in names:
        base = rel.rsplit("/", 1)[-1]
        if env and (base == "package.json" or base.startswith(JS_CONFIGS)):
            b = read(rel)
            if b is not None:
                js_configs.append((rel, b))
        if base in ("pyproject.toml", "setup.cfg"):
            b = read(rel)
            part = _rc_pytest11(b.decode("utf-8", "replace"), base) if b is not None else ""
            if part:
                out["%s [pytest11 entry points]" % rel] = sha(part)
        if (base in RUNNER_CONTROL["names"] or base.endswith(RUNNER_CONTROL["suffixes"])
                or base.startswith(RUNNER_CONTROL["prefixes"])):
            b = read(rel)
            if b is not None:
                out[rel] = sha(b)
        if base in RUNNER_CONTROL["sections"]:
            b = read(rel)
            part = _rc_section(b.decode("utf-8", "replace"), RUNNER_CONTROL["sections"][base]) if b is not None else ""
            if part:
                out["%s [%s]" % (rel, RUNNER_CONTROL["sections"][base])] = sha(part)
        if base == "package.json":
            b = read(rel)
            part = _rc_package(b) if b is not None else ""
            if part:
                out["%s (test scripts, jest/mocha/ava/vitest keys)" % rel] = sha(part)
        if rel in named:
            b = read(rel)
            if b is not None:
                out["%s (named in the test command)" % rel] = sha(b)
    if env:
        venvs += [v for v in _cmd_venvs(root, test_cmd) if os.path.realpath(v) not in [os.path.realpath(x) for x in venvs]]
        out.update(env_control_hashes(root, venvs, node_dirs, js_configs))
    return out


RUNNER_MSG = ("test runner config changed since it was last accepted: %s. A person must review it, then run "
              "/workforce-init --accept-runner-config from their own terminal.")
RUNNER_MSG_COPY = ("test runner config differs from the base branch %s: %s. Copy mode has no protected baseline (an "
                   "agent can rewrite git refs, so this check is weaker); a person must review it before it merges.")
RUNNER_NO_BASE = ("no accepted test runner config for this repo; run /workforce-init --upgrade from your own terminal")
NO_REPORT_MSG = ("the test command `%s` has no machine report the hook can read; record a direct runner command "
                 "(pytest, jest, vitest, go test, node --test, mocha, bun, dotnet, maven) with /workforce-init --upgrade "
                 "--test-cmd; see \"Direct test commands\" in UPDATING-YOUR-WORKFORCE.md or the hooks README")   # D-246
AUTO_RC_MSG = ("Workforce recorded this repo's test runner config for the first time. Review it with /workforce-doctor; "
               "from now on a change to it needs /workforce-init --accept-runner-config.")                     # D-245
CACHE_TTL = 600            # D-249: a cached run serves only later Stops of the same turn, for 10 minutes


def _ver(v):
    return tuple(int(x) for x in re.findall(r"\d+", str(v or "0"))[:3])


def record_protected(root):
    """D-245: the install record is write-protected for agents: the sandbox is on and its denyWrite lists the record."""
    try:
        st = json.load(open(os.path.join(root, ".claude", "settings.json"), encoding="utf-8"))
        sb = st.get("sandbox") or {}
        dw = (sb.get("filesystem") or {}).get("denyWrite") or []
    except Exception:          # D-259 (closed): "not protected" only narrows the first record (D-245)
        return False
    want = INSTALLED_REC.replace(os.sep, "/")
    return sb.get("enabled") is True and any(isinstance(x, str) and (x[2:] if x.startswith("./") else x) == want for x in dw)


def auto_record_runner(data, root, now):
    """D-245: write this repo's runner config into the protected baseline (the hook runs outside the sandbox). True
    when written; never over a baseline file it cannot read."""
    path = os.path.join(data, TAMPER_BASELINE)
    allb = {}
    if os.path.exists(path):
        try:
            allb = json.load(open(path, encoding="utf-8"))
        except Exception:      # D-259 (closed): no record written, the PASS stays blocked
            return False
        if not isinstance(allb, dict):
            return False
    entry = allb.get(root) if isinstance(allb.get(root), dict) else {}
    entry.update(runner_config=now, runner_config_by="the Stop hook (first record, D-245)",
                 runner_config_date=time.strftime("%Y-%m-%d"))
    allb[root] = entry
    try:
        os.makedirs(data, exist_ok=True)
        tmp = "%s.tmp-%d" % (path, os.getpid())
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(allb, fh, indent=2, sort_keys=True)
        os.replace(tmp, path)
    except Exception:          # D-259 (closed): no record written, the PASS stays blocked
        return False
    return True


def _rc_list(diff):
    return ", ".join(diff[:6]) + (" and %d more" % (len(diff) - 6) if len(diff) > 6 else "")


def runner_config_problem(project_dir, rec, cmd, now):
    """(problem, note): problem None when every runner-control input matches what was accepted (D-233); note set when
    the hook recorded the runner config itself (D-245)."""
    root = repo_top(project_dir)
    if now is None:
        return "too many files to check the test runner config (over %d)" % RC_WALK_LIMIT, None
    if rec.get("mode") == "copy":
        base = base_ref(project_dir)
        mb = (_git(project_dir, "merge-base", "HEAD", base) or "").strip() if base else ""
        if not mb:
            return "copy mode: no base branch to compare the test runner config with", None
        listing = _git(project_dir, "ls-tree", "-r", "-z", "--name-only", mb)
        if listing is None:
            return "copy mode: no base branch to compare the test runner config with", None

        def read_mb(rel):
            try:
                p = subprocess.run(["git", "-C", root, "show", "%s:%s" % (mb, rel)], capture_output=True, timeout=10)
            except Exception:  # D-259 (closed): a file not read at the base differs from the work tree, which blocks
                return None
            return p.stdout if p.returncode == 0 else None
        want = runner_control_hashes(root, cmd, [x for x in listing.split("\0") if x], read_mb, env=False)
        diff = sorted(k for k in set(want) | set(now) if want.get(k) != now.get(k))
        return ((RUNNER_MSG_COPY % (base, _rc_list(diff))) if diff else None), None
    data = plugin_data_dir()
    try:
        entry = json.load(open(os.path.join(data, TAMPER_BASELINE), encoding="utf-8")).get(root) if data else None
    except FileNotFoundError:   # D-270 (normal): no baseline file; a 2.8.3 plugin-mode record blocks on it below (BASELINE_MISSING), an older one keeps D-245
        entry = None
    except Exception as exc:   # D-259: never treat an unreadable baseline as "none yet" (the first record would overwrite it)
        return "the test runner config check could not run (%s): this gate is not passed" % type(exc).__name__, None
    want = entry.get("runner_config") if isinstance(entry, dict) else None
    if not isinstance(want, dict):
        if data and rec.get("mode") == "plugin" and record_is_new(rec) and not isinstance(entry, dict):
            return BASELINE_MISSING, None      # D-281: a 2.8.3 record with no baseline file, or none for this repo: the hook records nothing; the owner upgrades
        # D-245 (records older than 2.8.3 only, D-281): no runner config was ever accepted here (an install from before 2.8.3, or a plugin
        # bump with no re-init). Record it once and warn, instead of blocking every quality PASS; only when an agent cannot have
        # written the install record (the sandbox protects it), or the owner's terminal installed here before (the
        # protected baseline has an entry for this path). Otherwise block as before.
        if data and (record_protected(root) or isinstance(entry, dict)) and auto_record_runner(data, root, now):
            return None, AUTO_RC_MSG
        return RUNNER_NO_BASE, None
    diff = sorted(k for k in set(want) | set(now) if want.get(k) != now.get(k))
    return ((RUNNER_MSG % _rc_list(diff)) if diff else None), None


def ignored_state(root):
    """D-236: sha256 over path, size and mtime of every git-ignored file under the repo (RC_SKIP folders aside), so a
    changed ignored input re-runs the tests; None (do not cache) past 2,000 such files or with no git."""
    listed = _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    if listed is None:
        return None
    known = set(x for x in listed.split("\0") if x)
    h, n = hashlib.sha256(), 0
    for dp, dn, fn in os.walk(root):
        dn[:] = sorted(x for x in dn if x not in RC_SKIP)
        for f in sorted(fn):
            rel = os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/")
            if rel in known or rel.endswith(".pyc"):
                continue
            n += 1
            if n > 2000:
                return None
            try:
                st = os.stat(os.path.join(dp, f))
            except OSError:   # D-270 (b): a file that vanished while walking is not state
                continue
            h.update(("%s\0%d\0%d\0" % (rel, st.st_size, st.st_mtime_ns)).encode("utf-8", "replace"))
    return h.hexdigest()


def report_plan(test_cmd, root, rdir, _depth=0):
    """(command to run, report kind, report path): the test command with the runner's machine-report flags added, when
    its last simple command is a known runner and nothing pipes or redirects after it; else (test_cmd, "output", None)."""
    q = shlex.quote
    cmds = _simple_commands(test_cmd)
    if not cmds or re.search(r"[|>]|2>&1", test_cmd):
        return test_cmd, "output", None
    runner, _args = _canon(cmds[-1])
    if runner in (("python", "-m", "pytest"), ("pytest",), ("npx", "pytest")):
        f = os.path.join(rdir, "junit.xml")
        return "%s --junitxml=%s -p no:cacheprovider" % (test_cmd, q(f)), "junit", f
    if runner in (("jest",), ("npx", "jest")):
        f = os.path.join(rdir, "jest.json")
        return "%s --json --outputFile=%s" % (test_cmd, q(f)), "jestjson", f
    if runner in (("vitest",), ("npx", "vitest")):
        f = os.path.join(rdir, "vitest.json")
        return "%s --reporter=json --outputFile=%s" % (test_cmd, q(f)), "jestjson", f
    if len(runner) == 2 and runner[1] == "test" and runner[0] in ("npm", "pnpm", "yarn"):
        # D-234: through package.json's test script when it is one simple command a known runner reads
        script = _pkg_test_script(root).strip()
        if _depth > 0 or not script or len(_simple_commands(script)) != 1:
            return test_cmd, "output", None
        inner, kind, f = report_plan(script, root, rdir, _depth + 1)
        if kind == "output" or not inner.startswith(script):
            return test_cmd, "output", None
        return "%s%s%s" % (test_cmd, "" if runner[0] == "yarn" else " --", inner[len(script):]), kind, f
    if runner == ("go", "test"):
        return test_cmd + " -json", "gojson", None
    if runner == ("node", "--test"):
        f = os.path.join(rdir, "node.xml")
        return "%s --test-reporter=junit --test-reporter-destination=%s" % (test_cmd, q(f)), "junit", f
    if runner in (("mocha",), ("npx", "mocha")):
        f = os.path.join(rdir, "mocha.json")
        return "%s --reporter json --reporter-option output=%s" % (test_cmd, q(f)), "mochajson", f
    if runner == ("bun", "test"):
        f = os.path.join(rdir, "bun.xml")
        return "%s --reporter=junit --reporter-outfile=%s" % (test_cmd, q(f)), "junit", f
    if runner == ("dotnet", "test"):
        f = os.path.join(rdir, "r.trx")
        return "%s --logger %s" % (test_cmd, q("trx;LogFileName=" + f)), "trx", f
    if runner in (("mvn", "test"), ("./mvnw", "test")):
        f = os.path.join(rdir, "surefire")
        return "%s -Dsurefire.reportsDirectory=%s" % (test_cmd, q(f)), "junitdir", f
    return test_cmd, "output", None


def _junit_counts(paths):
    import xml.etree.ElementTree as ET
    total = failed = skipped = 0
    seen = False
    for path in paths:
        try:
            tree = ET.parse(path)
        except Exception:      # D-259: one report that cannot be read makes the whole reading unknown, never a pass
            return None
        seen = True
        for tc in tree.getroot().iter("testcase"):
            total += 1
            kids = {c.tag for c in tc}
            if kids & {"failure", "error"}:
                failed += 1
            elif "skipped" in kids:
                skipped += 1
        for ts in tree.getroot().iter("testsuite"):   # a suite that failed to load has errors but no testcase
            if not list(ts.iter("testcase")):
                try:
                    failed += int(ts.get("errors") or 0) + int(ts.get("failures") or 0)
                except ValueError:   # D-270 (closed): a suite whose error count cannot be read gives no count, so the run blocks
                    return None    # D-270: a suite whose error count cannot be read gives no count, so the run blocks
    return (total - failed - skipped, failed) if seen else None


def read_report(kind, path, stdout, readers):
    """(passed, failed) from the run's machine report, or from its own output for kind "output"; None when there is
    neither a report nor a summary."""
    try:
        if kind == "junit":
            return _junit_counts([path]) if path and os.path.isfile(path) else None
        if kind == "junitdir":
            return _junit_counts(sorted(glob.glob(os.path.join(path, "*.xml")))) if path and os.path.isdir(path) else None
        if kind == "jestjson":
            if not (path and os.path.isfile(path)):
                return None
            d = json.load(open(path, encoding="utf-8"))
            return int(d.get("numPassedTests") or 0), int(d.get("numFailedTests") or 0) + int(d.get("numRuntimeErrorTestSuites") or 0)
        if kind == "mochajson":
            if not (path and os.path.isfile(path)):
                return None
            st = json.load(open(path, encoding="utf-8")).get("stats") or {}
            return int(st.get("passes") or 0), int(st.get("failures") or 0)
        if kind == "trx":
            if not (path and os.path.isfile(path)):
                return None
            m = re.search(r"<Counters\b[^>]*>", open(path, encoding="utf-8", errors="replace").read())
            n = lambda a: int((re.search(r'\b%s="(\d+)"' % a, m.group(0)) or [0, 0])[1]) if m else 0
            return (n("passed"), n("failed") + n("error")) if m else None
        if kind == "gojson":
            passed = failed = 0
            seen = False
            for line in (stdout or "").splitlines():
                try:
                    e = json.loads(line)
                except ValueError:   # D-270 (b): go test -json output mixes non-JSON lines
                    continue
                if not isinstance(e, dict) or "Action" not in e:
                    continue
                seen = True
                if e.get("Test") and e["Action"] == "pass":
                    passed += 1
                elif e["Action"] == "fail":          # a test, or a package that failed to build
                    failed += 1
            return (passed, failed) if seen else None
    except Exception:          # D-259 (closed): no counts means "no test summary", which blocks
        return None
    green, passed, failed = run_is_green(stdout, False, readers)
    return None if passed is None else (passed, failed)


def confinement(argv, root, rdir, home_claude):
    """macOS: run the hook's test command under sandbox-exec with writes to the enforcement files refused (the hook
    itself runs outside Claude Code's sandbox; the tests it runs may be agent-written). (argv, note)."""
    if sys.platform != "darwin" or not os.path.isfile("/usr/bin/sandbox-exec"):
        return argv, "not confined (no sandbox-exec)"
    esc = lambda p: os.path.realpath(p).replace("\\", "\\\\").replace('"', '\\"')
    deny = ['(subpath "%s")' % esc(home_claude)]
    for sub in (".claude/hooks", ".claude/agents", ".claude/skills", ".claude/commands"):
        deny.append('(subpath "%s")' % esc(os.path.join(root, sub)))
    for f in (".claude/settings.json", ".claude/settings.local.json", INSTALLED_REC, ".claude/gates-allow.txt",
              ".claude/test-summary-patterns.txt", ".claude/live-commands-allow.txt", ".claude/review-copies.sha256"):
        deny.append('(literal "%s")' % esc(os.path.join(root, f)))
    try:
        st = json.load(open(os.path.join(root, ".claude", "settings.json"), encoding="utf-8"))
        for f in ((st.get("sandbox") or {}).get("filesystem") or {}).get("denyWrite") or []:
            if isinstance(f, str) and not f.startswith("~"):
                deny.append('(literal "%s")' % esc(os.path.join(root, f[2:] if f.startswith("./") else f)))
    except Exception:          # D-259 (b): the tamper check after the run compares every denyWrite file anyway
        pass
    prof = "(version 1)\n(allow default)\n(deny file-write* %s)\n(allow file-write* (subpath \"%s\"))\n" % (" ".join(deny), esc(rdir))
    return ["/usr/bin/sandbox-exec", "-p", prof] + argv, "confined"


def test_cmds(rec):
    """The recorded test commands (D-246): `test_cmd` is one command or a list of them."""
    v = rec.get("test_cmd")
    return [x.strip() for x in (v if isinstance(v, list) else [v]) if isinstance(x, str) and x.strip()]


def _run_one(cmd, root, tmo, base, limit):
    """One recorded command, run with its machine report (D-222, D-234): {"passed", "failed", "rc", "note"} or with
    "problem"."""
    try:
        if base:
            os.makedirs(base, exist_ok=True)
        rdir = os.path.realpath(tempfile.mkdtemp(prefix="run-", dir=base))
    except Exception:          # D-259 (b): only where the report is written
        rdir = os.path.realpath(tempfile.mkdtemp(prefix="br-test-run-"))
    run_cmd, kind, rpath = report_plan(cmd, root, rdir)
    argv, conf = confinement(["/bin/sh", "-c", run_cmd], root, rdir,
                             os.path.join(os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")))
    env = dict(os.environ, NO_COLOR="1", FORCE_COLOR="0", CI="1", PYTHONDONTWRITEBYTECODE="1")
    res = {"note": conf}
    try:
        pr = subprocess.Popen(argv, cwd=root, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, start_new_session=True)
        try:
            out, _e = pr.communicate(timeout=max(1, tmo))
            out = (out or b"").decode("utf-8", "replace")
            counts = read_report(kind, rpath, out, project_summary_readers(root))
            if counts is None:
                res["problem"] = "the hook's test run printed no test summary and wrote no report (exit %d): `%s`" % (pr.returncode, cmd)
            else:
                res.update(passed=counts[0], failed=counts[1], rc=pr.returncode)
                if not (pr.returncode == 0 and counts[0] >= 1 and counts[1] == 0):
                    res["problem"] = "the hook's test run did not pass (exit %d, %d passed, %d failed): `%s`" % (
                        pr.returncode, counts[0], counts[1], cmd)
        except subprocess.TimeoutExpired:   # D-286 (closed): the timeout problem line is set below
            try:
                os.killpg(pr.pid, 9)
            except Exception:  # D-259 (b): the timeout problem is already set
                pr.kill()
            pr.communicate()
            res["problem"] = "test run exceeded %d s; raise test_timeout or split the suite" % limit
        except BudgetExceeded:   # D-278: the hook's own deadline fired mid-run: the test run is killed with it, then main() answers
            try:
                os.killpg(pr.pid, 9)
            except Exception:  # D-278 (b): the child may already be gone
                pr.kill()
            raise
    except Exception as exc:   # D-259 (closed): a problem line
        res["problem"] = "the hook could not run the test command (%s): `%s`" % (type(exc).__name__, cmd)
    finally:
        shutil.rmtree(rdir, ignore_errors=True)
    return res


def hook_test_run(project_dir, session_id, turn_key=None):
    """The hook's own test run for a quality PASS (D-222): {"problem": str} or {"passed", "failed", "cmd", "cmds",
    "cached", "note", "notes"}. Every recorded command must have a machine report (D-234, D-246) and the runner config
    must match what was accepted (D-233) before anything runs; every command must pass, and the counts add (D-246).
    A run is cached only for later Stops of the same turn, for CACHE_TTL seconds (D-249), keyed by the commands, the
    timeout, the tree, the runner config and the git-ignored files (D-236); files outside the repo can be stale only
    inside that window."""
    rec = install_record(project_dir)
    cmds = test_cmds(rec)
    if not cmds:
        return {"problem": "no test command recorded; run /workforce-init"}
    try:
        tmo = int(rec.get("test_timeout") or TEST_TIMEOUT_DEFAULT)
    except (TypeError, ValueError):   # D-270 (b): an unreadable test_timeout falls back to the default timeout
        tmo = TEST_TIMEOUT_DEFAULT
    tmo = max(1, min(tmo, TEST_TIMEOUT_MAX))
    step("the test run")
    left = time_left()
    if left < 1e8:       # D-278: later steps (the CI read, the validators, the answer) keep 120 s of the budget
        tmo = max(1, min(tmo, int(left) - 120)) if left > 125 else max(1, min(tmo, 5))
    root = repo_top(project_dir)
    for c in cmds:
        if report_plan(c, root, os.path.join(root, ".br-no-run"))[1] == "output":
            return {"problem": NO_REPORT_MSG % c}         # D-234: no PASS from a run the hook cannot read directly
    joined = " ; ".join(cmds)
    rc_now = runner_control_hashes(root, cmds, env=rec.get("mode") != "copy")
    rc_prob, rc_note = runner_config_problem(project_dir, rec, cmds, rc_now)
    if rc_prob:
        return {"problem": rc_prob}                       # D-233: checked before the run, never cached
    notes = [rc_note] if rc_note else []
    data = plugin_data_dir()
    state = tree_state(root)
    ign = ignored_state(root)                             # D-236: ignored inputs and runner config join the key
    key = hashlib.sha256(("%s\0%s\0%d\0%s\0%s\0%s" % (turn_key, joined, tmo, state, json.dumps(rc_now, sort_keys=True), ign)).encode(
        "utf-8")).hexdigest() if state and ign and turn_key else None
    cache_file = None
    if data and key:
        cache_file = os.path.join(data, "test-runs", re.sub(r"[^A-Za-z0-9_.-]", "-", str(session_id or "nosession")) + ".json")
        try:
            hit = json.load(open(cache_file, encoding="utf-8")).get(key)
            if isinstance(hit, dict) and isinstance(hit.get("res"), dict) and 0 <= time.time() - float(hit.get("t") or 0) <= CACHE_TTL:
                return dict(hit["res"], cached=True, notes=notes)
        except Exception:      # D-259 (b): a cache miss runs the tests again
            pass
    base = os.path.join(data, "test-runs", "reports") if data else None
    res = {"cmd": joined, "cmds": cmds, "passed": 0, "failed": 0, "note": None}
    deadline = time.time() + tmo
    for i, c in enumerate(cmds):
        one = _run_one(c, root, int(deadline - time.time()), base, tmo)
        res["note"] = one.get("note")
        res["passed"] += int(one.get("passed") or 0)
        res["failed"] += int(one.get("failed") or 0)
        if one.get("problem"):
            res["problem"] = one["problem"] if len(cmds) == 1 else "command %d of %d: %s" % (i + 1, len(cmds), one["problem"])
            break
    if cache_file:
        try:
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            try:
                cache = json.load(open(cache_file, encoding="utf-8"))
            except Exception:  # D-259 (b): the cache only
                cache = {}
            now_t = time.time()
            cache = dict((k, v) for k, v in cache.items() if isinstance(v, dict) and now_t - float(v.get("t") or 0) <= CACHE_TTL)
            cache[key] = {"t": now_t, "res": res}
            with open(cache_file, "w", encoding="utf-8") as fh:
                json.dump(cache, fh)
        except Exception:      # D-259 (b): the cache only; the result below is returned either way
            pass
    return dict(res, cached=False, notes=notes)



# D-252 (Amendment 8, S2): CI IS THE JUDGE. Every bypass from audit 4 to audit 7 had one root: the hook runs code the
# judged agent wrote, in a folder the agent controls. A quality PASS now stands only when GitHub Actions ran the
# workforce-proof workflow for this exact commit on a clean runner and both its jobs passed. The facts the design rests
# on were measured (Amendment 8 C-0): a personal token cannot create a check run, it can create a commit status (so
# statuses are never read), and an Actions check run carries app `github-actions` and its workflow run's check suite.
# The local run (D-222 to D-249) still runs first and a local red blocks at once; it is the early warning.
CI_WORKFLOW = ".github/workflows/workforce-proof.yml"
CI_JOBS = ("head-suite", "base-suite")
CI_TIMEOUT = 20            # seconds for the one read of GitHub per Stop
CI_GOOD = ("success",)
CI_IGNORE = ("skipped",)   # a job skipped by its own condition (a push to the default branch)
NO_CI_JUDGE_LINE = ("No CI judge: test passes are checked only on this machine, where an agent can fake them. Use CI for "
                    "real proof.")                                                                   # D-254
CI_WAIT = "tests: waiting on CI for %s; the gate is not passed yet"
CI_PUSH = "tests: commit and push; CI decides (%s)"
# D-261 (U4): the base branch decides what CI can judge. The same default test-file globs as the workforce-proof judge
# (DEFAULT_GLOBS in workforce-proof.yml; c1/run_fixture_judge.py checks the two lists match).
WF_DEFAULT_GLOBS = ["tests/**", "test/**", "**/tests/**", "**/test/**", "**/__tests__/**", "**/test_*.py", "**/*_test.py",
                    "**/*_test.go", "**/*.test.*", "**/*.spec.*", "**/*Test.java", "**/*Tests.java", "**/*Test.kt",
                    "**/*Tests.cs", "**/*Test.cs"]
NO_BASE_RECORD = ("base branch has no Workforce install record; the first Workforce pull request is approved by the owner on "
                  "review, not by CI")
NO_BASE_TESTS = "no base tests to run; the owner's review decides this pull request"


def _wf_glob_re(g):
    out, i = "", 0
    while i < len(g):
        if g[i:i + 3] == "**/":
            out, i = out + "(?:.*/)?", i + 3
        elif g[i:i + 2] == "**":
            out, i = out + ".*", i + 2
        elif g[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif g[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(g[i]), i + 1
    return re.compile(out + r"\Z")


def base_judgeable(root, head, pr_base=None):
    """D-261: None when the merge base has an install record and test files CI can run; else the INCOMPLETE reason.
    None also when no base branch is found here (CI's own merge base decides then). pr_base (D-275): the open pull request's
    base branch, which CI's pull_request run uses; a base that is not in this clone is an INCOMPLETE reason, not a guess."""
    if pr_base:
        base = next((c for c in ("origin/" + pr_base, pr_base) if _git(root, "rev-parse", "--verify", "--quiet", c) is not None), None)
        if base is None:
            return "the pull request's base %s is not in this clone: run git fetch origin %s, then end the turn again" % (pr_base, pr_base)
    else:
        base = base_ref(root)
    mb = (_git(root, "merge-base", base, head) or "").strip() if base else ""
    if not mb:
        return None
    raw = _git(root, "show", "%s:%s" % (mb, INSTALLED_REC.replace(os.sep, "/")))
    if raw is None:
        return NO_BASE_RECORD
    try:
        brec = json.loads(raw)
    except ValueError:   # D-270 (closed): an unreadable base record is NO_BASE_RECORD, which is INCOMPLETE
        return NO_BASE_RECORD
    globs = brec.get("test_globs") if isinstance(brec, dict) and isinstance(brec.get("test_globs"), list) and brec.get("test_globs") else WF_DEFAULT_GLOBS
    rx = [_wf_glob_re(g) for g in globs]
    files = [x for x in (_git(root, "ls-tree", "-r", "-z", "--name-only", mb) or "").split("\0") if x]
    return None if any(r.match(p) for p in files for r in rx) else NO_BASE_TESTS


GH_REMOTE = re.compile(r"^(?:https:/{2}(?:[^@/]+@)?github\.com/|git@github\.com:|ssh://git@github\.com/)([^/\s]+)/([^/\s]+?)(?:\.git)?/?$")


def github_repo(root):
    """(owner, name) of the repo's GitHub remote: origin, else the first remote on github.com; None when there is none."""
    names = [x for x in (_git(root, "remote") or "").split() if x]
    for n in (["origin"] if "origin" in names else []) + [x for x in names if x != "origin"]:
        m = GH_REMOTE.match((_git(root, "remote", "get-url", n) or "").strip())
        if m:
            return m.group(1), m.group(2)
    return None


def gh_api(path, deadline):
    """(status, data): status "ok", "missing" (404/422), "auth", "offline", "timeout", "no-gh" or "error"."""
    exe = shutil.which("gh")
    if not exe:
        return "no-gh", None
    left = deadline - time.time()
    if left <= 0:
        return "timeout", None
    env = dict(os.environ, GH_PROMPT_DISABLED="1", NO_COLOR="1", GH_NO_UPDATE_NOTIFIER="1")
    try:
        p = subprocess.run([exe, "api", path], capture_output=True, text=True, timeout=left, env=env, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:   # D-270 (closed): a gh timeout is INCOMPLETE, never a PASS (D-252)
        return "timeout", None
    except Exception:          # D-259 (closed): INCOMPLETE, never a PASS (D-252)
        return "error", None
    if p.returncode == 0:
        try:
            return "ok", json.loads(p.stdout or "null")
        except ValueError:   # D-270 (closed): a reply that is not JSON is INCOMPLETE, never a PASS (D-252)
            return "error", None
    return _gh_classify((p.stderr or "") + (p.stdout or "")), None


def _gh_classify(err):
    if re.search(r"HTTP 40[4]|HTTP 422|Not Found|No commit found", err):
        return "missing"
    if re.search(r"HTTP 401|gh auth login|authentication|Bad credentials|not logged", err, re.I):
        return "auth"
    if re.search(r"rate limit", err, re.I):
        return "rate-limit"                 # D-266 (V9): INCOMPLETE, never a PASS
    if re.search(r"x509|failed to verify certificate|OSStatus -26276", err):
        return "sandbox-tls"                # measured (A8 C-5): gh inside Claude Code's macOS sandbox cannot verify TLS
    if re.search(r"dial tcp|no such host|connection refused|network is unreachable|timeout|could not resolve|error connecting", err, re.I):
        return "offline"
    GH_LAST_ERR[0] = " ".join(err.split())[:160]
    return "error"


def pr_base_ref(root, deadline):
    """D-275 (Amendment 10, Y8): the base branch of the open pull request for the current branch, read with
    `gh pr view --json baseRefName` (the hook runs outside the sandbox). (status, name): "ok" with the name, "none" when
    the branch has no open pull request, else a gh_api-style failure status."""
    exe = shutil.which("gh")
    if not exe:
        return "no-gh", None
    left = deadline - time.time()
    if left <= 0:
        return "timeout", None
    env = dict(os.environ, GH_PROMPT_DISABLED="1", NO_COLOR="1", GH_NO_UPDATE_NOTIFIER="1")
    try:
        p = subprocess.run([exe, "pr", "view", "--json", "baseRefName"], capture_output=True, text=True, timeout=left, env=env,
                           stdin=subprocess.DEVNULL, cwd=root)
    except subprocess.TimeoutExpired:   # D-270 (closed): INCOMPLETE, never a PASS
        return "timeout", None
    except Exception:          # D-270 (closed): INCOMPLETE, never a PASS
        return "error", None
    if p.returncode == 0:
        try:
            name = (json.loads(p.stdout or "null") or {}).get("baseRefName")
        except (ValueError, AttributeError):   # D-270 (closed): a reply that is not JSON is INCOMPLETE
            return "error", None
        return ("ok", name) if isinstance(name, str) and name else ("error", None)
    err = (p.stderr or "") + (p.stdout or "")
    if re.search(r"no (open )?pull requests? found", err, re.I):
        return "none", None
    return _gh_classify(err), None


def base_name(root):
    """The default branch's name for messages and comparison: origin/main -> main; None when only a commit was found."""
    b = base_ref(root)
    if not b or re.fullmatch(r"[0-9a-f]{40}", b):
        return None
    return b[len("origin/"):] if b.startswith("origin/") else b


GH_LAST_ERR = [""]       # the last unclassified gh error, quoted in the message so it can be diagnosed
GH_WHY = {"no-gh": "the GitHub CLI (gh) is not installed", "auth": "gh is not signed in to GitHub",
          "offline": "GitHub could not be reached",
          "rate-limit": "GitHub's API rate limit is used up; a later turn reads CI again",
          "sandbox-tls": "gh cannot verify GitHub's certificate here, inside Claude Code's sandbox; run it from your own terminal", "timeout": "GitHub did not answer within %d s" % CI_TIMEOUT,
          "error": "GitHub gave an answer the hook could not read"}


def gh_why(st):
    w = GH_WHY.get(st, st)
    return w + (" (gh: %s)" % GH_LAST_ERR[0] if st == "error" and GH_LAST_ERR[0] else "")


def ci_workflow_hash(rec, root):
    """The sha256 /workforce-init recorded for the CI workflow: the protected tamper baseline (plugin mode), else the
    install record's file list (copy mode, weaker)."""
    data = plugin_data_dir()
    if rec.get("mode") != "copy" and data:
        try:
            files = (json.load(open(os.path.join(data, TAMPER_BASELINE), encoding="utf-8")).get(root) or {}).get("files") or {}
            return files.get(CI_WORKFLOW)
        except Exception:      # D-259 (closed): "never recorded" blocks
            return None
    return ((rec.get("files") or {}).get(CI_WORKFLOW) or {}).get("sha256")


def ci_judge(project_dir, rec):
    """D-252: {"state": "pass" | "fail" | "wait" | "incomplete", "msg": str, "sha": str}. One read of GitHub, CI_TIMEOUT
    seconds in all. Commit statuses are never read."""
    step("the CI read")
    deadline = time.time() + min(CI_TIMEOUT, max(1.0, time_left() - 5))
    root = repo_top(project_dir)
    head = (_git(root, "rev-parse", "HEAD") or "").strip()
    out = lambda state, msg: {"state": state, "msg": msg, "sha": head}
    if not head:
        return out("incomplete", CI_PUSH % "no commit yet")
    short = head[:7]
    repo = github_repo(root)
    if repo is None:                                      # D-254
        return out("incomplete", "tests: no CI judge for this repo (no GitHub remote); the gate is not passed. "
                                 "/workforce-init --no-ci-judge makes this machine's check the judge, which an agent can fake")
    dirty = _git(root, "status", "--porcelain", "--untracked-files=normal")
    if dirty is None:
        return out("incomplete", "tests: git status could not be read; the gate is not passed yet")
    if dirty.strip():
        return out("incomplete", CI_PUSH % "uncommitted changes in the work tree")
    try:
        raw = subprocess.run(["git", "-C", root, "show", "HEAD:" + CI_WORKFLOW], capture_output=True, timeout=10)
        wf = raw.stdout if raw.returncode == 0 else None
    except Exception:          # D-259 (closed): "not in commit" blocks
        wf = None
    want = ci_workflow_hash(rec, root)
    if wf is None:
        return out("fail", "the CI workflow %s is not in commit %s; run /workforce-init --upgrade from your own terminal" % (CI_WORKFLOW, short))
    if not want:
        return out("fail", "the CI workflow was never recorded for this repo; run /workforce-init --upgrade from your own terminal")
    if hashlib.sha256(wf).hexdigest() != want:
        return out("fail", "the CI workflow in commit %s differs from the one /workforce-init recorded; a person must review the "
                           "change, then run /workforce-init --accept-changes from their own terminal" % short)
    # D-261: never a PASS, never a block: the owner reviews it. D-275 (Y8): the base is the open pull request's base when there is one
    # (CI's pull_request run uses it), else the default branch; the message says which, and CI's own run is compared below.
    hb, hb_src = base_name(root), "the default branch"
    why = base_judgeable(root, head)
    if why:
        pst, pb = pr_base_ref(root, deadline)
        if pst == "ok" and pb:
            hb, hb_src = pb, "the open pull request's base"
            why = base_judgeable(root, head, pb) if pb != base_name(root) else why
        if why:
            return out("incomplete", "tests: %s (base used: %s, %s)" % (why, hb or "none found", hb_src))
    o, n = repo
    st, _c = gh_api("repos/%s/%s/commits/%s" % (o, n, head), deadline)
    if st == "missing":
        return out("incomplete", CI_PUSH % ("commit %s is not on GitHub" % short))
    if st != "ok":
        return out("incomplete", "tests: CI not read (%s); the gate is not passed yet" % gh_why(st))
    st, runs = gh_api("repos/%s/%s/actions/runs?head_sha=%s&per_page=100" % (o, n, head), deadline)
    if st != "ok":
        return out("incomplete", "tests: CI not read (%s); the gate is not passed yet" % gh_why(st))
    suites = dict((r.get("check_suite_id"), r) for r in (runs or {}).get("workflow_runs") or []
                  if isinstance(r, dict) and r.get("path") == CI_WORKFLOW and r.get("head_sha") == head)
    if not suites:
        return out("wait", (CI_WAIT % short) + " (no workforce-proof run yet; if none starts, check that Actions is on)")
    st, crs = gh_api("repos/%s/%s/commits/%s/check-runs?per_page=100" % (o, n, head), deadline)
    if st != "ok":
        return out("incomplete", "tests: CI not read (%s); the gate is not passed yet" % gh_why(st))
    latest = {}
    for c in (crs or {}).get("check_runs") or []:
        if not isinstance(c, dict):
            continue
        suite = (c.get("check_suite") or {}).get("id")
        if (c.get("app") or {}).get("slug") != "github-actions" or suite not in suites or c.get("name") not in CI_JOBS \
                or c.get("head_sha") not in (None, head):
            continue
        k = (suite, c.get("name"))
        if k not in latest or int(c.get("id") or 0) > int(latest[k].get("id") or 0):
            latest[k] = c
    bad = [c for c in latest.values() if c.get("status") == "completed" and c.get("conclusion") not in CI_GOOD + CI_IGNORE]
    if bad:
        c = sorted(bad, key=lambda x: x.get("name"))[0]
        return out("fail", "CI failed for %s: %s concluded %s (%s)" % (short, c.get("name"), c.get("conclusion"), c.get("html_url") or ""))
    # D-262 (U5): every workforce-proof run for this commit (push and pull_request) must be complete and green; a run
    # whose two jobs both skipped (a push to the default branch) is not one of them.
    live = [(suite, run) for suite, run in suites.items()
            if not all((latest.get((suite, j)) or {}).get("conclusion") in CI_IGNORE for j in CI_JOBS)]
    pending = [run for suite, run in live if not all((latest.get((suite, j)) or {}).get("status") == "completed" for j in CI_JOBS)]
    if live and not pending and all((latest.get((suite, j)) or {}).get("conclusion") in CI_GOOD for suite, _r in live for j in CI_JOBS):
        run = sorted((r for _s, r in live), key=lambda r: -int(r.get("id") or 0))[0]
        # D-275: CI's pull_request run judges against the pull request's base; this check must have used the same one
        run_bases = sorted(set(((r.get("pull_requests") or [{}])[0].get("base") or {}).get("ref") for _s, r in live
                               if r.get("event") == "pull_request" and r.get("pull_requests")) - {None})
        if run_bases:
            if hb_src != "the open pull request's base":
                pst, pb = pr_base_ref(root, deadline)
                if pst == "ok" and pb:
                    hb, hb_src = pb, "the open pull request's base"
                    why2 = base_judgeable(root, head, pb)
                    if why2:
                        return out("incomplete", "tests: %s (base used: %s, %s)" % (why2, hb, hb_src))
            if hb and any(b != hb for b in run_bases):     # an unknown base (none found here) is not a mismatch: CI's own merge base decides
                return out("incomplete", "tests: CI's pull request run judged this commit against base %s, but this check used %s (%s); the gate "
                                         "is not passed yet" % (", ".join(run_bases), hb, hb_src))
        return out("pass", "CI passed for %s: head-suite and base-suite in all %d run(s) (%s)%s" % (
            short, len(live), run.get("html_url") or "", ("; judged against base %s, %s" % (hb, hb_src)) if hb else ""))
    run = sorted(pending or [r for _s, r in live] or list(suites.values()), key=lambda r: -int(r.get("id") or 0))[0]
    return out("wait", (CI_WAIT % short) + " (%s)" % (run.get("html_url") or ""))


def disk_check_status(root):
    """D-279: what the doctor reports about the disk check: {"skipped": bool, "reason": str|None, "candidates": int|None}."""
    DISK_SKIP["reason"] = None
    try:
        c = _snap_candidates(os.path.realpath(root))
    except Exception as exc:   # D-279 (closed): the doctor reports it as not checked
        return {"skipped": True, "reason": "the file list could not be read (%s)" % type(exc).__name__, "candidates": None}
    return {"skipped": c is None, "reason": DISK_SKIP["reason"], "candidates": None if c is None else len(c)}


def ci_status(project_dir):
    """`validate-verdicts.py --ci-status [dir]` (D-253): what the doctor reports, as JSON: the CI judge setting, the
    workflow file against the recorded hash, the default branch's required checks, and the judge for HEAD."""
    root = repo_top(project_dir)
    rec = install_record(root)
    res = {"ci_judge": rec.get("ci_judge") is not False, "repo": None, "workflow": None, "branch_protection": None, "judge": None,
           "writers": None, "actions_approve": None, "disk_check": None}
    wf_path = os.path.join(root, CI_WORKFLOW)
    want = ci_workflow_hash(rec, root)
    have = hashlib.sha256(open(wf_path, "rb").read()).hexdigest() if os.path.isfile(wf_path) else None
    res["workflow"] = "missing" if have is None else ("not recorded" if not want else ("matches" if have == want else "differs"))
    repo = github_repo(root)
    if repo:
        res["repo"] = "%s/%s" % repo
        deadline = time.time() + CI_TIMEOUT
        st, info = gh_api("repos/%s/%s" % repo, deadline)
        branch = (info or {}).get("default_branch") if st == "ok" else None
        if branch:
            bp = {"branch": branch, "protected": None, "required_checks": [], "requires_both": False, "strict": None,
                  "reviews_readable": False, "required_approving_review_count": None, "dismiss_stale_reviews": None,
                  "require_last_push_approval": None, "enforce_admins": None}
            names = set()
            # D-260 (V6): the full classic protection needs an admin login; it holds the review settings
            st, full = gh_api("repos/%s/%s/branches/%s/protection" % (repo[0], repo[1], branch), deadline)
            if st == "ok" and isinstance(full, dict):
                rsc = full.get("required_status_checks") or {}
                names |= set(rsc.get("contexts") or []) | set((x or {}).get("context") for x in rsc.get("checks") or [])
                rv = full.get("required_pull_request_reviews") or {}
                bp.update(protected=True, strict=bool(rsc.get("strict")), reviews_readable=True,
                          required_approving_review_count=int(rv.get("required_approving_review_count") or 0),
                          dismiss_stale_reviews=bool(rv.get("dismiss_stale_reviews")),
                          require_last_push_approval=bool(rv.get("require_last_push_approval")),
                          enforce_admins=bool((full.get("enforce_admins") or {}).get("enabled")))
            else:   # a read-only login sees the required checks only
                st2, b = gh_api("repos/%s/%s/branches/%s" % (repo[0], repo[1], branch), deadline)
                if st2 != "ok":
                    res["branch_protection"] = {"branch": branch, "error": gh_why(st2)}
                    b = None
                if b is not None:
                    rsc = ((b or {}).get("protection") or {}).get("required_status_checks") or {}
                    names |= set(rsc.get("contexts") or []) | set((x or {}).get("context") for x in rsc.get("checks") or [])
                    bp["protected"] = bool((b or {}).get("protected"))
            st3, rules = gh_api("repos/%s/%s/rules/branches/%s" % (repo[0], repo[1], branch), deadline)
            for r in (rules or []) if st3 == "ok" and isinstance(rules, list) else []:
                prm = r.get("parameters") or {}
                if r.get("type") == "required_status_checks":
                    names |= set((x or {}).get("context") for x in prm.get("required_status_checks") or [])
                    bp["strict"] = bool(bp["strict"]) or bool(prm.get("strict_required_status_checks_policy"))
                if r.get("type") == "pull_request":
                    bp.update(reviews_readable=True,
                              required_approving_review_count=max(int(bp["required_approving_review_count"] or 0),
                                                                  int(prm.get("required_approving_review_count") or 0)),
                              dismiss_stale_reviews=bool(bp["dismiss_stale_reviews"]) or bool(prm.get("dismiss_stale_reviews_on_push")),
                              require_last_push_approval=bool(bp["require_last_push_approval"]) or bool(prm.get("require_last_push_approval")))
            if res["branch_protection"] is None:
                bp["required_checks"] = sorted(x for x in names if x)
                bp["requires_both"] = all(j_ in names for j_ in CI_JOBS)
                res["branch_protection"] = bp
        else:
            res["branch_protection"] = {"error": gh_why(st)}
        # D-273 (Amendment 10, Y6): GitHub counts one approval from anyone with write access, so the doctor lists everyone with write,
        # maintain or admin and compares them with the owner and the agent accounts the install recorded
        st4, people = gh_api("repos/%s/%s/collaborators?per_page=100" % repo, deadline)
        wr = {"readable": False, "logins": [], "unexpected": [], "owner_recorded": bool(rec.get("owner_login")), "truncated": False}
        if st4 == "ok" and isinstance(people, list):
            logins = sorted(str(p_.get("login")) for p_ in people if isinstance(p_, dict) and p_.get("login")
                            and any((p_.get("permissions") or {}).get(k) for k in ("admin", "maintain", "push")))
            known = set(x.lower() for x in [rec.get("owner_login")] + list(rec.get("agent_accounts") or []) if isinstance(x, str) and x)
            owner_l = str(rec.get("owner_login") or "").lower()
            non_owner = [x for x in logins if x.lower() != owner_l] if wr["owner_recorded"] else []
            wr.update(readable=True, logins=logins, truncated=len(people) >= 100, non_owner=non_owner,
                      unexpected=[x for x in logins if x.lower() not in known] if wr["owner_recorded"] else [],
                      multiple_agents=len(non_owner) > 1)       # D-283: one agent account can approve another's pull request
        else:
            wr["error"] = gh_why(st4)
        res["writers"] = wr
        # D-283 (Amendment 11, Z6): can GitHub Actions approve pull requests here? (needs an admin login to read)
        stw, perm = gh_api("repos/%s/%s/actions/permissions/workflow" % repo, deadline)
        if stw == "ok" and isinstance(perm, dict) and "can_approve_pull_request_reviews" in perm:
            res["actions_approve"] = {"readable": True, "can_approve": bool(perm.get("can_approve_pull_request_reviews"))}
        else:
            res["actions_approve"] = {"readable": False, "can_approve": None,
                                      "error": gh_why(stw) if stw != "ok" else "GitHub gave an answer the hook could not read"}
    res["disk_check"] = disk_check_status(root)       # D-279
    if res["ci_judge"]:
        res["judge"] = ci_judge(root, rec)
    return res


# D-231 (Amendment 5, L3): in plugin mode /workforce-init records the sha256 of every enforcement file in the repo in a
# baseline under the plugin data folder (out of every agent's reach with the sandbox on). Every Stop compares.
TAMPER_BASELINE = "tamper-baseline.json"
TAMPER_MSG = ("enforcement file changed this session: %s; run /workforce-init --upgrade to restore, or --accept-changes "
              "if you made it")
BASELINE_MISSING = "tamper baseline missing: run /workforce-init --upgrade from your own terminal"   # D-270


def settings_hooks_hash(root):
    try:
        st = json.load(open(os.path.join(root, ".claude", "settings.json"), encoding="utf-8"))
    except Exception:          # D-259 (closed): None differs from a recorded hash, which blocks
        return None
    return hashlib.sha256(json.dumps(st.get("hooks") if isinstance(st, dict) else None, sort_keys=True).encode("utf-8")).hexdigest()


def enforcement_hashes(root, listed):
    """{repo path: sha256 or None (absent)} for the listed files and every file now in .claude/hooks (its log aside)."""
    names = set(listed)
    hd = os.path.join(root, ".claude", "hooks")
    if os.path.isdir(hd):
        for f in os.listdir(hd):
            if not f.endswith(".log") and f != "__pycache__":
                names.add(".claude/hooks/" + f)
    out = {}
    for rel in names:
        p = os.path.join(root, rel)
        try:
            with open(p, "rb") as fh:
                out[rel] = hashlib.sha256(fh.read()).hexdigest()
        except OSError:   # D-270 (closed): an unreadable enforcement file hashes as None, which differs from the baseline and blocks
            out[rel] = "dir" if os.path.isdir(p) else None
    return out


def record_is_new(rec):
    """D-281: the install record is from 2.8.3 or newer (it names the core pack version it was written by). A record that names none counts
    as new: fail closed."""
    v = (rec.get("packs") or {}).get("core") if isinstance(rec.get("packs"), dict) else None
    return True if not v else _ver(v) >= (2, 8, 3)


def tamper_problems(project_dir, gated=True):
    """gated: the turn dispatched an agent (any Task or Agent dispatch, a gate or not). For a plugin-mode record from 2.8.3 or newer (D-281), a baseline file that is missing, or that has
    no entry for this repo, blocks a turn that dispatched an agent (D-270): it is what the tamper check and the runner-config check compare against. A record
    older than 2.8.3 has no baseline yet; it is checked from its first /workforce-init --upgrade."""
    step("the tamper check")
    data = plugin_data_dir()
    if not data:
        return []
    root = repo_top(project_dir)
    needs = gated and install_record(project_dir).get("mode") == "plugin" and record_is_new(install_record(project_dir))
    try:
        base = json.load(open(os.path.join(data, TAMPER_BASELINE), encoding="utf-8")).get(root)
    except FileNotFoundError:   # D-270 (closed): a missing baseline file blocks a gated plugin-mode turn of a 2.8.3 record (BASELINE_MISSING)
        return [BASELINE_MISSING] if needs else []
    except Exception as exc:   # D-259: an unreadable baseline is not "nothing to compare"
        return ["the tamper check could not run (%s): this gate is not passed" % type(exc).__name__]
    if not isinstance(base, dict):
        return [BASELINE_MISSING] if needs else []      # D-281 (closed): the file exists but holds nothing for this repo
    if not isinstance(base.get("files"), dict):
        return []
    want = base["files"]
    have = enforcement_hashes(root, want)
    diff = sorted(rel for rel in set(want) | set(have) if want.get(rel) != have.get(rel))
    if base.get("settings_hooks") and settings_hooks_hash(root) != base["settings_hooks"]:
        diff.append(".claude/settings.json (hooks block)")
    if not diff:
        return []
    return [TAMPER_MSG % (", ".join(diff[:6]) + (" and %d more" % (len(diff) - 6) if len(diff) > 6 else ""))]


# D-218: the cited run tested the change.
TEST_PATH_EXT = (".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".rs", ".java", ".kt", ".cs", ".rb")
VALUE_FLAGS = {"-k", "-m", "-p", "-c", "-o", "-n", "--maxfail", "--rootdir", "--deselect", "-t", "--testNamePattern",
               "--grep", "-g", "--filter", "--reporter"}


TEST_FILE = re.compile(r"(^|/)(tests?|__tests__|spec)/|(^|/)test_[^/]*\.py$|_test\.(py|go)$|\.(test|spec)\.[cm]?[jt]sx?$|Tests?\.(java|kt|cs)$")
NEW_TEST_LINE = re.compile(r"^\s*(async\s+def\s+test_|def\s+test_|func\s+Test|(it|test|describe)\s*\(|@Test\b|#\[test\]|\[(Fact|Test)\])")


def _git(project_dir, *a):
    try:
        p = subprocess.run(["git", "-C", project_dir] + list(a), capture_output=True, text=True, timeout=10)
    except Exception as exc:   # D-259 (closed): a fault: a git that does not run is not 'no change'
        fault("git %s" % (a[0] if a else ""), exc)    # D-259: a git that does not run is not "no change"
        return None
    return p.stdout if p.returncode == 0 else None


def base_ref(project_dir):
    """The branch the change is measured against (D-226): origin/HEAD, else the merge base with the upstream, else
    main, master, trunk or develop."""
    r = (_git(project_dir, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD") or "").strip()
    if r.startswith("refs/remotes/"):
        return r[len("refs/remotes/"):]
    up = (_git(project_dir, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}") or "").strip()
    if up:
        mb = (_git(project_dir, "merge-base", "HEAD", up) or "").strip()
        if mb:
            return mb
    for b in ("main", "master", "trunk", "develop"):
        if _git(project_dir, "rev-parse", "--verify", "--quiet", b) is not None:
            return b
    return None


def changed_files(project_dir):
    """The change under review, read-only (D-218): `git diff --name-only HEAD` plus untracked files; when the work tree
    is clean, the branch's commits against base_ref (D-226). A test file counts only when the change adds a test case
    to it (D-227): touching or renaming the test a gate cites does not make it "the change". None when git is
    unavailable."""
    if _git(project_dir, "rev-parse", "--is-inside-work-tree") is None:
        return None
    untracked = set((_git(project_dir, "ls-files", "--others", "--exclude-standard") or "").split())
    spec = ["HEAD"]
    files = set((_git(project_dir, "diff", "--name-only", "HEAD") or "").split()) | untracked
    if not files:
        base = base_ref(project_dir)
        if base:
            spec = [base + "...HEAD"]
            files = set((_git(project_dir, "diff", "--name-only", base + "...HEAD") or "").split())
    added = {}                 # the lines the change adds, per file, over the whole tree so a rename is seen as one
    if any(TEST_FILE.search(f) for f in files):
        cur = None
        for line in (_git(project_dir, "diff", "-M", "--unified=0", *spec) or "").splitlines():
            if line.startswith("+++ "):
                cur = line[6:] if line.startswith("+++ b/") else None
            elif cur and line.startswith("+"):
                added.setdefault(cur, []).append(line[1:])
    out = set()
    for f in files:
        if not TEST_FILE.search(f):
            out.add(os.path.normpath(f))
            continue
        if f in untracked:
            try:
                lines = open(os.path.join(project_dir, f), encoding="utf-8", errors="replace").read().splitlines()
            except OSError:   # D-270 (closed): an untracked file that cannot be read adds no test lines, so a cited test in it does not touch the change, which blocks
                lines = []
        else:
            lines = added.get(f, [])
        if any(NEW_TEST_LINE.match(l) for l in lines):
            out.add(os.path.normpath(f))
    return out


def _named_test_paths(args, project_dir):
    out, skip = [], False
    for a in args:
        if skip:
            skip = False
            continue
        if a in VALUE_FLAGS:
            skip = True
            continue
        if a.startswith("-") or a == "--":
            continue
        p = os.path.normpath(a.split("::")[0])
        if "/" in a or p.endswith(TEST_PATH_EXT) or os.path.exists(os.path.join(project_dir, p)):
            out.append(p)
    return out


def _import_cands(src_file, project_dir):
    """Repo paths a source file imports (Python `import`/`from`, JS/TS relative `import`/`require`)."""
    try:
        text = open(os.path.join(project_dir, src_file), encoding="utf-8", errors="replace").read()
    except OSError:   # D-270 (closed): no imports found means a cited test does not touch the change, which blocks
        return set()
    here = os.path.dirname(src_file)
    cands = set()
    for m in re.finditer(r"^\s*from\s+(\.*[\w.]*)\s+import\s+([\w, ()*]+)|^\s*import\s+([\w.]+)", text, re.M):
        mod = m.group(1) if m.group(1) is not None else m.group(3)
        dots = len(mod) - len(mod.lstrip("."))
        base = here if dots else ""
        for _ in range(max(dots - 1, 0)):
            base = os.path.dirname(base)
        path = os.path.join(base, mod.lstrip(".").replace(".", "/")) if mod.lstrip(".") else base
        cands |= {path + ".py", os.path.join(path, "__init__.py")}
        for name in re.findall(r"\w+", m.group(2) or ""):
            cands.add(os.path.join(path, name) + ".py")
    for m in re.finditer(r"(?:from\s+|require\(\s*|import\s*\(\s*)['\"](\.{1,2}/[^'\"]+)['\"]", text):
        stem = os.path.normpath(os.path.join(here, m.group(1)))
        cands |= {stem + e for e in ("", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")} | {os.path.join(stem, "index.ts"), os.path.join(stem, "index.js")}
    return {os.path.normpath(c) for c in cands}


def _imports_changed(test_file, changed, project_dir):
    """True when the test imports a changed module, directly or through one re-export (a package `__init__.py` or an
    `index.ts`/`index.js` that imports it; D-226)."""
    cands = _import_cands(test_file, project_dir)
    if cands & changed:
        return True
    for c in cands:
        if os.path.basename(c) in ("__init__.py", "index.ts", "index.js") and os.path.isfile(os.path.join(project_dir, c)):
            if _import_cands(c, project_dir) & changed:
                return True
    return False


def tested_the_change(args, changed, project_dir):
    """True when a run with no named test path ran the suite, or a named path is a changed file, holds one, is a test
    file in a changed file's folder, or imports a changed module (D-218)."""
    named = _named_test_paths(args, project_dir)
    if not named:
        return True
    dirs = {os.path.dirname(c) for c in changed}
    for p in named:
        if p in changed or any(c.startswith(p.rstrip("/") + "/") for c in changed):
            return True
        full = os.path.join(project_dir, p)
        files = [p] if os.path.isfile(full) else []
        if os.path.isdir(full):
            for dp, _dn, fn in os.walk(full):
                files += [os.path.relpath(os.path.join(dp, f), project_dir) for f in fn if f.endswith(TEST_PATH_EXT)]
                if len(files) > 300:
                    break
        for f in files:
            if os.path.dirname(f) in dirs or _imports_changed(f, changed, project_dir):
                return True
    return False


def _return_verdict(text, validates=None):
    """How an earlier return reads in the D-214 note: its last block's verdict, "invalid" when its block does not
    validate (D-219), "no block", or "pending"."""
    if text is None:
        return "pending"
    blocks = FENCE.findall(text)
    if not blocks:
        return "no block"
    if validates is not None and not validates(text):
        return "invalid"
    try:
        return str(json.loads(blocks[-1]).get("verdict") or "no verdict")
    except Exception:          # D-259 (b): a label in the clean line's note
        return "unreadable block"


PLACEHOLDER = re.compile(r"<[^>]*>|\{[^}]*\}|\$\{?[A-Za-z_][A-Za-z0-9_]*\}?|\$[0-9@#?!*$-]|\$")   # D-280: also $1, $@, $#, $?, $$ and a lone $ left by ${1}


def placeholder_verdict_name(ref):
    """True for a verdict-file name that is only a placeholder (`<slug>.verdict.md`, `{slug}.verdict.md`,
    `$slug.verdict.md`) or a bare `.verdict.md`: text about verdict files, not a file (D-215)."""
    base = os.path.basename(ref.strip("'\"").replace("\\", ""))      # D-280: a shell backslash is the character after it
    stem = base[:-len(".verdict.md")] if base.lower().endswith(".verdict.md") else base
    return PLACEHOLDER.sub("", stem) == ""


MAX_STOP_BLOCKS = 3        # D-209: blocks per turn before the failure is put on record instead


def bump_stop_blocks(tpath, payload, turn_key):
    """Count one more blocking Stop for this session and turn in the snapshot file; return the new count,
    or None when the file cannot be written (then the hook keeps blocking; the client's cut-off applies)."""
    sp = _snap_path(tpath)
    try:
        state = json.load(open(sp))
    except Exception:          # D-259 (closed): the count restarts, so the hook keeps blocking
        state = {}
    key = "%s:%s" % (payload.get("session_id") or "", turn_key)
    counts = state.setdefault("stop_blocks", {})
    counts[key] = int(counts.get(key) or 0) + 1
    try:
        json.dump(state, open(sp, "w"))
    except OSError:   # D-270 (closed): None means the count cannot be kept, and the hook keeps blocking
        return None
    return counts[key]


def find_marker_dir(start_dir, project_dir):
    """Same rule as enforce-draft-gate.py: `.br-assets` in start_dir or any ancestor up to (and
    including) project_dir, bounded to 25 hops so a session rooted somewhere unexpected can never
    make this loop indefinitely."""
    d = os.path.realpath(start_dir)
    root = os.path.realpath(project_dir) if project_dir else None
    hops = 0
    while True:
        if os.path.isfile(os.path.join(d, ".br-assets")):
            return d
        if root and d == root:
            return None
        parent = os.path.dirname(d)
        if parent == d or hops >= 25:
            return None
        d = parent
        hops += 1


def _read_output_file_text(path):
    """The last assistant text in a task's own output file (D-65). The file may be a JSONL
    transcript in the same shape as the main one (assistant `message.content` text blocks) or
    plain text; None on anything unreadable rather than raise (the caller then has no returned text, which is a problem line)."""
    try:
        content = open(path, encoding="utf-8", errors="replace").read()
    except Exception:  # D-259 (closed): no text from the gate means no valid verdict, which blocks
        return None
    last_text, parsed_any, cut_assistant = None, False, False
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:  # D-286 (closed): an unreadable line that is an assistant message may be the gate's final text: no text is taken from the file
            if re.search(r'"type"\s*:\s*"assistant"', line):
                cut_assistant = True
            continue
        if not isinstance(ev, dict):
            continue           # D-270: JSON that is not an object is not an event
        parsed_any = True
        if ev.get("type") == "assistant":
            for blk in ((ev.get("message") or {}).get("content") or []):
                if isinstance(blk, dict) and blk.get("type") == "text":
                    last_text = blk.get("text")
    if cut_assistant:
        return None            # D-286: the last assistant line is unreadable, so the text of an earlier turn must not stand as the gate's answer
    if parsed_any:
        return last_text
    return content or None


NOTICE_TAG = re.compile(r"<(tool-use-id|status|result|summary|output-file)>(.*?)</\1>", re.S)


def _notice_text(ev):
    """The `<task-notification>` text a transcript event carries as a stored completion notice, or
    None (D-164): an `attachment` of type `queued_command`, or a `user` event from a task notice."""
    att = ev.get("attachment")
    if ev.get("type") == "attachment" and isinstance(att, dict) and att.get("type") == "queued_command":
        text = att.get("prompt")
        if isinstance(text, str) and (att.get("commandMode") == "task-notification"
                                      or text.lstrip().startswith("<task-notification>")):
            return text
    if ev.get("type") == "user":
        content = (ev.get("message") or {}).get("content")
        if isinstance(content, list):
            content = "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
        if isinstance(content, str) and ((ev.get("origin") or {}).get("kind") == "task-notification"
                                         or content.lstrip().startswith("<task-notification>")):
            return content
    return None


def _parse_notice(text):
    """{tool-use-id, status, result, summary, output-file} from a stored notice's tags (first of each)."""
    out = {}
    for tag, val in NOTICE_TAG.findall(text or ""):
        out.setdefault(tag, val.strip())
    return out


def _carries_tool_result(ev):
    """True if the event's message content holds a `tool_result` block (D-112)."""
    content = (ev.get("message") or {}).get("content")
    return isinstance(content, list) and any(
        isinstance(b, dict) and b.get("type") == "tool_result" for b in content)


SNAP_SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".tox", ".mypy_cache"}
SNAP_LIMIT = 20000         # entries one walk covers before it gives up (D-279: a skip is announced on the Stop, never silent)
DISK_SKIP = {"reason": None}   # D-279: why the last disk_snapshot() could not check, or None


def _snap_candidates(root):
    """D-279 (Amendment 11, Z2): the files the disk check hashes, without walking a whole large tree. In a git work tree the candidates
    come from `git ls-files` (tracked, and untracked but not ignored: where a script-written verdict file shows up), plus a bounded walk
    of the folders marked with .br-assets (which may hold git-ignored files). Outside git, or if git fails, the whole tree is walked up
    to SNAP_LIMIT entries. Returns [relative path] or None, with DISK_SKIP["reason"] set when it cannot. Files in git-ignored folders
    outside marked folders are out of scope by design; the hooks README says so."""
    names, walked_marked = None, []
    try:
        p = subprocess.run(["git", "-C", root, "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                           capture_output=True, timeout=max(1, min(20, time_left())))
        if p.returncode == 0:
            names = sorted(set(x.decode("utf-8", "replace") for x in p.stdout.split(b"\0") if x))
    except subprocess.TimeoutExpired:   # D-279 (closed): git is too slow here; the bounded walk below runs, and says so if it cannot finish
        names = None
    except OSError:                     # D-279 (closed): no git here; the bounded walk below runs, and says so if it cannot finish
        names = None
    out, seen = set(), 0
    if names is not None:
        marked = sorted(os.path.dirname(x) for x in names if os.path.basename(x) == ".br-assets")
        in_marked = lambda rel: any(m == "" or rel == m or rel.startswith(m + "/") for m in marked)
        for rel in names:
            fl = rel.lower()
            if fl.endswith(".verdict.md") or (fl.endswith(".md") and not fl.endswith(".draft.md") and in_marked(rel)):
                out.add(rel)
        for m in marked:        # git-ignored files inside a marked folder are walked
            base = os.path.join(root, m) if m else root
            for dp, ds, fs in os.walk(base):
                ds[:] = sorted(d for d in ds if d not in SNAP_SKIP)
                seen += len(fs) + len(ds)
                if seen > SNAP_LIMIT:
                    DISK_SKIP["reason"] = "a marked folder holds more than %d entries" % SNAP_LIMIT
                    return None
                for f in fs:
                    fl = f.lower()
                    if fl.endswith(".verdict.md") or (fl.endswith(".md") and not fl.endswith(".draft.md")):
                        out.add(os.path.relpath(os.path.join(dp, f), root))
        return sorted(out)
    marked_roots = []
    for dp, ds, fs in os.walk(root):
        ds[:] = sorted(d for d in ds if d not in SNAP_SKIP)
        seen += len(fs) + len(ds)
        if seen > SNAP_LIMIT:
            DISK_SKIP["reason"] = "no git to list the files, and the tree holds more than %d entries" % SNAP_LIMIT
            return None
        if ".br-assets" in fs:
            marked_roots.append(dp)
        marked = any(dp == m or dp.startswith(m + os.sep) for m in marked_roots)
        for f in fs:
            fl = f.lower()
            if fl.endswith(".verdict.md") or (marked and fl.endswith(".md") and not fl.endswith(".draft.md")):
                out.add(os.path.relpath(os.path.join(dp, f), root))
    return sorted(out)


def disk_snapshot(project_dir):
    """{relative path: sha256} for every *.verdict.md (any case) and every plain .md under a folder marked with .br-assets (D-190).
    None when it cannot be taken, with DISK_SKIP["reason"] saying why (D-279: the Stop then says the check was skipped)."""
    step("the disk check")
    import hashlib
    DISK_SKIP["reason"] = None
    root = os.path.realpath(project_dir)
    cands = _snap_candidates(root)
    if cands is None:
        return None
    out = {}
    for rel in cands:
        fp = os.path.join(root, rel)
        try:
            out[rel] = hashlib.sha256(open(fp, "rb").read()).hexdigest()
        except FileNotFoundError:   # D-279 (normal): listed by git but gone from the disk, so no file stands
            continue
        except OSError as exc:   # D-270 (closed): an unreadable verdict or marked file is a fault
            fault("the disk check of %s (it cannot be read)" % rel, exc)   # D-270: a gate input that cannot be read is not verified
    return out


def _snap_path(tpath):
    return (tpath[:-len(".jsonl")] if tpath.endswith(".jsonl") else tpath) + ".br-snapshot.json"


def snapshot_mode(event, payload):
    """UserPromptSubmit: record the turn-start snapshot. PostToolUse (Bash): record what that call changed."""
    tpath = payload.get("transcript_path")
    if not tpath:
        return 0
    project_dir = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())
    cur = disk_snapshot(project_dir)
    if cur is None:
        return 0
    sp = _snap_path(tpath)
    if event == "turn-start":
        state = {"turn_start": cur, "last": cur, "after_bash": []}
    else:
        try:
            state = json.load(open(sp))
        except Exception:      # D-259 (b): snapshot mode only records; the Stop check uses its fallback baseline
            return 0      # no turn-start record: the Stop check uses its fallback baseline
        last = state.get("last") or {}
        changed = sorted(k for k in cur if last.get(k) != cur[k])
        if changed:
            state.setdefault("after_bash", []).append({"tool_use_id": payload.get("tool_use_id"), "changed": changed})
        state["last"] = cur
    try:
        json.dump(state, open(sp, "w"))
    except OSError:   # D-270 (closed): no snapshot written, so the Stop check uses its fallback baseline, which counts unknown files as changed
        pass
    return 0


def _fallback_baseline(project_dir, cur, turn_ts):
    """Files git reports clean, plus files older than the turn's first user message (D-190 fallback)."""
    base = {}
    try:
        p = subprocess.run(["git", "-C", project_dir, "status", "--porcelain", "--untracked-files=all", "--", "."],
                           capture_output=True, text=True, timeout=20)
        if p.returncode == 0:
            dirty = {l[3:].strip().strip('"') for l in p.stdout.splitlines() if len(l) > 3}
            tracked = subprocess.run(["git", "-C", project_dir, "ls-files"], capture_output=True, text=True, timeout=20)
            for rel in tracked.stdout.splitlines():
                if rel in cur and rel not in dirty:
                    base[rel] = cur[rel]
    except Exception:          # D-259 (closed): a file left out of the baseline counts as changed, so it is checked
        pass
    if turn_ts:
        try:
            from datetime import datetime
            t0 = datetime.fromisoformat(turn_ts.replace("Z", "+00:00")).timestamp()
            for rel, sha in cur.items():
                if os.path.getmtime(os.path.join(project_dir, rel)) < t0:
                    base[rel] = sha
        except Exception:      # D-259 (closed): a file left out of the baseline counts as changed, so it is checked
            pass
    return base


_STOP = {"payload": None}      # the Stop payload main() read, for the crash guard


def _hook_frame(exc):
    """The innermost function of this file on exc's traceback, for the crash message."""
    name = "main"
    try:
        here = os.path.abspath(__file__)
        for fr in traceback.extract_tb(exc.__traceback__):
            if os.path.abspath(fr.filename) == here:
                name = fr.name
    except Exception:   # D-270 (b): the crash message names 'main' when the traceback cannot be read
        pass
    return name


def _crash_turn_key(tpath):
    """A key for the turn, to bound the crash block: the timestamp of the last real user line (the main loop's rule,
    written without the helpers that may be what crashed)."""
    key = "crash"
    try:
        for idx, line in enumerate(open(tpath, encoding="utf-8", errors="replace").read().splitlines()):
            if "task-notification" in line:
                continue
            try:
                ev = json.loads(line)
            except Exception:   # D-270 (b): the key that bounds the crash block; an unreadable line is skipped, and the key falls back to 'crash'
                continue
            if not isinstance(ev, dict) or ev.get("type") != "user" or ev.get("isSynthetic") or ev.get("isMeta"):
                continue
            c = ev.get("message", {}).get("content") if isinstance(ev.get("message"), dict) else None
            if isinstance(c, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
                continue
            key = "crash:%s" % (ev.get("timestamp") or "idx%d" % idx)
    except Exception:   # D-270 (b): the key that bounds the crash block; an unreadable line is skipped, and the key falls back to 'crash'
        pass
    return key


def stop_closed(payload, key, msg, bound="count"):
    """D-268: a failure that makes this turn not gated. Prints one block, bounded as the problem blocks are: the first
    MAX_STOP_BLOCKS Stops of a turn block, then a loud "Verdict check FAILED" systemMessage. bound="count" keeps the count
    beside the transcript; bound="active" (no transcript to keep it in) ends loudly on a Stop that already arrives with
    stop_hook_active. When the count cannot be kept, the same rule applies."""
    payload = payload if isinstance(payload, dict) else {}
    n = None
    if bound == "count":
        try:
            tpath = payload.get("transcript_path")
            if isinstance(tpath, str) and tpath:
                n = bump_stop_blocks(tpath, payload, key)
        except Exception:   # D-270 (closed): the count is unknown, so stop_hook_active bounds the block
            n = None
    spent = (n > MAX_STOP_BLOCKS) if n is not None else bool(payload.get("stop_hook_active"))
    if spent:
        print(json.dumps({"systemMessage": "Verdict check FAILED and was not fixed: " + msg}))
    else:
        print(json.dumps({"decision": "block", "reason": "This turn cannot be treated as gated:\n  - " + msg
                          + "\nStop and report it to the human with the reason above; do not disable the check."}))


def main():
    """D-268: the one guard. Any error that escapes the checks ends in a block (or a systemMessage), never silently.
    D-278: the hook's own deadline is armed here; reaching it is the same kind of end (see BudgetExceeded)."""
    snapshot = len(sys.argv) > 2 and sys.argv[2] == "--snapshot"
    if not (len(sys.argv) > 1 and sys.argv[1] == "--ci-status"):
        _arm_budget(snapshot)
    try:
        return _main()
    except BudgetExceeded as late:   # D-278: the deadline fired. Disarm first so the answer below cannot be cut off
        _disarm_budget()
        try:
            what = str(late) or "the verdict check"
            if snapshot:
                print(json.dumps({"systemMessage": "Verdict check: the turn snapshot ran out of time (%s); the Stop check falls back to counting "
                                  "files it cannot compare as changed." % what}))
                return 0
            payload = _STOP["payload"] or {}
            tp = payload.get("transcript_path") if isinstance(payload, dict) else None
            stop_closed(payload, _crash_turn_key(tp) if isinstance(tp, str) and tp else "crash",
                        "the verdict check ran out of time (%s): this turn is not gated; report it" % what,
                        "count" if isinstance(tp, str) and tp else "active")
        except Exception:      # D-278 (closed): the answer itself failed: a plain block
            print(json.dumps({"decision": "block", "reason": "This turn cannot be treated as gated: the verdict check ran out of time; report it."}))
        return 0
    except Exception as exc:   # D-270 (closed): the guard: an uncaught error is a block (or a systemMessage once bounded); a failing guard is a plain block
        _disarm_budget()
        try:
            where = _hook_frame(exc)
            if len(sys.argv) > 2 and sys.argv[2] == "--snapshot":
                print(json.dumps({"systemMessage": "Verdict check: the turn snapshot could not be recorded (%s at %s); the Stop check "
                                  "falls back to counting files it cannot compare as changed." % (type(exc).__name__, where)}))
                return 0
            if len(sys.argv) > 1 and sys.argv[1] == "--ci-status":
                print(json.dumps({"error": "the CI judge status could not run (%s): nothing here is passed" % type(exc).__name__}))
                return 1
            payload = _STOP["payload"] or {}
            tp = payload.get("transcript_path") if isinstance(payload, dict) else None
            stop_closed(payload, _crash_turn_key(tp) if isinstance(tp, str) and tp else "crash",
                        "the verdict check crashed (%s at %s): this turn is not gated; report it" % (type(exc).__name__, where),
                        "count" if isinstance(tp, str) and tp else "active")
        except Exception:      # D-270 (closed): the guard itself failed: say so, plainly, with a block
            print(json.dumps({"decision": "block", "reason": "This turn cannot be treated as gated: the verdict check crashed; report it."}))
        return 0
    finally:
        _disarm_budget()


def _main():
    if len(sys.argv) < 2:
        return 0
    if len(sys.argv) > 1 and sys.argv[1] == "--ci-status":        # D-253: the doctor's read of the CI judge
        try:
            print(json.dumps(ci_status(os.path.realpath(sys.argv[2] if len(sys.argv) > 2 else
                                                        os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())), indent=2, sort_keys=True))
        except Exception as exc:   # D-259: the doctor reports this as a FAIL, never as passing
            print(json.dumps({"error": "the CI judge status could not run (%s): nothing here is passed" % type(exc).__name__}))
            return 1
        return 0
    validator = sys.argv[1]

    raw = sys.stdin.read()
    if not raw.strip():
        return 0               # D-268: nothing was sent, so this is not a hook call at all
    snapshot = len(sys.argv) > 3 and sys.argv[2] == "--snapshot"
    try:
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("the payload is not a JSON object")
    except Exception as exc:   # D-270 (closed): an unreadable Stop payload blocks (a snapshot call stays silent: it only records)
        if snapshot:
            return 0           # the snapshot recorder only records; the Stop check has its own fallback baseline
        stop_closed({"stop_hook_active": bool(re.search(r'"stop_hook_active"\s*:\s*true', raw))}, "bad-payload",
                    "the verdict check could not read the hook payload (%s): this turn is not gated; report it" % type(exc).__name__, "active")
        return 0
    _STOP["payload"] = payload

    if snapshot:
        return snapshot_mode(sys.argv[3], payload)

    # D-209: a Stop with `stop_hook_active` is judged too; the block count below bounds the loop.

    tpath = payload.get("transcript_path")
    if not tpath or not os.path.isfile(tpath):
        if payload.get("hook_event_name") == "Stop" or "stop_hook_active" in payload or tpath:   # D-268: a Stop is in progress
            stop_closed(payload, "no-transcript", "the verdict check has no transcript to read (%s): this turn is not gated; report it"
                        % ("no transcript path was given" if not tpath else "the transcript file does not exist"), "active")
        return 0
    try:
        lines = open(tpath, encoding="utf-8", errors="replace").read().splitlines()
    except Exception as exc:   # D-259: a transcript that cannot be read is not a turn with nothing to judge
        n_blocks = bump_stop_blocks(tpath, payload, "unreadable-transcript")
        msg = "the verdict check could not read the transcript (%s): this turn is not gated" % type(exc).__name__
        if (n_blocks > MAX_STOP_BLOCKS) if n_blocks is not None else bool(payload.get("stop_hook_active")):   # D-286 (X9): no count kept, so a Stop already bounced once ends loudly
            print(json.dumps({"systemMessage": "Verdict check FAILED and was not fixed: " + msg}))
        else:
            print(json.dumps({"decision": "block", "reason": "This turn cannot be treated as gated. Fix and re-emit:\n  - "
                              + msg + "\nIf you believe this block is wrong, stop and report it to the human with the reason "
                              "above; do not disable the check."}))
        return 0

    # TURN BOUNDARY: `transcript_path` is the whole SESSION transcript,
    # cumulative across every turn — confirmed live downstream (a status-report turn that only
    # mentioned `code-reviewer` in prose got blocked) and traced to source: nothing here bounded
    # the scan, so a gate dispatched in an EARLIER turn whose verdict was never found valid stayed
    # in `dispatched` and got re-flagged on every LATER Stop-hook firing, including turns that
    # never touched that gate. Bound the scan to the current turn: everything from the most
    # recent REAL (non-synthetic) user message onward. A hook's own "Stop hook feedback"
    # continuation is marked `isSynthetic: true` and does NOT start a new turn — the user is still
    # waiting on the one exchange the hook bounced back for revision. Fail open (scan everything,
    # today's behaviour) if no real user message is found at all.
    # A tool result is ALSO stored as a `type: "user"` event (D-112, audit F1: measured on a live
    # `claude -p` transcript), so it never starts a turn; nor does an `isMeta` event. Without this the
    # turn began at the LAST tool result, after every dispatch, and the hook never saw a gate.
    turn_start, turn_ts = 0, None
    for idx, line in enumerate(lines):
        line_s = line.strip()
        if not line_s:
            continue
        try:
            ev = json.loads(line_s)
        except Exception:  # D-259 (b): a line that is not JSON is not an event (the current turn's lines are checked below, D-270)
            continue
        if not isinstance(ev, dict):
            continue
        if ev.get("type") == "user" and not ev.get("isSynthetic") and not ev.get("isMeta") \
                and not _carries_tool_result(ev) and _notice_text(ev) is None:   # a task notice is not the user (D-164)
            turn_start = idx
            turn_ts = ev.get("timestamp")
    session_lines = lines      # the whole session, for the executed-command check (D-146)
    lines = lines[turn_start:]

    project_dir = os.path.realpath(
        os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())
    global GATES, SEATS
    del FAULTS[:]
    ROSTER_FAULT[0] = None
    GATES, SEATS = load_roster(validator, project_dir)
    if not GATES and not ROSTER_FAULT[0]:
        return 0               # an empty roster that was read: nothing is a gate

    dispatched, results, task_idx = {}, {}, {}
    all_dispatched = {}        # tool_use_id -> slug, EVERY Task/Agent dispatch (R22 author check)
    agent_ids = {}             # tool_use_id -> the subagent's agentId (toolUseResult.agentId)
    notifications = {}         # tool_use_id -> {"summary": str|None, "output_file": str|None}
    draft_writes = []          # [(index, abs_path)] — DRAFT writes under a marked directory
    claims_gate_at = []        # [index, ...] — every claims-gate dispatch, in transcript order
    md_writes = []             # [(index, abs_path, content)] — every Write of a *.md file
    verdict_file_writes = []   # [(index, abs_path, content-or-None)] — Write/Edit/MultiEdit of *.verdict.md (R2)
    marked_md_writes = []      # [(index, abs_path)] — Write/Edit/MultiEdit of a plain .md under a marked dir (R2)
    bash_verdict_refs = []     # [raw path] — *.verdict.md named in a Bash command this turn (D-175)
    bash_cmds = []             # every Bash command of the turn, main session and subagents (D-190)
    send_msgs = []             # [(index, tool_use_id, to)] — every SendMessage call of the turn (D-208)
    resumed_aid = {}           # SendMessage tool_use_id -> toolUseResult.resumedAgentId (D-208)
    ladder_ids = set()         # D-237: completion-auditor dispatches marked ladder-only
    bad_call_lines = []        # D-270: 1-based transcript line numbers of unreadable lines that look like a dispatch or a result
    bad_sub_lines = []         # D-286: the same for a dispatched agent's own transcript: (agentId, 1-based line number)
    denied_ids = set()         # D-284 (Z7): a Write or Edit whose tool result is an error did not happen (the PreToolUse hook denied it, or it failed)
    for _l in lines:
        if '"is_error"' not in _l:
            continue
        try:
            _e = json.loads(_l)
        except Exception:      # D-284 (closed): the main loop below reports an unreadable line that looks like a result, by its number
            continue
        _c = (_e.get("message") or {}).get("content") if isinstance(_e, dict) and isinstance(_e.get("message"), dict) else None
        for _b in _c if isinstance(_c, list) else []:
            if isinstance(_b, dict) and _b.get("type") == "tool_result" and _b.get("is_error") is True and _b.get("tool_use_id"):
                denied_ids.add(_b["tool_use_id"])
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:  # D-270: a line of this turn that is not JSON but looks like a dispatch or a result blocks, by its number
            if CALL_LINE.search(line):
                bad_call_lines.append(turn_start + idx + 1)
            continue
        if not isinstance(ev, dict):
            continue           # JSON that is not an object is not an event
        if ev.get("type") == "system" and ev.get("subtype") == "task_notification":
            tuid = ev.get("tool_use_id")
            if tuid:
                notifications[tuid] = {"summary": ev.get("summary"), "output_file": ev.get("output_file")}
        ntext = _notice_text(ev)
        if ntext:
            n = _parse_notice(ntext)
            if n.get("tool-use-id"):
                notifications[n["tool-use-id"]] = {"summary": n.get("summary"), "output_file": n.get("output-file"),
                                                   "result": n.get("result"), "status": n.get("status")}
        for blk in ((ev.get("message") or {}).get("content") or []):
            if not isinstance(blk, dict):
                continue
            if blk.get("type") == "tool_use" and blk.get("name") in ("Task", "Agent"):
                # subagent_type is "<plugin>:<slug>" for a plugin agent, or a bare slug
                slug = str((blk.get("input") or {}).get("subagent_type") or "").split(":")[-1].strip()
                if ladder_only(slug, blk.get("input")):
                    ladder_ids.add(blk.get("id"))
                    continue           # D-237: a ladder run owes no verdict, and none it returns counts
                all_dispatched[blk.get("id")] = slug
                if slug in GATES:
                    dispatched[blk.get("id")] = slug
                    task_idx[blk.get("id")] = idx
                if slug == "claims-gate":
                    claims_gate_at.append(idx)
            elif blk.get("type") == "tool_use" and blk.get("name") == "Bash":
                bash_verdict_refs.extend(VERDICT_REF.findall(str((blk.get("input") or {}).get("command") or "")))
                bash_cmds.append(str((blk.get("input") or {}).get("command") or ""))
            elif blk.get("type") == "tool_use" and blk.get("name") == "SendMessage":
                send_msgs.append((idx, blk.get("id"), str((blk.get("input") or {}).get("to") or "").strip()))
            elif blk.get("type") == "tool_use" and blk.get("name") in ("Write", "Edit", "MultiEdit"):
                if blk.get("id") in denied_ids:
                    continue           # D-284: it did not happen, so it is neither a draft nor a verdict file nor a marked asset written
                try:
                    inp = blk.get("input") or {}
                    fp = inp.get("file_path") or ""
                    if fp.endswith(".md"):
                        ap = os.path.realpath(fp if os.path.isabs(fp) else os.path.join(project_dir, fp))
                        if ap.endswith(".verdict.md"):
                            verdict_file_writes.append(
                                (idx, ap, inp.get("content") if blk.get("name") == "Write" else None))
                        elif not ap.endswith(".DRAFT.md") and find_marker_dir(os.path.dirname(ap), project_dir):
                            marked_md_writes.append((idx, ap))
                    if blk.get("name") != "Write":
                        continue
                    if fp.endswith(".DRAFT.md"):
                        abs_path = fp if os.path.isabs(fp) else os.path.join(project_dir, fp)
                        abs_path = os.path.realpath(abs_path)
                        if find_marker_dir(os.path.dirname(abs_path), project_dir):
                            draft_writes.append((idx, abs_path))
                    if fp.endswith(".md"):
                        abs_path = fp if os.path.isabs(fp) else os.path.join(project_dir, fp)
                        abs_path = os.path.realpath(abs_path)
                        md_writes.append((idx, abs_path, inp.get("content") or ""))
                except Exception as exc:   # D-259 (closed): a fault: the asset write check of a path that cannot be resolved
                    fault("the asset write check of %s" % str(fp)[:120], exc)   # D-259
            elif blk.get("type") == "tool_result":
                c = blk.get("content")
                if isinstance(c, list):
                    c = "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
                results[blk.get("tool_use_id")] = c if isinstance(c, str) else ""
                tur = ev.get("toolUseResult")
                if isinstance(tur, dict) and tur.get("agentId"):
                    agent_ids[blk.get("tool_use_id")] = str(tur.get("agentId"))
                if isinstance(tur, dict) and tur.get("resumedAgentId"):
                    resumed_aid[blk.get("tool_use_id")] = str(tur.get("resumedAgentId"))

    # D-208: which agent each SendMessage of this turn resumed. The agentId -> slug map comes from every
    # Agent/Task dispatch in the session (a gate dispatched in an earlier turn may be resumed in this one).
    slug_by_aid, aid_by_name, _sess_tu = {}, {}, {}
    # D-219: every return of each agent in the session, so a chain names returns from earlier turns too.
    _sess_ret = []             # [(session index, tool_use_id, agentId or `to`, is_resume)]
    _sess_text, _sess_notice, _sess_sm = {}, {}, {}
    for s_idx, sl in enumerate(session_lines):
        try:
            sev = json.loads(sl)
        except Exception:  # D-259 (b): a line that is not JSON is not an event (this turn's lines are checked, D-270)
            continue
        if not isinstance(sev, dict):
            continue
        ntext_ = _notice_text(sev)
        if ntext_:
            n_ = _parse_notice(ntext_)
            if n_.get("tool-use-id") and (n_.get("result") or "").strip():
                _sess_notice[n_["tool-use-id"]] = n_["result"]
        cb = (sev.get("message") or {}).get("content")
        for b in cb if isinstance(cb, list) else []:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use" and b.get("name") in ("Task", "Agent"):
                inp = b.get("input") or {}
                if ladder_only(str(inp.get("subagent_type") or "").split(":")[-1].strip(), inp):
                    continue           # D-237: a ladder-only agent is not a gate when resumed either
                _sess_tu[b.get("id")] = (str(inp.get("subagent_type") or "").split(":")[-1].strip(),
                                         str(inp.get("name") or "").strip())
            elif b.get("type") == "tool_use" and b.get("name") == "SendMessage":
                _sess_sm[b.get("id")] = (s_idx, str((b.get("input") or {}).get("to") or "").strip())
            elif b.get("type") == "tool_result":
                c_ = b.get("content")
                if isinstance(c_, list):
                    c_ = "\n".join(x.get("text", "") for x in c_ if isinstance(x, dict))
                _sess_text[b.get("tool_use_id")] = c_ if isinstance(c_, str) else ""
                tur = sev.get("toolUseResult")
                if b.get("tool_use_id") in _sess_tu and isinstance(tur, dict) and tur.get("agentId"):
                    slug_, name_ = _sess_tu[b.get("tool_use_id")]
                    slug_by_aid[str(tur["agentId"])] = slug_
                    if name_:
                        aid_by_name[name_] = str(tur["agentId"])
                    _sess_ret.append((s_idx, b.get("tool_use_id"), str(tur["agentId"]), False))
                elif b.get("tool_use_id") in _sess_sm:
                    who = (tur or {}).get("resumedAgentId") if isinstance(tur, dict) else None
                    _sess_ret.append((s_idx, b.get("tool_use_id"), str(who or _sess_sm[b.get("tool_use_id")][1]), True))

    def earlier_returns(aid):
        """The texts of an agent's returns before this turn (D-219), oldest first; None for one with no text."""
        out_ = []
        for s_idx, tid, who, is_res in _sess_ret:
            if s_idx >= turn_start or (who != aid and aid_by_name.get(who) != aid):
                continue
            text_ = _sess_notice.get(tid) or _sess_text.get(tid) or ""
            if text_.startswith(STUB_PREFIX) or (is_res and not FENCE.search(text_)):
                text_ = _sess_notice.get(tid)
            out_.append(text_)
        return out_
    resumes = {}               # agentId -> [SendMessage tool_use_id, ...] in transcript order (D-208)
    resume_slug = {}           # SendMessage tool_use_id -> the resumed agent's slug
    for _i, sm_id, to in sorted(send_msgs, key=lambda x: x[0]):
        aid = resumed_aid.get(sm_id)
        if not aid:
            # No resumedAgentId: count it only if `to` names a known agent and its reply holds a block.
            cand = to if to in slug_by_aid else aid_by_name.get(to)
            if cand and FENCE.search(results.get(sm_id) or ""):
                aid = cand
        if aid and aid in slug_by_aid:
            resumes.setdefault(aid, []).append(sm_id)
            resume_slug[sm_id] = slug_by_aid[aid]

    last_error = {"msg": ""}   # the validator's first error from the latest validates() call (2.3.3: say why a gate's text failed)

    def validates(text):
        """Run validate_verdict.py over `text`; True if it contains at least one valid block. Keeps the
        validator's first error in last_error so a block message says WHY (no block vs a bad block)."""
        step("the validator")
        tmp = None
        last_error["msg"] = ""
        try:
            fd, tmp = tempfile.mkstemp(suffix=".md")
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
            p = subprocess.run([sys.executable, "-I", validator, tmp, "--require", "--json"],
                               capture_output=True, text=True, timeout=max(1, min(30, time_left())))      # D-278: the time that is left, not a fixed 30 s
            if p.returncode != 0:
                try:
                    errs = json.loads(p.stdout or "{}").get("errors") or []
                    last_error["msg"] = ("no ```verdict block in the returned text" if p.returncode == 3
                                         else str(errs[0]) if errs else "validator rc=%d" % p.returncode)
                except Exception:  # D-259 (closed): the validator already returned non-zero
                    last_error["msg"] = "validator rc=%d" % p.returncode
            return p.returncode == 0
        except Exception:  # D-259 (closed): not validated, which blocks
            return False       # fail-closed on THIS lookup only; caller still tries other locations
        finally:
            if tmp and os.path.exists(tmp):
                try:
                    os.unlink(tmp)
                except Exception:  # D-259 (b): removing a temp file
                    pass

    problems = []
    validated = []             # [(slug, text, agentId or None)] — every gate text or file content that validated (D-146)

    def gate_return(tuid, resume):
        """(text, location, problem) for one dispatch or one SendMessage resume. (None, None, None): the
        result never landed, not this hook's call."""
        tool_out = results.get(tuid)
        # A resume's own tool_result is "Resuming agent ..." (no block): its text comes in a notice (D-208).
        is_stub = isinstance(tool_out, str) and (tool_out.startswith(STUB_PREFIX)
                                                 or (resume and not FENCE.search(tool_out)))
        note = notifications.get(tuid)
        if note:
            summary = (note.get("summary") or "").strip()
            if (note.get("result") or "").strip():
                return note["result"], "task notice result", None
            elif "result" in note and note.get("status") and note["status"] != "completed" \
                    and not (note.get("output_file") and os.path.isfile(note["output_file"])):
                return None, None, "gate seat ended with status %s and returned no text" % note["status"]
            elif summary and "result" not in note:
                return note.get("summary"), "task_notification summary", None
            else:
                out_file = note.get("output_file")
                if out_file and os.path.isfile(out_file):
                    text = _read_output_file_text(out_file)
                    if text:
                        return text, "task_notification output_file (%s)" % out_file, None
        if tool_out is None:
            return None, None, None   # still running, or the result never landed — not this hook's call
        if is_stub:
            # Backgrounded dispatch (or a resume), no completed notification yet (D-65, D-208):
            # a still-running gate is not the same as one whose text failed to validate.
            return None, None, "gate seat still running; wait for its result before ending the turn"
        return tool_out, ("SendMessage reply" if resume else "inline ```verdict block"), None

    # D-208: each gate agent is one chain — its dispatch in this turn (if any), then every SendMessage
    # resume of it in this turn — judged on the latest return that carries a ```verdict block.
    chains = []                # [(slug, [(tool_use_id, is_resume), ...], index the chain starts at)]
    for tuid, slug in sorted(dispatched.items(), key=lambda kv: str(kv[0])):
        chain = [(tuid, False)] + [(sm, True) for sm in resumes.pop(agent_ids.get(tuid), [])]
        chains.append((slug, chain, task_idx.get(tuid, -1), agent_ids.get(tuid)))
    for aid, sms in sorted(resumes.items()):
        slug = slug_by_aid.get(aid)
        if slug in GATES:      # a gate dispatched in an earlier turn, resumed in this one
            sm_idx = min(i for i, sm, _t in send_msgs if sm in sms)
            chains.append((slug, [(sm, True) for sm in sms], sm_idx, aid))
    judged = set()             # slugs judged this turn (the W-09 count)
    extra_notes = set()        # D-218: "changed-file check skipped: no git"
    disk_note = None           # D-279: set when the disk check had to skip
    ci_pending = set()         # D-252: a quality PASS whose CI judge is still running or could not be read
    chain_notes = []           # D-214: "<slug>: latest of N returns; earlier: <verdicts>"

    # Check 1: every dispatched gate's verdict validates — inline (2.0.0), or in a file it wrote
    # (D-57, 2.1.0): council/<slug>.verdict.md for any GATES member dispatched as a seat, or
    # <name>.verdict.md beside <name>.DRAFT.md for claims-gate specifically.
    for slug, chain, t_idx, chain_aid in chains:
        judged.add(slug)
        rets = [gate_return(t, r) for t, r in chain]
        if rets[-1][0] is None:
            if rets[-1][2]:
                problems.append("%s: %s" % (slug, rets[-1][2]))
            continue          # the latest return is not in yet (or never landed): not judged on an older one
        with_block = [i for i, r in enumerate(rets) if r[0] is not None and FENCE.search(r[0])]
        j = with_block[-1] if with_block else len(rets) - 1
        out, out_location, _p = rets[j]
        before = earlier_returns(chain_aid) if chain_aid and chain[0][1] else []   # D-219: a chain that starts with a resume
        if len(chain) > 1:
            out_location += " (latest of %d returns)" % len(chain)
        out_ok = validates(out)
        saved_err = last_error["msg"]
        if len(before) + len(chain) > 1:
            # D-214, D-219: the earlier returns (earlier turns too) stay on record; an invalid block is "invalid"
            earlier = list(before) + [r[0] for i, r in enumerate(rets) if i != j]
            chain_notes.append("%s: latest of %d returns; earlier: %s" % (
                slug, len(before) + len(chain), ", ".join(_return_verdict(x, validates) for x in earlier)))
        last_error["msg"] = saved_err

        if out_ok:
            validated.append((slug, out, chain_aid))
            continue

        locations_checked = ["%s (%s)" % (out_location, last_error["msg"][:160]) if last_error["msg"] else out_location]
        found_valid = False

        seat_path_suffix = os.path.join("council", "%s.verdict.md" % slug)
        for w_idx, abs_path, content in md_writes:
            if w_idx < t_idx:
                continue
            if abs_path.endswith(seat_path_suffix):
                locations_checked.append(os.path.relpath(abs_path, project_dir))
                if validates(content):
                    validated.append((slug, content, None))
                    found_valid = True
                    break
        if found_valid:
            continue

        if slug == "claims-gate":
            # The DRAFT is written by the PRODUCER, earlier in the transcript than claims-gate's
            # own dispatch — no ordering constraint relative to t_idx here. What must come at/after
            # t_idx is the *.verdict.md write itself, so a stale verdict from an unrelated earlier
            # draft/gate pair cannot satisfy this dispatch.
            draft_stems = {dp[: -len(".DRAFT.md")] for _w_idx2, dp in draft_writes}
            for w_idx, abs_path, content in md_writes:
                if w_idx < t_idx or not abs_path.endswith(".verdict.md"):
                    continue
                stem = abs_path[: -len(".verdict.md")]
                if stem in draft_stems:
                    locations_checked.append(os.path.relpath(abs_path, project_dir))
                    if validates(content):
                        validated.append((slug, content, None))
                        found_valid = True
                        break
        if found_valid:
            continue

        detail = ("no valid verdict found in: %s. Every gate ends its output with a valid "
                   "```verdict block (schema v3.4: verdict, integer confidence 0-10, falsifier, "
                   "evidence opening with MEASURED, CITED, COMPUTED, ESTIMATED or ASSUMED, "
                   "standards[]; a PASS also needs a path:line or a backticked command and "
                   "never rests on ASSUMED; MEASURED names the backticked command it ran), or — for a council seat or the claims gate — writes "
                   "one to the file location this hook checked." % "; ".join(locations_checked))
        problems.append("%s: %s" % (slug, detail))

    # Check 1b (D-112, R22): a verdict block's `agent` must be the agent whose dispatch returned it.
    # Applies to EVERY dispatch, gate or not, so a producer cannot hand back a block signed as a gate.
    all_returns = dict(all_dispatched)
    all_returns.update(resume_slug)        # a resumed agent's reply is that agent's return too (D-208)
    for tuid, slug in sorted(all_returns.items(), key=lambda kv: str(kv[0])):
        texts = []
        note = notifications.get(tuid) or {}
        if (note.get("summary") or "").strip():
            texts.append(note.get("summary"))
        if (note.get("result") or "").strip():          # a backgrounded seat's stored notice (D-164)
            texts.append(note.get("result"))
        out = results.get(tuid)
        if isinstance(out, str) and not out.startswith(STUB_PREFIX):
            texts.append(out)
        for text in texts:
            for raw in FENCE.findall(text):
                try:
                    obj = json.loads(raw)
                except Exception:  # D-259 (closed): a block that does not parse is not that gate's verdict, so the gate is unsatisfied
                    continue
                agent = obj.get("agent") if isinstance(obj, dict) else None
                if isinstance(agent, str) and agent.split(":")[-1].strip() != slug:
                    problems.append(
                        "%s: returned a verdict block signed by agent '%s'; a verdict block must "
                        "carry the agent of the dispatch that returned it" % (slug or "?", agent))
                elif isinstance(agent, str) and slug not in GATES | SEATS:
                    problems.append(
                        "not a gate agent: %s (it returned a verdict block; only a gate or a council seat signs "
                        "one, so a producer's own PASS is not a gate's verdict)" % slug)

    # Check 1c (D-117, R2, audit F2): a *.verdict.md written or edited this turn must carry blocks a gate
    # actually returned this turn — same agent, same verdict — so no producer or main session can write
    # its own PASS. Write content comes from the transcript; an Edit/MultiEdit is read from disk.
    def _norm_v(v):
        return "COULD NOT ASSESS" if v == "COULD_NOT_ASSESS" else v

    returned = set()           # {(agent slug, verdict)} from every dispatch's returned text this turn
    for tuid, slug in all_returns.items():
        texts = []
        note = notifications.get(tuid) or {}
        if (note.get("summary") or "").strip():
            texts.append(note.get("summary"))
        if (note.get("result") or "").strip():          # a backgrounded seat's stored notice (D-164)
            texts.append(note.get("result"))
        out = results.get(tuid)
        if isinstance(out, str) and not out.startswith(STUB_PREFIX):
            texts.append(out)
        for text in texts:
            for raw in FENCE.findall(text):
                try:
                    obj = json.loads(raw)
                except Exception:  # D-259 (closed): a block that does not parse is not that gate's verdict, so the gate is unsatisfied
                    continue
                if isinstance(obj, dict) and str(obj.get("agent") or "").split(":")[-1].strip() == slug:
                    returned.add((slug, _norm_v(obj.get("verdict"))))
    # A dispatched subagent's own writes live in its own transcript, beside the main one:
    # <transcript_path minus .jsonl>/subagents/agent-<agentId>.jsonl, linked by the dispatch's
    # toolUseResult.agentId (measured on client 2.1.288). Read them for every dispatch of this turn, so a
    # producer subagent with Write cannot write a verdict file or a marked .md unseen (D-117).
    sub_dir = os.path.join(tpath[: -len(".jsonl")] if tpath.endswith(".jsonl") else tpath, "subagents")
    sub_dir_missing = False
    for tuid in all_dispatched:
        aid = agent_ids.get(tuid)
        if not aid or not all(c.isalnum() or c in "-_" for c in aid):
            continue
        try:
            sub_lines = open(os.path.join(sub_dir, "agent-%s.jsonl" % aid), encoding="utf-8",
                             errors="replace").read().splitlines()
        except FileNotFoundError as exc:   # D-286 (closed): a dispatched agent whose own transcript is missing is a fault; no folder at all is announced
            if os.path.isdir(sub_dir):
                fault("the subagent transcript check of agent %s (its transcript is missing)" % aid, exc)
            else:
                sub_dir_missing = True
            continue
        except Exception as exc:   # D-270 (closed): a subagent transcript that cannot be read is a fault
            fault("the subagent transcript check of agent %s" % aid, exc)
            continue
        sub_denied = set()      # D-284 (Z7), for the subagent's own Write and Edit calls
        for sl in sub_lines:
            if '"is_error"' not in sl:
                continue
            try:
                se = json.loads(sl)
            except Exception:  # D-286 (closed): an unreadable line that looks like a call is reported below, by its number
                continue
            sc = (se.get("message") or {}).get("content") if isinstance(se, dict) and isinstance(se.get("message"), dict) else None
            for sb in sc if isinstance(sc, list) else []:
                if isinstance(sb, dict) and sb.get("type") == "tool_result" and sb.get("is_error") is True and sb.get("tool_use_id"):
                    sub_denied.add(sb["tool_use_id"])
        for n_sl, sl in enumerate(sub_lines, 1):
            try:
                sev = json.loads(sl)
            except Exception:  # D-286 (closed): an unreadable line that looks like a tool call or its result blocks, by its number (the main transcript's rule)
                if CALL_LINE.search(sl):
                    bad_sub_lines.append((aid, n_sl))
                continue
            if not isinstance(sev, dict):
                continue
            content_blocks = (sev.get("message") or {}).get("content")
            for sblk in content_blocks if isinstance(content_blocks, list) else []:
                if isinstance(sblk, dict) and sblk.get("type") == "tool_use" and sblk.get("name") == "Bash":
                    bash_verdict_refs.extend(VERDICT_REF.findall(str((sblk.get("input") or {}).get("command") or "")))
                    bash_cmds.append(str((sblk.get("input") or {}).get("command") or ""))
                    continue
                if not (isinstance(sblk, dict) and sblk.get("type") == "tool_use"
                        and sblk.get("name") in ("Write", "Edit", "MultiEdit")):
                    continue
                if sblk.get("id") in sub_denied:
                    continue           # D-284: it did not happen
                inp = sblk.get("input") or {}
                fp = inp.get("file_path") or ""
                if not fp.endswith(".md"):
                    continue
                ap = os.path.realpath(fp if os.path.isabs(fp) else os.path.join(project_dir, fp))
                if ap.endswith(".verdict.md"):
                    verdict_file_writes.append(
                        (-1, ap, inp.get("content") if sblk.get("name") == "Write" else None))
                elif not ap.endswith(".DRAFT.md") and find_marker_dir(os.path.dirname(ap), project_dir):
                    marked_md_writes.append((-1, ap))

    if sub_dir_missing:   # D-279, D-286: no subagents folder beside the transcript, so the writes of the agents dispatched this turn were not read
        extra_notes.add("subagent transcripts not found: writes by the agents dispatched this turn are not checked")

    # D-190: the disk check. A verdict file or marked .md that appeared or changed since turn start with no
    # Write or Edit of it this turn was written by something no command-text match can see.
    try:
        cur = disk_snapshot(project_dir)
        if cur is not None:
            try:
                state = json.load(open(_snap_path(tpath)))
                if "turn_start" not in state:
                    raise KeyError("turn_start")    # only the D-209 block count is in the file
                base = state.get("turn_start") or {}
                by_bash = {c for e in state.get("after_bash") or [] for c in e.get("changed") or []}
            except Exception:  # D-259 (closed): the fallback baseline is computed instead, and it counts unknown files as changed
                base, by_bash = _fallback_baseline(project_dir, cur, turn_ts), set()
            touched = {os.path.relpath(ap, project_dir) for _i, ap, _c in verdict_file_writes}
            touched |= {os.path.relpath(ap, project_dir) for _i, ap in marked_md_writes}
            for rel in sorted(k for k in cur if base.get(k) != cur[k]):
                how = "a Bash command changed it" if rel in by_bash else "it appeared or changed on disk"
                if rel.lower().endswith(".verdict.md"):
                    if rel in touched:
                        bash_verdict_refs.append(rel)      # re-read from disk below and checked as before
                    else:
                        problems.append(
                            "'%s': verdict file not produced by a gate dispatch this turn (%s with no Write or "
                            "Edit of it this turn; verdict files are written with the Write tool so the gate "
                            "check can read them)" % (rel, how))
                elif rel not in touched:
                    marked_md_writes.append((-1, os.path.join(project_dir, rel)))   # judged as a Write (D-190)
        else:   # D-279: the check skipped itself; the Stop says so, every time
            disk_note = ("disk check skipped (%s): verdict files and marked assets written outside the Write tool are not checked this turn"
                         % (DISK_SKIP["reason"] or "the tree could not be listed"))
            extra_notes.add(disk_note)
    except Exception as exc:   # D-259 (closed): a fault: the disk check did not run
        fault("the disk check of verdict and asset files", exc)   # D-259 (was fail-open on the snapshot)

    # D-190 (audit 3 G10): a Bash command whose write target is a plain .md under a marked folder promotes
    # an asset outside the Write path; the PreToolUse draft gate's own target parser names it.
    try:
        import importlib.util
        sys.dont_write_bytecode = True     # no __pycache__ beside the shipped hook (it is loaded, not imported)
        spec = importlib.util.spec_from_file_location("br_draft_gate", os.path.join(os.path.dirname(os.path.abspath(__file__)), "enforce-draft-gate.py"))
        dg = importlib.util.module_from_spec(spec); spec.loader.exec_module(dg)
        for c in bash_cmds:
            files, _dirs = dg.bash_write_targets(c)
            for path, srcs in files:
                ap = os.path.realpath(path if os.path.isabs(path) else os.path.join(project_dir, path))
                dests = [os.path.join(ap, os.path.basename(x.rstrip("/"))) for x in srcs] if (os.path.isdir(ap) or path.endswith("/")) else [ap]
                for dest in dests:
                    b = os.path.basename(dest).lower()
                    if b.endswith(".md") and not b.endswith(".draft.md") and not b.endswith(".verdict.md") \
                            and find_marker_dir(os.path.dirname(dest), project_dir):
                        marked_md_writes.append((-1, dest))   # same rule as a Write: a claims-gate dispatch this turn
    except Exception as exc:   # D-259 (closed): a fault: the Bash write check of marked folders did not run
        fault("the Bash write check of marked folders", exc)      # D-259

    # D-175: a verdict file a Bash command named this turn. With a Write/Edit origin, re-read it from disk
    # (the shell may have changed it); with none, it is not produced by a gate dispatch.
    bash_paths = set()
    for ref in bash_verdict_refs:
        if placeholder_verdict_name(ref):
            continue           # D-215: `<slug>.verdict.md` in a command's text names no file
        ref = re.sub(r"\$\{?[A-Za-z_][A-Za-z0-9_]*\}?", "*", ref.strip("'\""))   # `council/$s.verdict.md` in a loop
        base = ref if os.path.isabs(ref) else os.path.join(project_dir, ref)
        found = glob.glob(base) if any(c in ref for c in "*?[") else [base]
        bash_paths.update(os.path.realpath(f) for f in found)
    written = {ap for _i, ap, _c in verdict_file_writes}
    verdict_file_writes = [(i, ap, None if ap in bash_paths else c) for i, ap, c in verdict_file_writes]
    for ap in sorted(bash_paths - written):
        problems.append(
            "'%s': verdict file not produced by a gate dispatch this turn (a Bash command named it and no "
            "Write or Edit made it; verdict files are written with the Write tool so the gate check can read "
            "them)" % os.path.relpath(ap, project_dir))
    for _w_idx, ap, content in verdict_file_writes:
        if content is None:
            try:
                content = open(ap, encoding="utf-8", errors="replace").read()
            except FileNotFoundError:   # D-259 (b): the file is gone, so no verdict file stands
                continue           # D-259 (b): the file is gone, so no verdict file stands
            except Exception as exc:   # D-270 (closed): an unreadable verdict file is a problem line
                problems.append("'%s': the verdict file could not be read (%s): this gate is not passed" % (
                    os.path.relpath(ap, project_dir), type(exc).__name__))
                continue
        for raw in FENCE.findall(content or ""):
            try:
                obj = json.loads(raw)
            except Exception:  # D-259 (closed): a block that does not parse is no verdict (validate_verdict.py rejects it), so it promotes nothing
                continue
            if not isinstance(obj, dict):
                continue
            key = (str(obj.get("agent") or "").split(":")[-1].strip(), _norm_v(obj.get("verdict")))
            if key[0] not in GATES | SEATS:
                problems.append("'%s': not a gate agent: %s (a verdict file carries a gate's block, never a "
                                "producer's)" % (os.path.relpath(ap, project_dir), key[0] or "?"))
            elif key not in returned:
                problems.append(
                    "'%s': verdict file not produced by a gate dispatch this turn (block agent '%s', "
                    "verdict %s; no dispatch of that agent returned that verdict in this turn)" % (
                        os.path.relpath(ap, project_dir), key[0] or "?", key[1]))
    for _w_idx, ap in marked_md_writes:
        if not claims_gate_at:
            problems.append(
                "DRAFT/GATED: '%s' was written under a marketing-asset directory with no claims-gate "
                "dispatch this turn." % os.path.relpath(ap, project_dir))

    # Check 3 (D-146): a MEASURED verdict must cite a command this session ran. Executed commands come
    # from every Bash tool_use in the main transcript (all turns) and every subagent transcript.
    measured_matched = set()
    failed_ids = {"ids": set()}
    try:
        executed, failed = {}, set()   # tool_use_id -> whitespace-collapsed command; ids whose result is_error

        def _scan(src_lines):
            for sl in src_lines:
                try:
                    sev = json.loads(sl)
                except Exception:  # D-259 (closed): a line that is not JSON adds no executed command, so a MEASURED span it would match blocks
                    continue
                if not isinstance(sev, dict):
                    continue
                cb = (sev.get("message") or {}).get("content")
                for b in cb if isinstance(cb, list) else []:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_use" and b.get("name") == "Bash":
                        c = (b.get("input") or {}).get("command")
                        if isinstance(c, str) and c.strip():
                            executed[b.get("id")] = _flat(c)   # D-210
                    elif b.get("type") == "tool_result" and b.get("is_error") is True:
                        failed.add(b.get("tool_use_id"))

        failed_ids["ids"] = failed
        own_run = {}                   # D-222: the hook's own test run, made at most once per Stop

        def quality_pass_problem(slug):
            """None when the hook's own run of the recorded test command passes and covers the change (D-222, D-227);
            else the problem. The gate's printed output is not read."""
            if not own_run:
                own_run.update(hook_test_run(project_dir, payload.get("session_id"), turn_ts or "idx%d" % turn_start))
                extra_notes.update(own_run.get("notes") or [])
                if not own_run.get("problem"):
                    cmd_ = own_run["cmd"]
                    parsed = [_canon((_simple_commands(c_) or [()])[-1]) for c_ in own_run.get("cmds") or [cmd_]]
                    # every recorded runner names test paths: together they must reach the change (D-218, D-227, D-246)
                    if all(_is_known_runner(r_) and _named_test_paths(a_, project_dir) for r_, a_ in parsed):
                        ch = changed_files(project_dir)
                        if ch is None:
                            extra_notes.add("changed-file check skipped: no git")
                        elif not any(tested_the_change(a_, ch, project_dir) for _r, a_ in parsed):
                            own_run["problem"] = "the hook's test run did not test the changed files: `%s`" % cmd_
                    if not own_run.get("problem"):        # D-252: the local run passed; CI decides
                        rec_ = install_record(project_dir)
                        if rec_.get("ci_judge") is False:  # D-254: the owner chose this machine as the judge
                            extra_notes.add(NO_CI_JUDGE_LINE)
                        else:
                            cj = ci_judge(project_dir, rec_)
                            own_run["ci"] = cj
                            if cj["state"] == "fail":
                                own_run["problem"] = cj["msg"]
                            elif cj["state"] == "pass":
                                extra_notes.add(cj["msg"])
                            else:
                                ci_pending.add(cj["msg"])
                    if not own_run.get("problem"):
                        extra_notes.add("hook test run `%s`: %d passed, %d failed%s%s" % (
                            cmd_[:80], own_run.get("passed", 0), own_run.get("failed", 0),
                            " (cached)" if own_run.get("cached") else "", "" if own_run.get("note") == "confined" else
                            "; " + str(own_run.get("note"))))
            return ("%s: %s" % (slug, own_run["problem"])) if own_run.get("problem") else None
        _scan(session_lines)
        if os.path.isdir(sub_dir):
            for fn in sorted(os.listdir(sub_dir)):
                if fn.startswith("agent-") and fn.endswith(".jsonl"):
                    try:
                        _scan(open(os.path.join(sub_dir, fn), encoding="utf-8",
                                   errors="replace").read().splitlines())
                    except Exception:  # D-259 (closed): a subagent run not read adds no executed command, so a MEASURED span it would match blocks
                        continue
        for slug, text, own_aid in validated:
            for raw in FENCE.findall(text or ""):
                try:
                    obj = json.loads(raw)
                except Exception:  # D-259 (closed): a block that does not parse carries no PASS
                    continue
                ev = obj.get("evidence") if isinstance(obj, dict) else None
                if not isinstance(ev, str):
                    continue
                quality_pass = (str(obj.get("agent") or "").split(":")[-1].strip() in QUALITY_GATES
                                and obj.get("verdict") == "PASS" and re.match(r"^(CITED|MEASURED)\b", ev))
                if quality_pass:   # D-222
                    prob = quality_pass_problem(slug)
                    if prob:
                        problems.append(prob)
                    continue
                if not re.match(r"^MEASURED\b", ev):
                    continue
                spans = [" ".join(x.split()) for x in re.findall(r"`([^`]+)`", ev)]
                spans = [x for x in spans if x]
                hits = [tid for tid, cmd in executed.items() for sp in spans if span_matches(sp, cmd, project_dir)]
                if hits:
                    measured_matched.update(hits)
                else:
                    near = nearest_command(spans[0], list(executed.values()), project_dir) if spans else None
                    problems.append("%s: MEASURED command not executed in this session: %s%s" % (
                        slug, ", ".join("`%s`" % x[:120] for x in spans[:3]) or "(no backticked command)",
                        ("; nearest command run: `%s`" % near[:160]) if near else ""))
    except Exception as exc:   # D-259 (closed): a fault: the test and MEASURED-evidence check did not run
        fault("the test and MEASURED-evidence check", exc)   # D-259 (was fail-open: a PASS stood on any error here)

    # Check 4 (D-231): in plugin mode, the enforcement files still match the baseline /workforce-init recorded.
    try:
        problems.extend(tamper_problems(project_dir, gated=bool(all_dispatched)))
    except Exception as exc:   # D-259 (closed): a fault: the tamper check did not run
        fault("the tamper check", exc)                       # D-259 (was fail-open)

    # D-270: a line of this turn that cannot be read and looks like a dispatch or a result could be a gate not judged
    if bad_call_lines:
        problems.append("transcript line%s %s cannot be read as JSON and look%s like a tool call or its result: this turn is not gated; report it"
                        % ("s" if len(bad_call_lines) > 1 else "", ", ".join(str(n) for n in bad_call_lines[:5]),
                           "" if len(bad_call_lines) > 1 else "s"))

    if bad_sub_lines:      # D-286 (X11): the rule for the main transcript, applied to each dispatched agent's own transcript
        problems.append("subagent transcript line%s %s cannot be read as JSON and look%s like a tool call or its result: this turn is not gated; report it"
                        % ("s" if len(bad_sub_lines) > 1 else "", ", ".join("%d of agent %s" % (n_, a_) for a_, n_ in bad_sub_lines[:5]),
                           "" if len(bad_sub_lines) > 1 else "s"))

    # D-259: every error a judging path recorded blocks
    if ROSTER_FAULT[0] and all_dispatched:
        problems.append(ROSTER_FAULT[0])
    problems.extend(x for x in FAULTS if x not in problems)

    # Check 2 (the 2.1.0 claims-gate change): a DRAFT under a marked directory needs a LATER claims-gate dispatch.
    for idx, abs_path in draft_writes:
        if not any(g > idx for g in claims_gate_at):
            problems.append(
                "DRAFT/GATED: '%s' was written under a marketing-asset directory with no "
                "claims-gate dispatch afterward in this session." % (
                    os.path.relpath(abs_path, project_dir)))

    if not problems and ci_pending:
        # D-252: nothing to fix in the turn, but a quality PASS is not a PASS until CI says so. The turn may end.
        print(json.dumps({"systemMessage": "Verdict check INCOMPLETE: %s. Gates checked %d; a later turn re-reads CI%s." % (
            "; ".join(sorted(ci_pending)), len(judged), "".join("; " + x for x in chain_notes + sorted(extra_notes)))}))
        return 0

    if not problems and judged:
        # W-09 completion signal (2.3.3): one line after a clean turn that dispatched gates, so a
        # quiet Stop hook is distinguishable from an absent one. Not a block: no "decision" key.
        n = len(judged)
        print(json.dumps({"systemMessage": "BlackRaptor verdict check: gates checked %d, verdicts valid %d; "
                          "measured: %d runs matched, %d non-zero%s."
                          % (n, n, len(measured_matched), len(measured_matched & failed_ids["ids"]),
                             "".join("; " + x for x in chain_notes + sorted(extra_notes)))}))
        return 0

    if problems:
        # De-duplicate while preserving order (P3-FOLLOWON-v2 §3): a same-turn retry dispatches the
        # same gate twice, producing two identical problem lines (e.g. `security-architect` invalid
        # both attempts) that read as two separate failures to the user. Distinct problems, including
        # a distinct gate, are never collapsed — only an exact repeat of the same line.
        seen = set()
        deduped = []
        for p in problems:
            if p not in seen:
                seen.add(p)
                deduped.append(p)
        problems = deduped
        n_blocks = bump_stop_blocks(tpath, payload, turn_ts or "idx%d" % turn_start)   # D-209
        if (n_blocks > MAX_STOP_BLOCKS) if n_blocks is not None else bool(payload.get("stop_hook_active")):   # D-286 (X9): no count kept, so a Stop already bounced once ends loudly
            running = [p_.split(":")[0] for p_ in problems if p_.endswith("gate seat still running; wait for its result before ending the turn")]
            if len(running) == len(problems):   # D-220: a gate still running is not a failed verdict
                print(json.dumps({"systemMessage": "Verdict check INCOMPLETE: %s still running at turn end; this turn "
                                  "is not gated until %s returns." % (", ".join(running), "it" if len(running) == 1 else "they")}))
                return 0
            print(json.dumps({"systemMessage": "Verdict check FAILED and was not fixed: after %d blocks this turn the "
                              "problems remain, so this turn is not gated:\n  - %s" % (MAX_STOP_BLOCKS, "\n  - ".join(problems[:5]))}))
            return 0
        print(json.dumps({
            "decision": "block",
            "reason": ("This turn cannot be treated as gated. Fix and re-emit:\n  - "
                       + "\n  - ".join(problems[:5])
                       + "\nIf you believe this block is wrong, stop and report it to the human with the "
                         "reason above; do not disable the check."),
        }))
    elif disk_note:       # D-279: a turn with no gate and no problem still says the disk check was skipped
        print(json.dumps({"systemMessage": "Verdict check: " + disk_note}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
