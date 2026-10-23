#!/usr/bin/env python3
"""workforce_init.py: install, upgrade or remove the BlackRaptor Workforce in a repo.

Run by the core command /workforce-init. Python 3 standard library only.

  python3 workforce_init.py [--mode plugin|copy|user] [--sandbox yes|no | --no-sandbox]
                            [--test-cmd CMD] [--test-timeout SECONDS] [--lint-cmd CMD] [--typecheck-cmd CMD]
                            [--upgrade [--confirm-removals]] [--accept-changes] [--accept-runner-config]
                            [--remove] [--dry-run]
                            [--suggest] [--repo DIR] [--yes]

Modes:
  plugin  (default) the repo's .claude/settings.json names the marketplace and the packs, so a
          collaborator who opens and trusts the repo is offered the same packs.
  copy    the engineering agents and the skills they name are copied into .claude/agents/ and
          .claude/skills/, with a checksum file, a guard script and a CI job that fails when a
          copy drifts from the checksum file.
  user    nothing is written to the repo except the project values and the installed list.

Rules it keeps:
  - Every file it writes or edits is listed with its sha256 in .claude/workforce-installed.json.
  - It never overwrites a user file. JSON settings are merged key by key. A non-JSON file that
    already exists and differs is skipped and reported.
  - --remove deletes only files whose current sha256 matches the installed list. A file you
    changed since the install is kept and reported.
  - --upgrade in copy mode stops before deleting a file the newer packs no longer ship, and names
    it (and where it went, if it moved to another pack). Re-run with --confirm-removals to go on.
  - A repo-owned file that is not in any pack is never touched.
  - When it installs the Tier-3 hook it adds the hook's log, .claude/hooks/tier3-attempts.log, to
    the repo's .gitignore (creating it if absent, appending only if the line is missing); --remove
    takes out only that line, and deletes .gitignore only if this command created it and it is
    otherwise empty.
  - With the Tier-3 hook it writes an empty .claude/live-commands-allow.txt: the repo's read-only
    exceptions to the hook's live-system check, one regular expression per line, edited by the human
    only (the hook protects it). --remove deletes it only while it is still empty.
  - The sandbox (D-223, on by default): sandbox.enabled, sandbox.failIfUnavailable, allowUnsandboxedCommands
    false, and sandbox.filesystem.denyWrite for every enforcement file outside the .claude folders the sandbox
    already protects. With the sandbox on, no agent's shell command can write them. --no-sandbox (or
    --sandbox no) is the opt-out and says what it gives up.
  - The test command (D-222): `test_cmd` and `test_timeout` (default 300 s) are recorded in the installed
    list. The Stop hook runs that command itself to check a test-auditor or completion-auditor PASS.
  - Plugin mode (D-231): the sha256 of every enforcement file is recorded in a baseline in the core plugin's
    data folder (under ~/.claude/plugins/, out of every agent's reach with the sandbox on); the Stop hook
    blocks when a file differs. --upgrade and --accept-changes rewrite the baseline. Copy and user modes
    have no protected baseline. With the sandbox on, run --upgrade, --accept-changes and --remove from your
    own terminal: the script writes files the sandbox keeps every shell command in a session out of.
  - Test runner config (D-233): the same baseline records the files that steer the test runner (conftest.py,
    pytest.ini, the pytest tables, jest/vitest/mocha config, the test scripts in package.json, any repo file the
    test command names). The Stop hook blocks a quality PASS while one differs. Install and --upgrade record them;
    after reviewing a change, --accept-runner-config records them again. Copy mode compares with the base branch
    instead, which is weaker (an agent can rewrite git refs).

Exit codes: 0 done; 1 usage or environment error; 3 stopped (upgrade needs confirmation, or a
check failed). Nothing is written on --dry-run or on exit 3.
"""

from __future__ import print_function

import argparse
import datetime
import errno
import glob
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys

SCHEMA = 1
INSTALLED = ".claude/workforce-installed.json"
SETTINGS = ".claude/settings.json"
CONTEXT = "BUSINESS-CONTEXT.md"
CHECKSUMS = ".claude/review-copies.sha256"
GUARD = ".claude/check-review-copies.py"
GUARD_CI = ".github/workflows/review-copies.yml"
GITIGNORE = ".gitignore"
HOOK_LOG = ".claude/hooks/tier3-attempts.log"   # the Tier-3 hook's audit log of blocks and overrides
LIVE_ALLOW = ".claude/live-commands-allow.txt"  # the human's live-command exceptions (2.8.2); installed empty
# D-223: the enforcement files outside the folders the sandbox already protects (.claude settings files and
# .claude/hooks, agents, skills, commands). sandbox.filesystem.denyWrite lists each, so no shell command can write it.
DENY_WRITE = [".claude/gates-allow.txt", ".claude/test-summary-patterns.txt", LIVE_ALLOW, INSTALLED, CHECKSUMS,
              ".github/workflows/change-record-required.yml", ".github/workflows/workforce-proof.yml"]   # D-253
DENY_WRITE_COPY = [GUARD, GUARD_CI]
NO_SANDBOX_MSG = ("enforcement files are not protected without the sandbox; hooks still run, but an agent with a "
                  "shell can edit them")
NO_SANDBOX_TAMPER = "the tamper check can also be edited without the sandbox, so it no longer protects you"   # D-240
COPY_RUNNER_NOTE = ("copy mode checks the test runner config against the base branch, not a protected baseline; this "
                    "is weaker, because an agent can rewrite git refs")                                     # D-233
TEST_TIMEOUT_DEFAULT = 300
# D-251: the test files workforce-proof's base-suite puts back from the merge base, per ecosystem (test_globs).
TEST_GLOBS = {
    "python": ["tests/**", "test/**", "**/tests/**", "**/test_*.py", "**/*_test.py"],
    "node": ["**/*.test.*", "**/*.spec.*", "**/__tests__/**", "test/**", "tests/**"],
    "go": ["**/*_test.go"],
    "java": ["**/src/test/**"],
    "dotnet": ["**/*Tests/**", "**/*Test.cs", "**/*Tests.cs"],
}
NO_CI_JUDGE_MSG = ("No CI judge: test passes are checked only on this machine, where an agent can fake them. Use CI for "
                   "real proof.")                                                                    # D-254
CI_CHECKS = ("head-suite", "base-suite")
GITHUB_ACTIONS_APP_ID = 15368     # measured at Amendment 8 C-0: the app id of check runs Actions creates
TAMPER_BASELINE = "tamper-baseline.json"
COPY_NO_TAMPER = ("tamper detection needs plugin mode: copy mode keeps no baseline where agents cannot write, so a "
                  "changed enforcement file is not caught at Stop (the copy guard and CI still check the copies)")
MARKETPLACE = "blackraptor"
MARKETPLACE_SOURCE = {"source": {"source": "github", "repo": "BlackRaptorAI-Labs/BlackRaptor_Workforce"}}
PACKS = ["core", "engineering", "council", "marketing", "hardware"]
PLUGIN_ID = dict((p, "blackraptor-" + p) for p in PACKS)
VALUE_SLOTS = ["TEST_CMD", "LINT_CMD", "TYPECHECK_CMD"]

# The engineering repo files: (path inside the pack, path in the repo). CUSTOMIZATION.md section 1.
ENG_FILES = [
    ("engineering", "claude/hooks/protect-tier3.py", ".claude/hooks/protect-tier3.py"),
    ("engineering", "github/change-record-required.yml", ".github/workflows/change-record-required.yml"),
    ("engineering", "github/workforce-proof.yml", ".github/workflows/workforce-proof.yml"),       # D-251: the CI judge
    ("core", "skills/gate-verdict-format/validate_verdict.py", ".claude/skills/gate-verdict-format/validate_verdict.py"),
    ("core", "skills/gate-verdict-format/verdict-schema.json", ".claude/skills/gate-verdict-format/verdict-schema.json"),
]
ENG_SETTINGS = "claude/settings.json"   # its "hooks" block is merged into the repo's settings

