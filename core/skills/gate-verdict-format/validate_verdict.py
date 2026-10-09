#!/usr/bin/env python3
"""R11 verdict validator — the machine the governance layer was missing.

Extracts every ```verdict fenced block from a file (a Change Record, or an agent's
output) and validates each against verdict-schema.json — the schema is LOADED and
ENFORCED (types, enums, required keys, additionalProperties, minItems, minLength,
string `pattern`, and the verdict-conditional rules), not merely referenced. Hand-rolled against the schema
JSON so it runs with no external deps (the CI runner and an orchestrator subagent
both have plain python3, not necessarily `jsonschema`).

  exit 0  — all verdict blocks present and well-formed
  exit 1  — a malformed / missing-field / bad-type / extra-key / rubber-stamp block
  exit 3  — no verdict blocks found (only an error when --require is passed)

Also summarizes the aggregate gate state (all PASS / has CONCERNS / has FAIL) so an
orchestrator can enforce "fail-closed until every gate shows PASS", and a FAIL
surfaces the §5 risk-acceptance requirement.

Usage: validate_verdict.py <file.md> [--require] [--json]
"""
import json
import re
import sys
from pathlib import Path

# Indent-tolerant: a ```verdict fence nested under a list item / inside <details>
# is indented. The CI (change-record-required.yml) shells out to THIS file, so there
# is no second regex implementation to keep in sync.
FENCE = re.compile(r"^[ \t]*```verdict[ \t]*\n(.*?)\n[ \t]*```", re.S | re.M)

SCHEMA_PATH = Path(__file__).with_name("verdict-schema.json")

# The exact literal strings the CR template ships. A copy that changes only
# verdict '___' → PASS but leaves these is a two-character rubber stamp; reject them.
TEMPLATE_PLACEHOLDERS = {
    "file:line — basis",
    "CITED file:line@sha — basis",   # the v3.1 Change Record form placeholder
    "the one fact that would flip this",
    "PR #___",
    "PR #___ / <files>",
    "...",
    "___",
}


def load_schema():
    try:
        return json.loads(SCHEMA_PATH.read_text())
    except Exception as e:  # a validator that can't load its schema must not pass silently
        print(f"FATAL: cannot load verdict-schema.json ({e})", file=sys.stderr)
        sys.exit(2)


def _type_ok(val, jtype):
    if jtype == "string":
        return isinstance(val, str)
    if jtype == "array":
        return isinstance(val, list)
    if jtype == "object":
        return isinstance(val, dict)
    if jtype == "integer":
        # bool is a subclass of int in Python; `true` is not a confidence score.
        return isinstance(val, int) and not isinstance(val, bool)
    return True


def _standards_item_errs(item, idx, i):
    """schema v3 `standards[]`: either the literal no-standard string, or a full citation.

    A designation with no access and no verification date is a memory, not a citation — the whole
    point of the field. Both branches are checked here because the hand-rolled validator does not
    implement oneOf generically."""
    if isinstance(item, str):
        if re.match(r"^none: practice applied: \S", item):
            return []
        return [f"block {idx}: standards[{i}] string must read "
                f"'none: practice applied: <the practice>', got {item!r}"]
    if not isinstance(item, dict):
        return [f"block {idx}: standards[{i}] must be a citation object or the "
                f"'none: practice applied: ...' string"]
    errs = []
    required = ("designation", "edition", "clause", "access", "verified")
    for k in required:
        if k not in item:
            errs.append(f"block {idx}: standards[{i}] missing '{k}' "
                        f"(a designation without {k} is not a citation)")
        elif not isinstance(item[k], str) or not item[k].strip():
            errs.append(f"block {idx}: standards[{i}].{k} must be a non-blank string")
    for k in item:
        if k not in required:
            errs.append(f"block {idx}: standards[{i}] unknown key '{k}'")
    v = item.get("verified")
    if isinstance(v, str) and v.strip() and not re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", v):
        errs.append(f"block {idx}: standards[{i}].verified must be YYYY-MM-DD, got {v!r}")
    return errs


