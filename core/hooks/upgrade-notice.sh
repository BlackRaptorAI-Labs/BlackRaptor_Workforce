#!/bin/bash
# BlackRaptor Core — the upgrade notice, a SessionStart hook (2.8.3, D-239).
#
# WHY. From 2.8.3 the Stop hook runs the repo's recorded test command itself before it lets a test-auditor or
# completion-auditor PASS stand, and it needs the runner-config baseline /workforce-init writes. A user who only
# bumps the plugin and never re-runs /workforce-init gets every such PASS blocked, with nothing said up front.
# This hook says it once per session, to the user (systemMessage, not added to the model's context), when the
# repo's install record is older than the running core pack or has no test command. Silent otherwise, and in a
# repo with no install record.
#
# D-282 (Amendment 11, Z5): it also says so when the install record is current but this machine's tamper baseline for the repo is
# missing (the baseline file, or this repo's entry in it), because from then on a turn that dispatched an agent is blocked with
# "tamper baseline missing" (D-270, D-281). A repo cloned onto a second machine is the usual case. Silent when no plugin data folder
# can be found (copy mode, or not run by the plugin).
#
# SWITCH. BR_HOOKS=off turns it off with every other core hook (br-hooks-env.sh).
# FAIL-OPEN: any error prints nothing and exits 0.
HERE="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
if [ -f "$HERE/br-hooks-env.sh" ]; then
  . "$HERE/br-hooks-env.sh"
  br_hook_disabled "" "upgrade-notice SessionStart hook" "an out-of-date install is not announced this session." && exit 0
fi
{
  BR_PLUGIN_JSON="$HERE/../.claude-plugin/plugin.json" BR_PROJECT="${CLAUDE_PROJECT_DIR:-$PWD}" python3 -I -c '
import json, os, re
try:
    rec = json.load(open(os.path.join(os.environ["BR_PROJECT"], ".claude", "workforce-installed.json"), encoding="utf-8"))
    ver = str(json.load(open(os.environ["BR_PLUGIN_JSON"], encoding="utf-8"))["version"])
except Exception:
    raise SystemExit(0)
num = lambda v: tuple(int(x) for x in re.findall(r"\d+", str(v or "0"))[:3])
have = (rec.get("packs") or {}).get("core") if isinstance(rec, dict) else None
if not isinstance(rec, dict):
    raise SystemExit(0)
if not (rec.get("test_cmd") and have and num(have) >= num(ver)):
    print(json.dumps({"systemMessage": "Workforce %s needs /workforce-init --upgrade in this repo (run it from your own terminal). "
                      "Until then test-auditor and completion-auditor passes are blocked." % ver}))
    raise SystemExit(0)
if rec.get("mode") != "plugin":
    raise SystemExit(0)
import subprocess
data = os.environ.get("CLAUDE_PLUGIN_DATA")
if not data:
    m = re.match(r"^(.*)/plugins/cache/([^/]+)/([^/]+)/[^/]+/?$", os.path.realpath(os.environ.get("CLAUDE_PLUGIN_ROOT") or "/-"))
    if m:
        data = os.path.join(m.group(1), "plugins", "data", re.sub(r"[^A-Za-z0-9_.-]", "-", "%s-%s" % (m.group(3), m.group(2))))
if not data:
    raise SystemExit(0)
proj = os.path.realpath(os.environ["BR_PROJECT"])
try:
    p = subprocess.run(["git", "-C", proj, "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=5)
    root = os.path.realpath(p.stdout.strip()) if p.returncode == 0 and p.stdout.strip() else proj
except Exception:
    root = proj
try:
    have_entry = isinstance(json.load(open(os.path.join(data, "tamper-baseline.json"), encoding="utf-8")).get(root), dict)
except FileNotFoundError:
    have_entry = False
except Exception:
    raise SystemExit(0)
if not have_entry:
    print(json.dumps({"systemMessage": "Workforce %s: this machine has no tamper baseline for this repo, so a turn that dispatched an agent "
                      "will be blocked (\"tamper baseline missing\"). Run /workforce-init --upgrade from your own terminal." % ver}))
'
} 2>/dev/null || true
exit 0