GUARD_TEXT = r'''#!/usr/bin/env python3
"""Fails when a copied Workforce file differs from .claude/review-copies.sha256.

Written by /workforce-init (copy mode). Standard library only. Run from the repo root:
  python3 .claude/check-review-copies.py
Only the files listed in the checksum file are checked; repo-owned files are never read.
"""
import hashlib, os, sys
SUMS = ".claude/review-copies.sha256"
def main():
    try:
        lines = open(SUMS, encoding="utf-8").read().splitlines()
    except OSError as exc:
        print("review-copies: cannot read %s: %s" % (SUMS, exc)); return 1
    bad = checked = 0
    for line in lines:
        if not line.strip() or line.startswith("#"):
            continue
        want, sep, path = line.partition("  ")
        if not sep or len(want) != 64:
            print("review-copies: malformed line: %s" % line); bad += 1; continue
        checked += 1
        try:
            got = hashlib.sha256(open(path, "rb").read()).hexdigest()
        except OSError:
            print("review-copies: MISSING %s" % path); bad += 1; continue
        if got != want:
            print("review-copies: CHANGED %s (expected %s, found %s)" % (path, want[:12], got[:12])); bad += 1
    if checked == 0:
        print("review-copies: no files listed in %s (failing closed)" % SUMS); return 1
    if bad:
        print("review-copies: FAIL, %d of %d copied file(s) differ from the checksum file. "
              "Restore each file from git, or delete it and re-run /workforce-init --upgrade." % (bad, checked))
        return 1
    print("review-copies: OK, %d copied file(s) match the checksum file" % checked)
    return 0
if __name__ == "__main__":
    sys.exit(main())
'''

GUARD_CI_TEXT = '''# review-copies: fails when an agent or skill copied by /workforce-init (copy mode) differs from
# .claude/review-copies.sha256. Written by /workforce-init; remove it with /workforce-init --remove.
name: review-copies
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  review-copies:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 .claude/check-review-copies.py
'''


# ---------------------------------------------------------------------------------------------
# small helpers

def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(path):
    with open(path, "rb") as fh:
        return sha_bytes(fh.read())


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def say(msg=""):
    print(msg)


def die(msg, code=1):
    sys.stderr.write("workforce-init: %s\n" % msg)
    sys.exit(code)


def json_text(obj):
    return json.dumps(obj, indent=2, sort_keys=False) + "\n"


def repo_root(arg):
    if arg:
        return os.path.realpath(arg)
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        if out.returncode == 0 and out.stdout.strip():
            return os.path.realpath(out.stdout.strip())
    except OSError:
        pass
    return os.path.realpath(os.getcwd())


# ---------------------------------------------------------------------------------------------
# finding the installed packs

def config_dir():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")