def validate_block(obj, idx, schema):
    errs = []
    if not isinstance(obj, dict):
        return [f"block {idx}: not a JSON object"]
    props = schema.get("properties", {})

    # additionalProperties: false — reject unknown keys (e.g. an "evidance" typo)
    if schema.get("additionalProperties") is False:
        for k in obj:
            if k not in props:
                errs.append(f"block {idx}: unknown key '{k}' (schema forbids additional properties)")

    # required
    for k in schema.get("required", []):
        if k not in obj:
            errs.append(f"block {idx}: missing required field '{k}'")

    # per-property type / enum / minItems / minLength / item-types
    for k, v in obj.items():
        spec = props.get(k)
        if spec is None:
            continue
        if "enum" in spec and v not in spec["enum"]:
            errs.append(f"block {idx}: {k} '{v}' not one of {spec['enum']}")
        if "type" in spec and not _type_ok(v, spec["type"]):
            errs.append(f"block {idx}: {k} must be of type {spec['type']}, got {type(v).__name__}")
            continue  # further checks assume the right type
        if spec.get("type") == "array":
            mi = spec.get("minItems")
            if mi is not None and len(v) < mi:
                errs.append(f"block {idx}: {k}[] needs at least {mi} item(s)")
            it = spec.get("items", {}).get("type")
            if it and not all(_type_ok(i, it) for i in v):
                errs.append(f"block {idx}: every {k}[] item must be a {it}")
            ipat = spec.get("items", {}).get("pattern")
            if ipat is not None:
                for i in v:
                    if isinstance(i, str) and re.search(ipat, i) is None:
                        errs.append(f"block {idx}: every {k}[] item must match /{ipat}/ (e.g. non-blank — a whitespace-only string is not evidence)")
        if spec.get("type") == "integer":
            lo, hi = spec.get("minimum"), spec.get("maximum")
            if lo is not None and v < lo:
                errs.append(f"block {idx}: {k} must be >= {lo}, got {v}")
            if hi is not None and v > hi:
                errs.append(f"block {idx}: {k} must be <= {hi}, got {v}")
        if k == "standards" and isinstance(v, list):
            for i, item in enumerate(v):
                errs.extend(_standards_item_errs(item, idx, i))
        if spec.get("type") == "string":
            ml = spec.get("minLength")
            if ml is not None and len(v) < ml:
                errs.append(f"block {idx}: {k} must be at least {ml} char(s)")
            pat = spec.get("pattern")
            if pat is not None and re.search(pat, v) is None:
                if k == "evidence" and pat.startswith("^(MEASURED"):
                    errs.append(f"block {idx}: evidence must open with a provenance label — MEASURED, CITED, "
                                f"COMPUTED, ESTIMATED or ASSUMED (schema v3.1) — got '{v[:40]}'")
                else:
                    errs.append(f"block {idx}: {k} must match /{pat}/ (e.g. non-blank — not just whitespace)")

    # verdict-conditional rules (schema allOf, hand-applied)
    v = obj.get("verdict")
    if v in ("CONCERNS", "FAIL"):
        c = obj.get("conditions")
        if not isinstance(c, list) or len(c) == 0:
            errs.append(f"block {idx}: verdict {v} requires a non-empty conditions[] (array)")
    if v in ("COULD_NOT_ASSESS", "COULD NOT ASSESS") and not obj.get("reason"):
        errs.append(f"block {idx}: verdict {v} requires a one-line 'reason' "
                    f"(what blocked the assessment, and what would unblock it)")
    if v == "N/A":
        errs.append(f"block {idx}: 'N/A' is not a verdict in schema v3. A gate that does not apply "
                    f"emits no verdict block; the Change Record row carries the N/A and its reason.")

    # anti-rubber-stamp: reject the unmodified CR-template placeholder strings
    for field in ("artifact", "falsifier"):
        val = obj.get(field)
        if isinstance(val, str) and val.strip() in TEMPLATE_PLACEHOLDERS:
            errs.append(f"block {idx}: {field} is an unfilled template placeholder ('{val}')")
    ev = obj.get("evidence")
    if isinstance(ev, str) and ev.strip() in TEMPLATE_PLACEHOLDERS:
        errs.append(f"block {idx}: evidence is an unfilled template placeholder ('{ev}')")
    elif isinstance(ev, list):
        # schema v2 shipped evidence as an array. Name the migration rather than failing on a
        # bare type error, so a stale gate body gets a fixable message.
        errs.append(f"block {idx}: evidence must be a string in schema v3 (it was an array in v2) "
                    f"— join the citations into one line")
    return errs


