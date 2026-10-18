#!/usr/bin/env python3
"""workforce_init.py: install, upgrade or remove the BlackRaptor Workforce in a repo.

Run by the core command /workforce-init. Python 3 standard library only.

  python3 workforce_init.py [--mode plugin|copy|user] [--sandbox yes|no]
                            [--test-cmd CMD] [--lint-cmd CMD] [--typecheck-cmd CMD]
                            [--upgrade [--confirm-removals]] [--remove] [--dry-run]
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

Exit codes: 0 done; 1 usage or environment error; 3 stopped (upgrade needs confirmation, or a
check failed). Nothing is written on --dry-run or on exit 3.
"""

from __future__ import print_function

import argparse
import datetime
import hashlib
import json
import os
import re
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
MARKETPLACE = "blackraptor"
MARKETPLACE_SOURCE = {"source": {"source": "github", "repo": "BlackRaptorAI-Labs/BlackRaptor_Workforce"}}
PACKS = ["core", "engineering", "council", "marketing", "hardware"]
PLUGIN_ID = dict((p, "blackraptor-" + p) for p in PACKS)
VALUE_SLOTS = ["TEST_CMD", "LINT_CMD", "TYPECHECK_CMD"]

# The engineering repo files: (path inside the pack, path in the repo). CUSTOMIZATION.md section 1.
ENG_FILES = [
    ("engineering", "claude/hooks/protect-tier3.py", ".claude/hooks/protect-tier3.py"),
    ("engineering", "github/change-record-required.yml", ".github/workflows/change-record-required.yml"),
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


def skill_names_in(text, names):
    return set(n for n in names if re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(n), text))


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
            plan.settings["sandbox"] = {"enabled": True, "filesystem": {"allowWrite": ["./"]}}
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


def apply_install(repo, packs, plan, mode, sandbox, dry, prior=None, market=None, replace=()):
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
    if "engineering" in packs and mode != "copy":
        rec["engineering_root"] = os.path.realpath(packs["engineering"])
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
                elif existed:
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
            elif existed:
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
                                replace={c[0] for c in conflicts})
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
    say("Upgrade done. Next: run /workforce-doctor.")
    return 0


# ---------------------------------------------------------------------------------------------

# D-177 (audit 2 F3): what copy mode does not bring with it, printed on every copy-mode run.
COPY_MODE_NOTE = ("copy mode installs the agents, skills and the Tier-3 hook only; the Stop hook, draft gate, onboarding hook and the five slash commands come from the core plugin and are not present; use plugin mode or run the validator by hand.")


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
    ap.add_argument("--test-cmd")
    ap.add_argument("--lint-cmd")
    ap.add_argument("--typecheck-cmd")
    ap.add_argument("--suggest", action="store_true", help="print what was found and the suggested answers as JSON")
    ap.add_argument("--yes", action="store_true", help="ask nothing; take the defaults and suggestions")
    ap.add_argument("--repo")
    ap.add_argument("--pack-root", action="append", default=[], help=argparse.SUPPRESS)
    # test only: name a local marketplace folder instead of the published one (NAME=DIR)
    ap.add_argument("--marketplace", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
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
    if a.remove and a.upgrade:
        die("choose one of --upgrade or --remove")
    if a.remove:
        report, kept = do_remove(repo, a.dry_run)
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
    vals = {"TEST_CMD": a.test_cmd, "LINT_CMD": a.lint_cmd, "TYPECHECK_CMD": a.typecheck_cmd}
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
                                replace={c[0] for c in conflicts})
    for line in report:
        say(line)
    for n in plan.notes:
        say("note: " + n)
    if rec["skipped"]:
        say("Skipped %d file(s) that already existed with other content. Merge them by hand if you need them." % len(rec["skipped"]))
    say("Dry run: nothing written." if a.dry_run else "Done. Next: run /workforce-doctor. Commit the files listed above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