def pack_version(root):
    try:
        return json.load(open(os.path.join(root, ".claude-plugin", "plugin.json"), encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError):
        return None


def find_packs(repo, overrides):
    """{pack: root} for every BlackRaptor pack this machine has installed.

    Order: --pack-root overrides; core is the pack this script ships in; then the client's
    installed_plugins.json, preferring a project-scope entry for this repo, then an entry from the
    same marketplace as core, then any user-scope entry; then, for packs loaded straight from a local
    marketplace folder (enabled in settings, no installed_plugins.json entry), the folder beside core."""
    found = {}
    for item in overrides:
        name, _, root = item.partition("=")
        if name not in PACKS or not root:
            die("--pack-root wants <pack>=<dir> with pack one of %s" % ", ".join(PACKS))
        found[name] = os.path.realpath(root)
    here = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))   # <pack root>/scripts/..
    if "core" not in found and pack_version(here):
        found["core"] = here
    core_market = None
    m = re.search(r"/plugins/cache/([^/]+)/blackraptor-core/", found.get("core", "") + "/")
    if m:
        core_market = m.group(1)
    try:
        data = json.load(open(os.path.join(config_dir(), "plugins", "installed_plugins.json"), encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    cands = {}
    for key, entries in (data.get("plugins") or {}).items():
        pid, _, market = key.partition("@")
        pack = pid[len("blackraptor-"):] if pid.startswith("blackraptor-") else None
        if pack not in PACKS:
            continue
        for e in entries or []:
            path = e.get("installPath")
            if not path or not os.path.isdir(path):
                continue
            if e.get("scope") in ("project", "local"):
                if os.path.realpath(e.get("projectPath") or "") != repo:
                    continue
                rank = 0
            elif e.get("scope") == "user":
                rank = 1 if market == core_market else 2
            else:
                continue
            cands.setdefault(pack, []).append((rank, key, path))
    for pack, lst in cands.items():
        if pack not in found:
            found[pack] = os.path.realpath(sorted(lst)[0][2])
    enabled = set()
    for f in (os.path.join(config_dir(), "settings.json"), os.path.join(repo, SETTINGS),
              os.path.join(repo, ".claude", "settings.local.json")):
        try:
            ep = json.load(open(f, encoding="utf-8")).get("enabledPlugins") or {}
        except (OSError, ValueError, AttributeError):
            continue
        enabled |= set(k.split("@", 1)[0] for k, v in ep.items() if v)
    parent = os.path.dirname(found.get("core", here))
    for pack in PACKS:
        sib = os.path.join(parent, pack)
        if pack not in found and PLUGIN_ID[pack] in enabled and pack_version(sib):
            found[pack] = os.path.realpath(sib)
    return found


# ---------------------------------------------------------------------------------------------
# project values

def suggest_values(repo):
    s = {}
    pj = os.path.join(repo, "package.json")
    if os.path.isfile(pj):
        try:
            scripts = (json.load(open(pj, encoding="utf-8")).get("scripts") or {})
        except ValueError:
            scripts = {}
        if "test" in scripts:
            s["TEST_CMD"] = "npm test"
        if "lint" in scripts:
            s["LINT_CMD"] = "npm run lint"
        for k in ("typecheck", "type-check", "tsc"):
            if k in scripts:
                s["TYPECHECK_CMD"] = "npm run " + k
                break
        if "TYPECHECK_CMD" not in s and os.path.isfile(os.path.join(repo, "tsconfig.json")):
            s["TYPECHECK_CMD"] = "npx tsc --noEmit"
    pp = os.path.join(repo, "pyproject.toml")
    if os.path.isfile(pp):
        text = open(pp, encoding="utf-8", errors="replace").read()
        s.setdefault("TEST_CMD", "python3 -m pytest")
        if "[tool.ruff" in text:
            s.setdefault("LINT_CMD", "ruff check .")
        if "[tool.mypy" in text:
            s.setdefault("TYPECHECK_CMD", "mypy .")
    mk = os.path.join(repo, "Makefile")
    if os.path.isfile(mk):
        text = open(mk, encoding="utf-8", errors="replace").read()
        for slot, target in (("TEST_CMD", "test"), ("LINT_CMD", "lint"), ("TYPECHECK_CMD", "typecheck")):
            if re.search(r"(?m)^%s\s*:" % target, text):
                s.setdefault(slot, "make " + target)
    return s


ROW_RE = re.compile(r"^\|\s*`?([A-Z][A-Z0-9_]*)`?\s*\|")


def context_with_values(text, values):
    """Return (new_text, added_rows, kept_slots). Adds a row per slot that has none; never edits a row."""
    lines = text.splitlines(True) if text else []
    have = set()
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^##\s+Project values\s*$", line.strip()):
            start = i
    if start is not None:
        for line in lines[start + 1:]:
            if line.startswith("## "):
                break
            m = ROW_RE.match(line)
            if m:
                have.add(m.group(1))
    add = [(k, values[k]) for k in VALUE_SLOTS if values.get(k) and k not in have]
    kept = [k for k in VALUE_SLOTS if values.get(k) and k in have]
    if not add:
        return text, [], kept
    rows = ["| %s | %s |\n" % (k, v) for k, v in add]
    if start is None:
        if not lines:
            head = "# Business context\n\n"
        elif text.endswith("\n\n"):
            head = ""
        elif text.endswith("\n"):
            head = "\n"
        else:
            head = "\n\n"
        return text + head + "## Project values\n\n| Slot | Value |\n|---|---|\n" + "".join(rows), rows, kept
    # insert after the last table row of the Project values section
    last = start
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            break
        if lines[j].startswith("|"):
            last = j
    if last == start:   # section with no table: add header + rows right after the heading
        ins = ["\n", "| Slot | Value |\n", "|---|---|\n"] + rows
    else:
        ins = rows
        if not lines[last].endswith("\n"):
            lines[last] += "\n"
    new = lines[:last + 1] + ins + lines[last + 1:]
    return "".join(new), rows, kept


def context_without_rows(text, rows):
    lines = text.splitlines(True)
    out, removed = [], 0
    pending = list(rows)
    for line in lines:
        if line in pending:
            pending.remove(line)
            removed += 1
            continue
        out.append(line)
    return "".join(out), removed


# ---------------------------------------------------------------------------------------------
# JSON merge with an undo record

def merge_settings(cur, add):
    """Merge `add` into `cur` key by key. Returns (merged, ops). ops are ("set", path, value) for keys
    that did not exist and ("append", path, item) for list items added to an existing or new list."""
    ops = []

    def walk(dst, src, path):
        for k, v in src.items():
            p = path + [k]
            if k not in dst:
                dst[k] = v
                ops.append(("set", p, v))
            elif isinstance(dst[k], dict) and isinstance(v, dict):
                walk(dst[k], v, p)
            elif isinstance(dst[k], list) and isinstance(v, list):
                for item in v:
                    if item not in dst[k]:
                        dst[k].append(item)
                        ops.append(("append", p, item))
            # an existing scalar the user set is never changed
    merged = json.loads(json.dumps(cur))
    walk(merged, add, [])
    return merged, ops


def unmerge_settings(cur, ops):
    """Undo ops where the value is still what was written. Returns (new, kept_paths)."""
    new = json.loads(json.dumps(cur))
    kept = []
    for op, path, val in reversed(ops):
        node = new
        for k in path[:-1]:
            node = node.get(k) if isinstance(node, dict) else None
            if node is None:
                break
        if not isinstance(node, dict) or path[-1] not in node:
            continue
        if op == "set":
            if node[path[-1]] == val:
                del node[path[-1]]
            else:
                kept.append(".".join(path))
        elif op == "append" and isinstance(node[path[-1]], list):
            if val in node[path[-1]]:
                node[path[-1]].remove(val)
                if not node[path[-1]]:
                    del node[path[-1]]
    # drop containers emptied by the undo
    def prune(d):
        for k in list(d):
            if isinstance(d[k], dict):
                prune(d[k])
                if not d[k]:
                    del d[k]
    prune(new)
    return new, kept


# ---------------------------------------------------------------------------------------------
# the plan: what this install wants in the repo

class Plan(object):
    def __init__(self):
        self.files = {}      # repo path -> (bytes, source label)
        self.settings = {}   # dict merged into .claude/settings.json
        self.values = {}
        self.copied = {}     # repo path -> pack (copy mode only)
        self.ignore = []     # lines the repo's .gitignore must hold
        self.notes = []


def deny_write_paths(mode):
    return ["./" + p for p in DENY_WRITE + (DENY_WRITE_COPY if mode == "copy" else [])]


# ---------------------------------------------------------------------------------------------
# D-231: the tamper baseline (plugin mode)

def plugin_data_dir(packs, override=None):
    """The core plugin's data folder: --plugin-data, else CLAUDE_PLUGIN_DATA, else derived from where core is
    installed (<config>/plugins/cache/<marketplace>/blackraptor-core/<version> -> <config>/plugins/data/
    blackraptor-core-<marketplace>), the folder the client gives the core plugin's hooks."""
    if override:
        return os.path.realpath(override)
    if os.environ.get("CLAUDE_PLUGIN_DATA"):
        return os.environ["CLAUDE_PLUGIN_DATA"]
    m = re.match(r"^(.*)/plugins/cache/([^/]+)/([^/]+)/[^/]+/?$", os.path.realpath(packs.get("core", "/-")))
    if m:
        return os.path.join(m.group(1), "plugins", "data", re.sub(r"[^A-Za-z0-9_.-]", "-", "%s-%s" % (m.group(3), m.group(2))))
    return None


def settings_hooks_hash(repo):
    try:
        st = json.load(open(os.path.join(repo, SETTINGS), encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return sha_bytes(json.dumps(st.get("hooks") if isinstance(st, dict) else None, sort_keys=True).encode("utf-8"))


def enforcement_hashes(repo, mode):
    """{repo path: sha256 or None (absent)} for every file in .claude/hooks (its log aside) and every denyWrite path.
    The same reading as the Stop hook's (validate-verdicts.py enforcement_hashes)."""
    names = set(DENY_WRITE + (DENY_WRITE_COPY if mode == "copy" else []))
    hd = os.path.join(repo, ".claude", "hooks")
    if os.path.isdir(hd):
        names |= set(".claude/hooks/" + f for f in os.listdir(hd) if not f.endswith(".log") and f != "__pycache__")
    out = {}
    for rel in names:
        p = os.path.join(repo, rel)
        out[rel] = sha_file(p) if os.path.isfile(p) else ("dir" if os.path.isdir(p) else None)
    return out


def write_baseline(repo, data, mode, by, remove=False, test_cmd=None, part="all"):
    """Record (or, with remove, drop) this repo's entry in <data>/tamper-baseline.json. `part` "files" keeps the
    recorded runner config (--accept-changes); "runner" keeps the recorded enforcement files (--accept-runner-config,
    D-233). Returns the file path."""
    path = os.path.join(data, TAMPER_BASELINE)
    try:
        allb = json.load(open(path, encoding="utf-8"))
        if not isinstance(allb, dict):
            allb = {}
    except (OSError, ValueError):
        allb = {}
    if remove:
        allb.pop(repo, None)
    else:
        old = allb.get(repo) if isinstance(allb.get(repo), dict) else {}
        new = {"files": enforcement_hashes(repo, mode), "settings_hooks": settings_hooks_hash(repo),
               "runner_config": runner_control_hashes(repo, test_cmd), "by": by, "date": datetime.date.today().isoformat()}
        if part == "files":
            new["runner_config"] = old.get("runner_config")
        elif part == "runner":
            new["files"], new["settings_hooks"] = old.get("files"), old.get("settings_hooks")
        allb[repo] = new
    if not os.path.isdir(data):
        os.makedirs(data)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json_text(allb))
    return path


# ---------------------------------------------------------------------------------------------
# D-233: the test runner config. The same list and reading as the Stop hook's (validate-verdicts.py
# RUNNER_CONTROL, runner_control_hashes); keep the two in step (a fixture compares their output).

RUNNER_CONTROL = {
    "names": ("conftest.py", "pytest.ini", ".pytest.ini", "pytest.toml", ".pytest.toml", "sitecustomize.py",
              "usercustomize.py", "setup.py"),
    "suffixes": (".pth",),
    "prefixes": ("jest.config.", "vitest.config.", "vitest.workspace.", "vite.config.", ".mocharc", "karma.conf.",
                 "playwright.config."),
    "sections": {"pyproject.toml": "tool.pytest", "setup.cfg": "tool:pytest", "tox.ini": "pytest"},
}
RC_WALK_LIMIT = 200000
RC_SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".tox", ".mypy_cache"}
TEST_FILE = re.compile(r"(^|/)(tests?|__tests__|spec)/|(^|/)test_[^/]*\.py$|_test\.(py|go)$|\.(test|spec)\.[cm]?[jt]sx?$|Tests?\.(java|kt|cs)$")
REDIRECT = re.compile(r"(?<!\S)[0-9]*(?:&>>?|>>?&?|<)\s*[^\s;|&<>]+")
CMD_SEP = {";", "&&", "||", "|", "&", "|&"}


def _simple_commands(text):
    text = REDIRECT.sub(" ", text.replace("\n", " ; "))
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=";&|")
        lex.whitespace_split = True
        toks = list(lex)
    except ValueError:
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


def _rc_section(text, want):
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
    except ValueError:
        return raw.decode("utf-8", "replace")
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
        except ValueError:
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
        except FileNotFoundError:
            main = "index.js"
        except Exception as exc:
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
        except OSError:
            return None
        out["%s (%s)" % (rel(path), label)] = sha(b)
        return b
    for v in sorted(set(venvs)):
        for sp in _site_dirs(v):
            try:
                entries = sorted(os.listdir(sp))
            except OSError:
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
                    except OSError:
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
            except ValueError:
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
            except OSError:
                pass


def runner_control_hashes(root, test_cmd, env=True):
    """{key: sha256} for every runner-control input present in the work tree, and with `env` the startup files of the
    in-repo environments (D-243); None past RC_WALK_LIMIT."""
    root = os.path.realpath(root)
    names, n = [], 0
    venvs, node_dirs = [], []
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

    def read(rel):
        try:
            with open(os.path.join(root, rel), "rb") as fh:
                return fh.read()
        except OSError:
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


def _changed_keys(old, new):
    old, new = old or {}, new or {}
    return sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))


def context_test_cmd(repo):
    """TEST_CMD from BUSINESS-CONTEXT.md's Project values table, if set."""
    try:
        text = open(os.path.join(repo, CONTEXT), encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    m = re.search(r"^\|\s*`?TEST_CMD`?\s*\|\s*(.*?)\s*\|", text, re.M)
    val = (m.group(1) if m else "").strip().strip("`").strip()
    if not val or re.fullmatch(r"(?i)[_\-\u2014.\s]*|n/?a|none|tbd|\{\{.*\}\}|<.*>", val):
        return None
    return val


def skill_names_in(text, names):
    return set(n for n in names if re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(n), text))


def default_test_globs(repo):
    """D-251: test-file globs for the ecosystems this repo shows; every list when it shows none."""
    has = lambda *names: any(glob.glob(os.path.join(repo, n)) for n in names)
    picks = [k for k, cond in (("python", has("pyproject.toml", "setup.py", "setup.cfg", "requirements*.txt", "pytest.ini")),
                               ("node", has("package.json")), ("go", has("go.mod")), ("java", has("pom.xml", "build.gradle*")),
                               ("dotnet", has("*.sln", "*.csproj"))) if cond] or list(TEST_GLOBS)
    out = []
    for k in picks:
        out += [g for g in TEST_GLOBS[k] if g not in out]
    return out