def aggregate_state(verdicts):
    """The aggregate gate state over a list of verdict strings. COULD_NOT_ASSESS (the canonical
    machine form) is normalised to the spaced form first (2.3.2, audit F8): without that, a file whose
    only blocker was COULD_NOT_ASSESS reported HAS_CONCERNS."""
    verdicts = ["COULD NOT ASSESS" if v == "COULD_NOT_ASSESS" else v for v in verdicts]
    # N/A is neutral (gate does not apply); COULD NOT ASSESS is BLOCKING — it stays in non_na
    non_na = [v for v in verdicts if v != "N/A"]
    if not non_na:
        return "N/A"
    if all(v == "PASS" for v in non_na):
        return "ALL_PASS"
    if any(v == "FAIL" for v in non_na):
        return "HAS_FAIL"
    if any(v == "COULD NOT ASSESS" for v in non_na):
        return "HAS_COULD_NOT_ASSESS"
    return "HAS_CONCERNS"


def self_test():
    """Run the fixture set. A validator nobody tests is a claim, not a control.

    fixtures/EXPECTATIONS.json records the intended outcome per fixture; every valid fixture must
    pass and every invalid one must fail. A silently-loosened rule shows up here as a fixture that
    stopped failing."""
    fx = SCHEMA_PATH.parent / "fixtures"
    exp_path = fx / "EXPECTATIONS.json"
    if not exp_path.exists():
        print("FATAL: no fixtures/EXPECTATIONS.json", file=sys.stderr)
        return 2
    expectations = json.loads(exp_path.read_text())
    schema = load_schema()
    bad = 0
    for name in sorted(expectations):
        want = expectations[name]
        # An expectation is "PASS"/"FAIL", or {"valid": "PASS"|"FAIL", "state": "<aggregate>"} for a
        # fixture that also pins the aggregate state (2.3.2, audit F8).
        want_state = want.get("state") if isinstance(want, dict) else None
        want = want["valid"] if isinstance(want, dict) else want
        text = (fx / name).read_text()
        errs, verdicts = [], []
        for i, raw in enumerate(FENCE.findall(text), 1):
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as e:
                errs.append(f"block {i}: invalid JSON ({e})")
                continue
            errs.extend(validate_block(obj, i, schema))
            if isinstance(obj, dict) and obj.get("verdict"):
                verdicts.append(obj["verdict"])
        got = "FAIL" if errs else "PASS"
        ok = (got == want)
        if want_state is not None:
            got_state = aggregate_state(verdicts)
            if got_state != want_state:
                ok = False
                errs.append(f"aggregate state {got_state}, expected {want_state}")
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'BAD '} {name:<42} want {want:<4} got {got}")
        if not ok:
            for e in errs:
                print(f"         {e}")
        elif want == "FAIL":
            print(f"         caught: {errs[0]}")
    print(f"\n  {len(expectations) - bad}/{len(expectations)} fixtures behaved as expected")
    return 1 if bad else 0


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if "--self-test" in flags:
        return self_test()
    if not args:
        print("usage: validate_verdict.py <file.md> [--require] [--json] | --self-test",
              file=sys.stderr)
        return 2
    schema = load_schema()
    text = Path(args[0]).read_text()
    raw_blocks = FENCE.findall(text)

    if not raw_blocks:
        msg = {"blocks": 0, "ok": "--require" not in flags, "errors": ["no ```verdict blocks found"]}
        if "--json" in flags:
            print(json.dumps(msg))
        else:
            print("no ```verdict blocks found" + (" (required!)" if "--require" in flags else ""))
        return 3 if "--require" in flags else 0

    all_errs, verdicts = [], []
    for i, raw in enumerate(raw_blocks, 1):
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as e:
            all_errs.append(f"block {i}: invalid JSON — {e}")
            continue
        all_errs += validate_block(obj, i, schema)
        if isinstance(obj, dict) and obj.get("verdict"):
            verdicts.append(obj["verdict"])

    state = aggregate_state(verdicts)

    report = {"blocks": len(raw_blocks), "verdicts": verdicts, "state": state,
              "ok": not all_errs, "errors": all_errs}
    if "--json" in flags:
        print(json.dumps(report, indent=2))
    else:
        print(f"{len(raw_blocks)} verdict block(s) · aggregate: {state}")
        for e in all_errs:
            print(f"  ERROR: {e}")
        if state == "HAS_FAIL":
            print("  NOTE: a FAIL is present — merge requires a §5 human risk-acceptance to overrule.")
        if state == "HAS_COULD_NOT_ASSESS":
            print("  NOTE: a COULD NOT ASSESS is present — BLOCKING; the gate must be re-run or the artifact reduced. completion-auditor treats it as not-done.")
        if not all_errs:
            print("  OK — all verdict blocks well-formed.")
    return 1 if all_errs else 0


if __name__ == "__main__":
    sys.exit(main())