def github_remote(repo):
    """(owner, name) of the repo's GitHub remote (origin first), or None."""
    pat = re.compile(r"^(?:https:/{2}(?:[^@/]+@)?github\.com/|git@github\.com:|ssh://git@github\.com/)([^/\s]+)/([^/\s]+?)(?:\.git)?/?$")
    try:
        names = subprocess.run(["git", "-C", repo, "remote"], capture_output=True, text=True, timeout=10).stdout.split()
    except Exception:
        return None
    for n in (["origin"] if "origin" in names else []) + [x for x in names if x != "origin"]:
        url = subprocess.run(["git", "-C", repo, "remote", "get-url", n], capture_output=True, text=True, timeout=10).stdout.strip()
        m = pat.match(url)
        if m:
            return m.group(1), m.group(2)
    return None


def protection_body():
    """D-253, D-260: the branch protection that makes workforce-proof the judge and the owner the only approval: both
    checks from GitHub Actions required on a branch up to date with the base (strict); one approving review (the
    owner's), stale approvals dismissed, the last push approved; no code-owner rule; admins not bound
    (enforce_admins false), so the owner can merge their own pull request by an admin override GitHub shows as a
    bypass, since GitHub does not let anyone approve their own; no force push or deletion."""
    return {"required_status_checks": {"strict": True, "checks": [{"context": c, "app_id": GITHUB_ACTIONS_APP_ID} for c in CI_CHECKS]},
            "enforce_admins": False,
            "required_pull_request_reviews": {"require_code_owner_reviews": False, "required_approving_review_count": 1,
                                              "dismiss_stale_reviews": True, "require_last_push_approval": True},
            "restrictions": None, "allow_force_pushes": False, "allow_deletions": False}


def protection_command(owner, name, branch):
    return ("gh api -X PUT repos/%s/%s/branches/%s/protection --input - <<'JSON'\n%s\nJSON" % (
        owner, name, branch, json.dumps(protection_body(), indent=2)))


def do_setup_branch_protection(repo, args):
    """D-253: run the branch-protection call with the person's own gh login (their terminal, not a session)."""
    gr = github_remote(repo)
    if not gr:
        die("no GitHub remote in %s; branch protection is set on GitHub" % repo)
    p = subprocess.run(["gh", "api", "repos/%s/%s" % gr], capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        die("gh could not read %s/%s (%s); sign in with gh auth login from your own terminal" % (gr[0], gr[1], p.stderr.strip()[:200]))
    branch = json.loads(p.stdout).get("default_branch") or "main"
    if args.dry_run:
        say("Dry run: would run:\n" + protection_command(gr[0], gr[1], branch))
        return 0
    p = subprocess.run(["gh", "api", "-X", "PUT", "repos/%s/%s/branches/%s/protection" % (gr[0], gr[1], branch), "--input", "-"],
                       input=json.dumps(protection_body()), capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        die("GitHub refused the branch protection for %s/%s %s: %s" % (gr[0], gr[1], branch, (p.stderr or p.stdout).strip()[:300]))
    say("branch protection set on %s/%s %s: head-suite and base-suite required (GitHub Actions, up to date with the "
        "base), one approving review required, stale approvals dismissed, the last push approved; admins can override "
        "(that is how the owner merges their own pull request). GitHub counts one approval from anyone with write access: keep write "
        "access to you and one agent or build account, so the approval is yours; /workforce-doctor lists who has it (D-273)"
        % (gr[0], gr[1], branch))
    return 0


def build_plan(repo, packs, mode, sandbox, values, market=None):
    plan = Plan()
    mname, msource = market or (MARKETPLACE, MARKETPLACE_SOURCE)
    plan.values = values
    eng = "engineering" in packs
    if mode in ("plugin", "copy"):
        if eng:
            for pack, src, dest in ENG_FILES:
                if pack not in packs:
                    die("the %s pack is needed for %s and was not found" % (pack, dest))
                path = os.path.join(packs[pack], src)
                if not os.path.isfile(path):
                    die("installed %s pack has no %s (re-install the pack)" % (pack, src))
                plan.files[dest] = (read_bytes(path), "%s/%s" % (pack, src))
            try:
                eng_settings = json.load(open(os.path.join(packs["engineering"], ENG_SETTINGS), encoding="utf-8"))
            except (OSError, ValueError) as exc:
                die("cannot read engineering %s: %s" % (ENG_SETTINGS, exc))
            plan.settings["hooks"] = eng_settings.get("hooks", {})
            plan.ignore.append(HOOK_LOG)
            plan.files[LIVE_ALLOW] = (b"", "workforce-init live-command allow list (empty)")
        if sandbox:
            plan.settings["sandbox"] = {"enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
                                        "filesystem": {"allowWrite": ["./"], "denyWrite": deny_write_paths(mode)}}
    elif sandbox:
        plan.notes.append("user mode writes no settings to the repo, so the sandbox was not turned on; "
                          "run /sandbox in Claude Code to turn it on for this project")
    if mode == "plugin":
        plan.settings["extraKnownMarketplaces"] = {mname: msource}
        plan.settings["enabledPlugins"] = dict(("%s@%s" % (PLUGIN_ID[p], mname), True)
                                              for p in PACKS if p in packs)
    if mode == "copy":
        if not eng:
            die("copy mode copies the engineering agents; the engineering pack was not found")
        plan.notes.append(COPY_MODE_NOTE)
        skill_dirs = {}
        for pack in ("core", "engineering"):
            sroot = os.path.join(packs.get(pack, ""), "skills")
            if os.path.isdir(sroot):
                for n in sorted(os.listdir(sroot)):
                    if os.path.isfile(os.path.join(sroot, n, "SKILL.md")):
                        skill_dirs.setdefault(n, (pack, os.path.join(sroot, n)))
        aroot = os.path.join(packs["engineering"], "agents")
        named = set()
        for fn in sorted(os.listdir(aroot)):
            if fn.endswith(".md"):
                b = read_bytes(os.path.join(aroot, fn))
                dest = ".claude/agents/" + fn
                plan.files[dest] = (b, "engineering/agents/" + fn)
                plan.copied[dest] = "engineering"
                named |= skill_names_in(b.decode("utf-8", "replace"), skill_dirs)
        for n in sorted(named):
            pack, sdir = skill_dirs[n]
            for root, _d, fs in os.walk(sdir):
                for f in sorted(fs):
                    full = os.path.join(root, f)
                    dest = ".claude/skills/%s/%s" % (n, os.path.relpath(full, sdir).replace(os.sep, "/"))
                    b = read_bytes(full)
                    if dest in plan.files and plan.files[dest][0] != b:
                        die("two sources for %s" % dest)
                    plan.files[dest] = (b, "%s/skills/%s/%s" % (pack, n, os.path.relpath(full, sdir)))
                    plan.copied[dest] = pack
        plan.files[GUARD] = (GUARD_TEXT.encode("utf-8"), "workforce-init guard")
        plan.files[GUARD_CI] = (GUARD_CI_TEXT.encode("utf-8"), "workforce-init guard CI job")
    return plan


def checksum_text(packs, sums, from_packs):
    """`# <pack>: <version>` per pack the copies came from, then `<sha256>  <path>` per copied file,
    sorted in C-locale byte order (the same order as `LC_ALL=C sort`)."""
    head = ["# %s: %s\n" % (p, pack_version(packs[p]) or "unknown") for p in PACKS if p in from_packs]
    body = sorted(("%s  %s\n" % (sha, path)).encode("utf-8") for path, sha in sums.items())
    return ("".join(head)).encode("utf-8") + b"".join(body)


# ---------------------------------------------------------------------------------------------
# applying a plan

class Writer(object):
    def __init__(self, repo, dry):
        self.repo, self.dry = repo, dry
        self.made_dirs = []

    def abs(self, rel):
        return os.path.join(self.repo, rel)

    def write(self, rel, data):
        if self.dry:
            return
        path = self.abs(rel)
        d = os.path.dirname(path)
        missing = []
        while d and not os.path.isdir(d):
            missing.append(d)
            d = os.path.dirname(d)
        for m in reversed(missing):
            os.mkdir(m)
            self.made_dirs.append(os.path.relpath(m, self.repo))
        with open(path, "wb") as fh:
            fh.write(data)
        if rel.endswith(".py"):
            os.chmod(path, 0o755)

    def delete(self, rel):
        if not self.dry:
            os.remove(self.abs(rel))


def load_installed(repo):
    p = os.path.join(repo, INSTALLED)
    if not os.path.isfile(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except ValueError as exc:
        die("%s is not valid JSON (%s); fix or delete it first" % (INSTALLED, exc))


# D-191 (audit 3 G8): the files that ARE the enforcement. A repo copy that differs from the pack's is never
# silently kept: the install stops (exit 3) unless --replace-enforcement, which keeps the old file as .bak.
# validate-verdicts.py and enforce-draft-gate.py run from the core plugin in every mode, so no mode writes
# them into a repo; they are listed so a repo copy (an older vendored install) is checked too.
ENFORCEMENT = ("protect-tier3.py", "validate-verdicts.py", "enforce-draft-gate.py", "validate_verdict.py",
               "verdict-schema.json")


def enforcement_conflicts(repo, plan, prior=None):
    """[(rel, repo sha256, pack sha256)] for every planned enforcement file whose repo copy differs from the
    pack's and is not an untouched copy from an earlier install (that one is updated as usual)."""
    prior_files = (prior or {}).get("files", {})
    out = []
    for rel in sorted(plan.files):
        if os.path.basename(rel) not in ENFORCEMENT:
            continue
        path = os.path.join(repo, rel)
        if not os.path.isfile(path):
            continue
        have, want = sha_file(path), sha_bytes(plan.files[rel][0])
        old = prior_files.get(rel)
        if have == want or (old and old.get("owned") and have == old.get("sha256")):
            continue
        out.append((rel, have, want))
    return out


def stop_on_enforcement(conflicts):
    say("STOPPED before writing anything: %d enforcement file(s) in this repo differ from the pack's." % len(conflicts))
    for rel, have, want in conflicts:
        say("  %s\n    repo sha256 %s\n    pack sha256 %s" % (rel, have, want))
    say("A changed enforcement file can switch a check off while every report says it is on. Nothing was changed.")
    say("To install the pack's file and keep the repo's as <name>.bak, run again with --replace-enforcement.")
    return 3


def apply_install(repo, packs, plan, mode, sandbox, dry, prior=None, market=None, replace=(), test=None):
    """Write the plan. Returns the installed-list record. `prior` (upgrade) carries ownership forward.
    `replace`: enforcement files to overwrite with the pack's copy, the old one kept as <name>.bak (D-191)."""
    w = Writer(repo, dry)
    prior_files = (prior or {}).get("files", {})
    rec = {"schema": SCHEMA, "mode": mode, "sandbox": bool(sandbox) and mode != "user", "marketplace": market,
           "date": datetime.date.today().isoformat(),
           "packs": dict((p, pack_version(packs[p])) for p in PACKS if p in packs),
           "pack_roots_seen": sorted(packs), "files": {}, "skipped": [], "made_dirs": list((prior or {}).get("made_dirs", []))}
    # D-194 (audit 3 G3): where the validator lives, so a skill never searches the disk for it. Plugin and
    # user modes: the installed core pack's folder (<core_root>/skills/gate-verdict-format/validate_verdict.py).
    # Copy mode: the repo copy's folder, `.claude` (same relative layout). engineering_root lets the doctor
    # compare the Tier-3 hook with the pack's (D-191).
    rec["core_root"] = ".claude" if mode == "copy" else os.path.realpath(packs["core"])
    # D-222: the command the Stop hook runs itself to check a quality PASS, and how long it may take.
    test = test or {}
    rec["test_cmd"] = test.get("cmd") or (prior or {}).get("test_cmd") or context_test_cmd(repo)
    rec["test_timeout"] = int(test.get("timeout") or (prior or {}).get("test_timeout") or TEST_TIMEOUT_DEFAULT)
    if not rec["test_cmd"]:
        rec.pop("test_cmd")
    # D-251: the test files workforce-proof's base-suite puts back; D-254: whether CI is the judge (absent = yes)
    rec["test_globs"] = test.get("globs") or (prior or {}).get("test_globs") or default_test_globs(repo)
    if test.get("no_ci_judge") or ((prior or {}).get("ci_judge") is False and not test.get("ci_judge")):
        rec["ci_judge"] = False
    if "engineering" in packs and mode != "copy":
        rec["engineering_root"] = os.path.realpath(packs["engineering"])
    # D-273 (Amendment 10, Y6): GitHub counts one approval from anyone with write access, so the install records who is meant to have
    # it: the owner's GitHub login and the agent or build accounts. The doctor lists everyone with write, maintain or admin and FAILs on
    # anyone else. Never read from gh here (a session's gh is the build account, not the owner).
    owner = (test.get("owner_login") or (prior or {}).get("owner_login") or "").strip()
    agents = sorted(set(x.strip() for x in (list(test.get("agent_accounts") or []) + list((prior or {}).get("agent_accounts") or [])) if x and x.strip()))
    if owner:
        rec["owner_login"] = owner
    if agents:
        rec["agent_accounts"] = agents
    report = []

    # plain files
    for rel in sorted(plan.files):
        data, label = plan.files[rel]
        path = w.abs(rel)
        want = sha_bytes(data)
        old = prior_files.get(rel)
        if rel in replace and os.path.isfile(path):
            w.write(rel + ".bak", read_bytes(path))
            w.write(rel, data)
            rec["files"][rel] = {"sha256": want, "owned": True, "kind": "file", "from": label}
            report.append("replaced %s (the repo's copy kept as %s.bak)" % (rel, rel))
            continue
        if os.path.isfile(path):
            have = sha_file(path)
            if old and old.get("owned"):
                if have == want:
                    rec["files"][rel] = dict(old, sha256=want)
                    continue
                if have == old.get("sha256"):     # ours and unchanged since install: update it
                    w.write(rel, data)
                    rec["files"][rel] = {"sha256": want, "owned": True, "kind": "file", "from": label}
                    report.append("updated  %s" % rel)
                    continue
                rec["files"][rel] = dict(old)      # ours, but you changed it: keep yours
                rec["skipped"].append(rel)
                report.append("KEPT     %s (changed since install; not overwritten)" % rel)
                continue
            if have == want:                       # already there, same bytes, not ours
                rec["files"][rel] = {"sha256": want, "owned": False, "kind": "file", "from": label}
                report.append("present  %s (already identical; left as yours)" % rel)
                continue
            rec["skipped"].append(rel)
            report.append("SKIPPED  %s (a different file already exists; not overwritten)" % rel)
            continue
        w.write(rel, data)
        rec["files"][rel] = {"sha256": want, "owned": True, "kind": "file", "from": label}
        report.append("wrote    %s" % rel)

    # copy mode checksum file, over the copies that are actually in place as ours
    if mode == "copy":
        # A copy you changed since install stays listed at its installed sha256, so the guard flags
        # it; a repo-owned file at a pack path (skipped, never ours) is not listed.
        copied = {}
        for rel in plan.copied:
            e = rec["files"].get(rel)
            if e and e.get("owned"):
                copied[rel] = e["sha256"]
        data = checksum_text(packs, copied, set(plan.copied[r] for r in copied))
        path = w.abs(CHECKSUMS)
        old = prior_files.get(CHECKSUMS)
        if os.path.isfile(path) and not (old and old.get("owned")):
            rec["skipped"].append(CHECKSUMS)
            report.append("SKIPPED  %s (exists and is not from this command)" % CHECKSUMS)
        else:
            w.write(CHECKSUMS, data)
            rec["files"][CHECKSUMS] = {"sha256": sha_bytes(data), "owned": True, "kind": "file", "from": "checksums"}
            report.append("wrote    %s (%d copied files)" % (CHECKSUMS, len(copied)))
        rec["copied"] = sorted(copied)

    # settings.json merge
    if plan.settings:
        path = w.abs(SETTINGS)
        old = prior_files.get(SETTINGS)
        existed = os.path.isfile(path)
        if existed:
            raw = read_bytes(path)
            try:
                cur = json.loads(raw.decode("utf-8")) if raw.strip() else {}
            except ValueError:
                cur = None
            if not isinstance(cur, dict):
                rec["skipped"].append(SETTINGS)
                report.append("SKIPPED  %s (not a JSON object; merge these keys by hand: %s)"
                              % (SETTINGS, ", ".join(sorted(plan.settings))))
                cur = None
        else:
            raw, cur = None, {}
        if cur is not None:
            base_ops = (old or {}).get("ops", []) if old else []
            merged, ops = merge_settings(cur, plan.settings)
            if ops or not old:
                data = json_text(merged).encode("utf-8") if (ops or not existed) else raw
                if ops:
                    w.write(SETTINGS, data)
                entry = {"kind": "json-merge", "owned": not existed if not old else old.get("owned"),
                         "ops": base_ops + [list(o) for o in ops], "sha256": sha_bytes(data)}
                if old and "original" in old:
                    entry["original"] = old["original"]
                elif existed and not old:          # a file the install found, not one an earlier install created
                    entry["original"] = raw.decode("utf-8")
                rec["files"][SETTINGS] = entry
                report.append(("merged   %s (%d key(s) added)" % (SETTINGS, len(ops))) if ops
                              else "present  %s (nothing to add)" % SETTINGS)
            else:
                rec["files"][SETTINGS] = dict(old, sha256=sha_bytes(raw))
    elif prior_files.get(SETTINGS):
        rec["files"][SETTINGS] = prior_files[SETTINGS]

    # .gitignore: the hook's log stays out of git status (D-162)
    if plan.ignore:
        path = w.abs(GITIGNORE)
        old = prior_files.get(GITIGNORE)
        existed = os.path.isfile(path)
        data = read_bytes(path) if existed else b""
        have = set(l.strip() for l in data.splitlines())
        missing = [l for l in plan.ignore if l.encode("utf-8") not in have]
        if missing:
            added = (b"\n" if data and not data.endswith(b"\n") else b"") + "".join(l + "\n" for l in missing).encode("utf-8")
            new = data + added
            w.write(GITIGNORE, new)
            rec["files"][GITIGNORE] = {"kind": "gitignore-lines", "owned": old.get("owned") if old else not existed,
                                       "lines": sorted(set((old or {}).get("lines", []) + missing)),
                                       "added": added.decode("utf-8"), "sha256": sha_bytes(new)}
            report.append("%s %s (%s)" % ("edited  " if existed else "wrote   ", GITIGNORE, ", ".join(missing)))
        elif old:
            rec["files"][GITIGNORE] = dict(old, sha256=sha_bytes(data))
        else:
            report.append("present  %s (already ignores %s)" % (GITIGNORE, ", ".join(plan.ignore)))
    elif prior_files.get(GITIGNORE):
        rec["files"][GITIGNORE] = prior_files[GITIGNORE]

    # project values in BUSINESS-CONTEXT.md
    vals = dict((k, v) for k, v in plan.values.items() if v)
    if vals:
        path = w.abs(CONTEXT)
        old = prior_files.get(CONTEXT)
        existed = os.path.isfile(path)
        text = open(path, encoding="utf-8").read() if existed else ""
        new, rows, kept = context_with_values(text, vals)
        for k in kept:
            report.append("kept     %s row %s (already set; not changed)" % (CONTEXT, k))
        if rows:
            w.write(CONTEXT, new.encode("utf-8"))
            entry = {"kind": "context-rows", "owned": (not existed) if not old else old.get("owned"),
                     "rows": (old or {}).get("rows", []) + rows, "sha256": sha_bytes(new.encode("utf-8"))}
            if old and "original" in old:
                entry["original"] = old["original"]
            elif existed and not old:
                entry["original"] = text
            rec["files"][CONTEXT] = entry
            report.append("%s %s (%s)" % ("edited  " if existed else "wrote   ", CONTEXT,
                                           ", ".join(r.split("|")[1].strip() for r in rows)))
        elif old:
            rec["files"][CONTEXT] = dict(old, sha256=sha_bytes(text.encode("utf-8")))
    elif prior_files.get(CONTEXT):
        rec["files"][CONTEXT] = prior_files[CONTEXT]

    if not dry:
        w.write(INSTALLED, b"{}\n")             # creates .claude/ if needed, so it is recorded
        rec["made_dirs"] = sorted(set(rec["made_dirs"] + w.made_dirs))
        w.write(INSTALLED, json_text(rec).encode("utf-8"))
    report.append("wrote    %s" % INSTALLED)
    return rec, report


def do_remove(repo, dry):
    rec = load_installed(repo)
    if rec is None:
        die("no %s in %s; nothing to remove" % (INSTALLED, repo))
    w = Writer(repo, dry)
    report, kept = [], []
    for rel in sorted(rec.get("files", {})):
        e = rec["files"][rel]
        path = w.abs(rel)
        if not os.path.isfile(path):
            report.append("gone     %s (already removed)" % rel)
            continue
        have = sha_file(path)
        kind = e.get("kind", "file")
        if kind == "file":
            if not e.get("owned"):
                report.append("left     %s (was yours before the install)" % rel)
            elif have == e.get("sha256"):
                w.delete(rel)
                report.append("removed  %s" % rel)
            else:
                kept.append(rel)
                report.append("KEPT     %s (changed since install)" % rel)
        elif kind == "json-merge":
            if have == e.get("sha256") and "original" in e:
                w.write(rel, e["original"].encode("utf-8"))
                report.append("restored %s (to its content before the install)" % rel)
                continue
            if have == e.get("sha256") and e.get("owned"):
                w.delete(rel)
                report.append("removed  %s" % rel)
                continue
            try:
                cur = json.loads(read_bytes(path).decode("utf-8"))
            except ValueError:
                kept.append(rel)
                report.append("KEPT     %s (no longer valid JSON; remove the added keys by hand)" % rel)
                continue
            new, kk = unmerge_settings(cur, e.get("ops", []))
            if not new and e.get("owned"):
                w.delete(rel)
                report.append("removed  %s (only added keys were left)" % rel)
            else:
                w.write(rel, json_text(new).encode("utf-8"))
                report.append("edited   %s (added keys taken out; your other keys kept)" % rel)
            for k in kk:
                report.append("KEPT     %s key %s (you changed its value)" % (rel, k))
        elif kind == "context-rows":
            if have == e.get("sha256"):
                if "original" in e:
                    w.write(rel, e["original"].encode("utf-8"))
                    report.append("restored %s" % rel)
                elif e.get("owned"):
                    w.delete(rel)
                    report.append("removed  %s" % rel)
                continue
            text = open(path, encoding="utf-8").read()
            new, n = context_without_rows(text, e.get("rows", []))
            if n:
                w.write(rel, new.encode("utf-8"))
            report.append("edited   %s (%d added row(s) taken out; the rest kept)" % (rel, n))
        elif kind == "gitignore-lines":
            data = read_bytes(path)
            added = e.get("added", "").encode("utf-8")
            if added and data.endswith(added):        # nothing after our lines: back to the bytes before
                new = data[:-len(added)]
            else:                                      # you edited it since: take out only our lines
                keep, drop = [], set(e.get("lines", []))
                for line in data.splitlines(True):
                    s = line.decode("utf-8", "replace").strip()
                    if s in drop:
                        drop.discard(s)
                        continue
                    keep.append(line)
                new = b"".join(keep)
            if not new.strip() and e.get("owned"):
                w.delete(rel)
                report.append("removed  %s (only the added line was in it)" % rel)
            elif new != data:
                w.write(rel, new)
                report.append("edited   %s (added line taken out; your lines kept)" % rel)
    if not dry:
        os.remove(w.abs(INSTALLED))
    report.append("removed  %s" % INSTALLED)
    if not dry:
        for d in sorted(rec.get("made_dirs", []), key=lambda x: -x.count("/")):
            p = w.abs(d)
            try:
                if os.path.isdir(p) and not os.listdir(p):
                    os.rmdir(p)
            except OSError:
                pass
    return report, kept


def finish_notes(repo, packs, rec, mode, sandbox, args, by):
    """The sandbox sentence, the test command, and (plugin mode) the tamper baseline (D-222, D-223, D-231)."""
    if not sandbox or mode == "user":
        say("note: " + NO_SANDBOX_MSG)
        if mode == "plugin":
            say("note: " + NO_SANDBOX_TAMPER)
    if rec.get("test_cmd"):
        tc = rec["test_cmd"] if isinstance(rec["test_cmd"], list) else [rec["test_cmd"]]
        say("test command%s recorded: %s (the Stop hook runs %s to check a test-auditor or completion-auditor PASS; "
            "limit %d s)" % ("s" if len(tc) > 1 else "", ", ".join("`%s`" % x for x in tc), "each" if len(tc) > 1 else "it",
                             rec.get("test_timeout", TEST_TIMEOUT_DEFAULT)))
    else:
        say("note: no test command recorded; a test-auditor or completion-auditor PASS will be blocked until you run "
            "/workforce-init --upgrade --test-cmd \"<your test command>\"")
    if mode == "copy":
        say("note: " + COPY_NO_TAMPER)
        say("note: " + COPY_RUNNER_NOTE)
    if rec.get("ci_judge") is False:                          # D-254
        say("note: " + NO_CI_JUDGE_MSG)
    elif "engineering" in packs and mode in ("plugin", "copy"):     # D-253
        gr = github_remote(repo)
        if gr:
            say("CI is the judge: a test-auditor or completion-auditor PASS stands when workforce-proof's head-suite and "
                "base-suite pass on GitHub for the exact commit. Require both on the default branch (from your own "
                "terminal): /workforce-init --setup-branch-protection, which runs:\n" + protection_command(gr[0], gr[1], "<default branch>"))
            if rec.get("owner_login"):
                say("approval: GitHub counts one approval from anyone with write access. Keep write access to %s and one agent or build "
                    "account (%s), so the approval is yours; /workforce-doctor lists who has it (D-273)."
                    % (rec["owner_login"], ", ".join(rec.get("agent_accounts") or ["none recorded"])))
            else:
                say("approval: GitHub counts one approval from anyone with write access. Record whose it is, so /workforce-doctor can check who has "
                    "write access: /workforce-init --upgrade --owner-login <your GitHub login> --agent-account <build account> (D-273)")
        else:
            say("note: no GitHub remote: a test-auditor or completion-auditor PASS stays INCOMPLETE (no CI judge) until "
                "the repo is on GitHub with Actions on, or you run /workforce-init --upgrade --no-ci-judge")
    if mode != "plugin" or getattr(args, "dry_run", False):
        return
    data = plugin_data_dir(packs, getattr(args, "plugin_data", None))
    if not data:
        say("note: tamper baseline not written: the core plugin's data folder was not found")
        return
    try:
        old_rc = (json.load(open(os.path.join(data, TAMPER_BASELINE), encoding="utf-8")).get(repo) or {}).get("runner_config")
    except (OSError, ValueError, AttributeError):
        old_rc = None
    path = write_baseline(repo, data, mode, by, test_cmd=rec.get("test_cmd"))
    say("wrote    tamper baseline for this repo (%s)" % path)
    new_rc = (json.load(open(path, encoding="utf-8")).get(repo) or {}).get("runner_config")
    if new_rc is None:
        say("note: test runner config not recorded: more than %d files to walk" % RC_WALK_LIMIT)
    else:
        moved = _changed_keys(old_rc, new_rc) if old_rc is not None else []
        say("recorded test runner config: %d input(s)%s" % (len(new_rc), (
            "; changed since the last record, now accepted: " + ", ".join(moved)) if moved else ""))


def do_accept_changes(repo, packs, args):
    """D-231: record the enforcement files as they are now, after a change the human made."""
    rec = load_installed(repo)
    if rec is None:
        die("no %s in %s; run /workforce-init first" % (INSTALLED, repo))
    if rec.get("mode") != "plugin":
        die("--accept-changes is for plugin mode; %s mode keeps no tamper baseline" % rec.get("mode"))
    data = plugin_data_dir(packs, args.plugin_data)
    if not data:
        die("the core plugin's data folder was not found; nothing to update")
    try:
        old = (json.load(open(os.path.join(data, TAMPER_BASELINE), encoding="utf-8")).get(repo) or {}).get("files") or {}
    except (OSError, ValueError):
        old = {}
    now = enforcement_hashes(repo, "plugin")
    changed = sorted(r for r in set(old) | set(now) if old.get(r) != now.get(r))
    if args.dry_run:
        say("Dry run: would accept %d changed file(s): %s" % (len(changed), ", ".join(changed) or "none"))
        return 0
    path = write_baseline(repo, data, "plugin", "accept-changes", test_cmd=rec.get("test_cmd"), part="files")
    say("accepted %d changed enforcement file(s)%s; baseline rewritten (%s)" % (
        len(changed), (": " + ", ".join(changed)) if changed else "", path))
    return 0


def do_accept_runner_config(repo, packs, args):
    """D-233: record the test runner config as it is now, after a person reviewed the change."""
    rec = load_installed(repo)
    if rec is None:
        die("no %s in %s; run /workforce-init first" % (INSTALLED, repo))
    if rec.get("mode") != "plugin":
        die("--accept-runner-config is for plugin mode; %s mode checks the runner config against the base branch, so a "
            "reviewed change is accepted when it is merged there" % rec.get("mode"))
    data = plugin_data_dir(packs, args.plugin_data)
    if not data:
        die("the core plugin's data folder was not found; nothing to update")
    try:
        old = (json.load(open(os.path.join(data, TAMPER_BASELINE), encoding="utf-8")).get(repo) or {}).get("runner_config")
    except (OSError, ValueError, AttributeError):
        old = None
    now = runner_control_hashes(repo, rec.get("test_cmd"))
    if now is None:
        die("more than %d files to walk; the test runner config cannot be recorded" % RC_WALK_LIMIT)
    changed = _changed_keys(old, now)
    if args.dry_run:
        say("Dry run: would accept %d changed runner input(s): %s" % (len(changed), ", ".join(changed) or "none"))
        return 0
    path = write_baseline(repo, data, "plugin", "accept-runner-config", test_cmd=rec.get("test_cmd"), part="runner")
    say("accepted %d changed test runner input(s)%s; baseline rewritten (%s)" % (
        len(changed), (": " + ", ".join(changed)) if changed else "", path))
    return 0


def where_now(packs, rel):
    """For a copied agent no longer in engineering: the installed pack that ships it now, if any."""
    fn = os.path.basename(rel)
    if not rel.startswith(".claude/agents/"):
        return None
    for p in PACKS:
        if p in packs and os.path.isfile(os.path.join(packs[p], "agents", fn)):
            return p
    return None


def do_upgrade(repo, packs, args):
    prior = load_installed(repo)
    if prior is None:
        die("no %s in %s; run /workforce-init first" % (INSTALLED, repo))
    mode = prior.get("mode", "plugin")
    sandbox = prior.get("sandbox", False)
    market = prior.get("marketplace")
    market = tuple(market) if market else None
    plan = build_plan(repo, packs, mode, sandbox, {}, market)
    old_files = prior.get("files", {})
    added, changed, gone = [], [], []
    for rel in sorted(plan.files):
        if rel not in old_files:
            added.append(rel)
        elif old_files[rel].get("kind", "file") == "file" and old_files[rel].get("sha256") != sha_bytes(plan.files[rel][0]):
            changed.append(rel)
    for rel in sorted(old_files):
        if old_files[rel].get("kind", "file") == "file" and rel not in plan.files and rel != CHECKSUMS:
            gone.append(rel)
    say("Upgrade check (%s mode). Installed list: %s." % (mode, ", ".join("%s %s" % kv for kv in sorted(prior.get("packs", {}).items()))))
    say("Now installed: %s." % ", ".join("%s %s" % (p, pack_version(packs[p])) for p in PACKS if p in packs))
    say("New files the packs now ship: %d%s" % (len(added), "".join("\n  + " + r for r in added)))
    say("Files that changed in the packs: %d%s" % (len(changed), "".join("\n  ~ " + r for r in changed)))
    say("Files the packs no longer ship: %d%s" % (len(gone), "".join(
        "\n  - %s%s" % (r, (" (moved to the %s pack)" % where_now(packs, r)) if where_now(packs, r) else " (removed upstream)")
        for r in gone)))
    if gone and mode == "copy" and not args.confirm_removals:
        say("STOPPED before deleting anything. The copies above are no longer shipped by the newer packs.")
        say("Nothing was changed. To delete them and finish the upgrade, run again with --confirm-removals.")
        return 3
    if args.dry_run:
        say("Dry run: nothing written.")
        return 0
    conflicts = enforcement_conflicts(repo, plan, prior)
    if conflicts and not getattr(args, "replace_enforcement", False):
        return stop_on_enforcement(conflicts)
    rec, report = apply_install(repo, packs, plan, mode, sandbox, False, prior=prior, market=market,
                                replace={c[0] for c in conflicts},
                                test={"cmd": args.test_cmd, "timeout": args.test_timeout, "globs": args.test_glob,
                                      "no_ci_judge": args.no_ci_judge, "ci_judge": args.ci_judge,
                                      "owner_login": args.owner_login, "agent_accounts": args.agent_account})
    w = Writer(repo, False)
    for rel in gone:
        e = old_files[rel]
        path = w.abs(rel)
        if e.get("owned") and os.path.isfile(path):
            if sha_file(path) == e.get("sha256"):
                w.delete(rel)
                say("removed  %s" % rel)
            else:
                rec["files"][rel] = e
                say("KEPT     %s (changed since install)" % rel)
    with open(w.abs(INSTALLED), "wb") as fh:
        fh.write(json_text(rec).encode("utf-8"))
    for line in report:
        say(line)
    finish_notes(repo, packs, rec, mode, sandbox, args, "upgrade")
    say("Upgrade done. Next: run /workforce-doctor.")
    return 0


# ---------------------------------------------------------------------------------------------

# D-177 (audit 2 F3): what copy mode does not bring with it, printed on every copy-mode run.
COPY_MODE_NOTE = ("copy mode installs the agents, skills and the Tier-3 hook only; the Stop hook, draft gate, onboarding hook and the five slash commands come from the core plugin and are not present; use plugin mode or run the validator by hand.")


def one_or_list(cmds):
    """D-246: the --test-cmd values as recorded: None, one command, or a list of several."""
    cmds = [c.strip() for c in (cmds or []) if c and c.strip()]
    return None if not cmds else (cmds[0] if len(cmds) == 1 else cmds)


# D-247: a sandboxed session cannot write the files this script manages. macOS refuses with EPERM, the Linux sandbox's
# read-only mount with EROFS; both get the same guidance.
READ_ONLY_ERRNOS = (errno.EACCES, errno.EPERM, errno.EROFS)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Install, upgrade or remove the BlackRaptor Workforce in a repo.")
    ap.add_argument("--mode", choices=("plugin", "copy", "user"), default=None)
    ap.add_argument("--upgrade", action="store_true")
    ap.add_argument("--remove", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--replace-enforcement", action="store_true",
                    help="install the pack's enforcement file over a different repo copy, keeping the old one as <name>.bak")
    ap.add_argument("--confirm-removals", action="store_true", help="with --upgrade: delete copies the packs no longer ship")
    ap.add_argument("--sandbox", choices=("yes", "no"), default=None)
    ap.add_argument("--no-sandbox", action="store_true", help="same as --sandbox no: the enforcement files are not protected")
    ap.add_argument("--accept-changes", action="store_true",
                    help="plugin mode: record the enforcement files as they are now (after a change you made yourself)")
    ap.add_argument("--accept-runner-config", action="store_true",
                    help="plugin mode: record the test runner config as it is now (after you reviewed a change)")
    ap.add_argument("--test-glob", action="append",
                    help="a test-file glob for workforce-proof's base-suite; give it more than once (D-251)")
    ap.add_argument("--no-ci-judge", action="store_true",
                    help="no GitHub Actions: this machine's check is the judge, which an agent can fake (D-254)")
    ap.add_argument("--ci-judge", action="store_true", help="turn the CI judge back on after --no-ci-judge")
    ap.add_argument("--setup-branch-protection", action="store_true",
                    help="from your own terminal: require workforce-proof's two checks and the owner's approval (D-253, D-260)")
    ap.add_argument("--owner-login", help="your GitHub login: write access should stay with you and one agent account, so the approval is yours (recorded; the doctor checks who has write access, D-273, D-283)")
    ap.add_argument("--agent-account", action="append",
                    help="the GitHub login of the agent or build account that has write access (use one account; the doctor warns when more than one has it; recorded, D-273, D-283)")
    ap.add_argument("--test-timeout", type=int, help="seconds the Stop hook's own test run may take (default 300)")
    ap.add_argument("--plugin-data", help=argparse.SUPPRESS)   # test only: the core plugin's data folder
    ap.add_argument("--test-cmd", action="append",
                    help="the test command the Stop hook runs; give it more than once for several (D-246)")
    ap.add_argument("--lint-cmd")
    ap.add_argument("--typecheck-cmd")
    ap.add_argument("--suggest", action="store_true", help="print what was found and the suggested answers as JSON")
    ap.add_argument("--yes", action="store_true", help="ask nothing; take the defaults and suggestions")
    ap.add_argument("--repo")
    ap.add_argument("--pack-root", action="append", default=[], help=argparse.SUPPRESS)
    # test only: name a local marketplace folder instead of the published one (NAME=DIR)
    ap.add_argument("--marketplace", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    a.test_cmd = one_or_list(a.test_cmd)
    if a.no_ci_judge and a.ci_judge:
        die("choose one of --ci-judge or --no-ci-judge")
    if a.no_sandbox:
        if a.sandbox == "yes":
            die("choose one of --sandbox yes or --no-sandbox")
        a.sandbox = "no"
    market = None
    if a.marketplace:
        mname, _, mdir = a.marketplace.partition("=")
        if not mname or not mdir:
            die("--marketplace wants NAME=DIR")
        market = (mname, {"source": {"source": "directory", "path": os.path.realpath(mdir)}})
    repo = repo_root(a.repo)
    packs = find_packs(repo, a.pack_root)
    if "core" not in packs:
        die("the core pack was not found; install blackraptor-core first")

    if a.suggest:
        print(json.dumps({"repo": repo, "packs": dict((p, pack_version(r)) for p, r in packs.items()),
                          "installed": (load_installed(repo) or {}).get("mode"),
                          "suggested": dict({"mode": "plugin", "sandbox": "yes"}, **suggest_values(repo))}, indent=2))
        return 0
    if sum(map(bool, (a.remove, a.upgrade, a.accept_changes, a.accept_runner_config, a.setup_branch_protection))) > 1:
        die("choose one of --upgrade, --remove, --accept-changes, --accept-runner-config or --setup-branch-protection")
    if a.setup_branch_protection:
        return do_setup_branch_protection(repo, a)
    if a.accept_changes:
        return do_accept_changes(repo, packs, a)
    if a.accept_runner_config:
        return do_accept_runner_config(repo, packs, a)
    if a.remove:
        rec_before = load_installed(repo) or {}
        report, kept = do_remove(repo, a.dry_run)
        data = plugin_data_dir(packs, a.plugin_data)
        if not a.dry_run and rec_before.get("mode") == "plugin" and data and os.path.isfile(os.path.join(data, TAMPER_BASELINE)):
            write_baseline(repo, data, "plugin", "remove", remove=True)
            report.append("removed  this repo's tamper baseline (%s)" % os.path.join(data, TAMPER_BASELINE))
        for line in report:
            say(line)
        if kept:
            say("Kept %d file(s) you changed since the install; delete them yourself if you want them gone." % len(kept))
        say("Dry run: nothing written." if a.dry_run else "Removed.")
        return 0
    if a.upgrade:
        return do_upgrade(repo, packs, a)

    if load_installed(repo) is not None:
        die("this repo already has %s; use --upgrade, or --remove first" % INSTALLED)
    interactive = sys.stdin.isatty() and not a.yes and a.mode is None and a.sandbox is None and not a.test_cmd
    sug = suggest_values(repo)
    mode, sandbox = a.mode, a.sandbox
    vals = {"TEST_CMD": " ; ".join(a.test_cmd) if isinstance(a.test_cmd, list) else a.test_cmd, "LINT_CMD": a.lint_cmd,
            "TYPECHECK_CMD": a.typecheck_cmd}
    if interactive:
        mode = (input("Install mode: plugin, copy or user [plugin]: ").strip() or "plugin")
        if mode not in ("plugin", "copy", "user"):
            die("mode must be plugin, copy or user")
        sandbox = (input("Turn on Claude Code's sandbox for this project? [yes]: ").strip().lower() or "yes")
        t = input("Test command [%s]: " % sug.get("TEST_CMD", "none")).strip()
        vals["TEST_CMD"] = t or sug.get("TEST_CMD")
        for k in ("LINT_CMD", "TYPECHECK_CMD"):
            if sug.get(k):
                vals[k] = sug[k]
    else:
        for k in VALUE_SLOTS:
            if not vals.get(k) and sug.get(k):
                vals[k] = sug[k]
    mode = mode or "plugin"
    sandbox = (sandbox or "yes") in ("yes", "y", "true")
    plan = build_plan(repo, packs, mode, sandbox, vals, market)
    say("Installing the Workforce in %s mode into %s%s." % (mode, repo, " (dry run)" if a.dry_run else ""))
    say("Packs found: %s." % ", ".join("%s %s" % (p, pack_version(packs[p])) for p in PACKS if p in packs))
    conflicts = enforcement_conflicts(repo, plan)
    if conflicts and not a.replace_enforcement:
        return stop_on_enforcement(conflicts)
    rec, report = apply_install(repo, packs, plan, mode, sandbox, a.dry_run, market=market,
                                replace={c[0] for c in conflicts},
                                test={"cmd": a.test_cmd or vals.get("TEST_CMD"), "timeout": a.test_timeout, "globs": a.test_glob,
                                      "no_ci_judge": a.no_ci_judge, "ci_judge": a.ci_judge,
                                      "owner_login": a.owner_login, "agent_accounts": a.agent_account})
    for line in report:
        say(line)
    for n in plan.notes:
        say("note: " + n)
    finish_notes(repo, packs, rec, mode, sandbox, a, "install")
    if rec["skipped"]:
        say("Skipped %d file(s) that already existed with other content. Merge them by hand if you need them." % len(rec["skipped"]))
    say("Dry run: nothing written." if a.dry_run else "Done. Next: run /workforce-doctor. Commit the files listed above.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OSError as exc:
        # D-223, D-247: with the sandbox on, a shell command in a session cannot write the files this script manages.
        if exc.errno not in READ_ONLY_ERRNOS:
            raise
        die("cannot write %s (%s). With the sandbox on, run this from your own terminal, not from Claude Code:\n  "
            "python3 %s %s" % (getattr(exc, "filename", "") or "a protected file", exc.strerror or exc,
                               os.path.realpath(__file__), " ".join(sys.argv[1:])))
