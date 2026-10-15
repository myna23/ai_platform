#!/usr/bin/env python3
"""
QA evidence — input validation control (ACN-2026-31023, story 186198).

Demonstrates that a place name taken from user text is checked against a closed
allowlist of known Zambian districts and provinces, and that anything not on
that list is rejected BEFORE any dataset query is constructed.

The validation functions are not re-implemented here. They are extracted
verbatim from app.py at run time and executed against the same administrative
boundary dataset the application loads, so these results reflect the deployed
code rather than a copy of it.

Run from the application root:

    python QA_Evidence/test_input_validation.py
"""

import ast
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "app.py")
DISTRICTS = os.path.join(ROOT, "data", "districts.json")

# Names lifted from app.py — the allowlist builder and the check that guards
# every query. If a name is renamed in app.py this script fails loudly rather
# than silently testing nothing.
WANTED = ("_ZAMBIA_PROVINCES", "_build_place_allowlist", "_is_valid_place")


def load_control_under_test():
    """Extract the real validation code from app.py and execute it."""
    source = open(APP, encoding="utf-8").read()
    tree = ast.parse(source)

    segments = {}
    for node in tree.body:
        name = None
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
        if name in WANTED:
            segments[name] = ast.get_source_segment(source, node)

    missing = [n for n in WANTED if n not in segments]
    if missing:
        sys.exit(f"FAIL: could not find {missing} in app.py — test aborted")

    # The allowlist is built from the bundled boundary data, exactly as the
    # application builds it at startup.
    with open(DISTRICTS, encoding="utf-8") as f:
        context_layers = [{"geojson": json.load(f), "name": "Districts",
                           "type": "boundary"}]

    ns = {"_re": re, "_CONTEXT_LAYERS": context_layers}
    for name in WANTED:
        exec(segments[name], ns)
    ns["_PLACE_ALLOWLIST"] = ns["_build_place_allowlist"]()
    return ns, segments


# The eight cases previously reported for this story, re-run against the
# current code. (input, expected outcome, what the case demonstrates)
CASES = [
    ("Lusaka",                           "ACCEPT", "Valid district and province"),
    ("Chadiza",                          "ACCEPT", "Valid district"),
    ("Rufunsa",                          "ACCEPT", "Valid district"),
    ("Nairobi",                          "REJECT", "Not a Zambian place"),
    ("Atlantis",                         "REJECT", "Not a Zambian place"),
    ("' OR 1=1--",                       "REJECT", "Injection attempt"),
    ("Robert'); DROP TABLE schools;--",  "REJECT", "Injection attempt"),
    ("<script>alert(1)</script>",        "REJECT", "Script payload"),
]


def call_sites():
    """Locate every place the allowlist check is applied, in the live source."""
    found = []
    for i, line in enumerate(open(APP, encoding="utf-8"), 1):
        stripped = line.strip()
        if "_is_valid_place(" in stripped and not stripped.startswith("def "):
            found.append((i, stripped))
    return found


def main():
    ns, segments = load_control_under_test()
    is_valid = ns["_is_valid_place"]
    allowlist = ns["_PLACE_ALLOWLIST"]

    print("=" * 78)
    print("QA EVIDENCE - INPUT VALIDATION (CLOSED ALLOWLIST)")
    print("ACN-2026-31023 / story 186198")
    print("=" * 78)
    print(f"Environment        : QA")
    print(f"Application        : Zambia GeoHub AI Assistant")
    print(f"Control under test : app.py :: _is_valid_place()")
    print(f"Allowlist source   : data/districts.json + fixed province list")
    print(f"Allowlist entries  : {len(allowlist)}")
    print()
    print("CONTROL AS IT APPEARS IN app.py")
    print("-" * 78)
    print(segments["_is_valid_place"])
    print("-" * 78)
    print()
    print("ENFORCEMENT POINTS - every call site, located in the current source")
    print("-" * 78)
    for lineno, line in call_sites():
        print(f"  app.py:{lineno}: {line}")
    print("-" * 78)
    print()
    print("TEST RESULTS")
    print("-" * 78)
    print(f"{'#':<3}{'Input':<34}{'Expected':<10}{'Actual':<10}{'Result':<8}")
    print("-" * 78)

    failures = 0
    for i, (value, expected, _why) in enumerate(CASES, 1):
        actual = "ACCEPT" if is_valid(value) else "REJECT"
        ok = actual == expected
        failures += not ok
        shown = value if len(value) <= 32 else value[:29] + "..."
        print(f"{i:<3}{shown:<34}{expected:<10}{actual:<10}{'PASS' if ok else 'FAIL':<8}")

    print("-" * 78)
    for i, (value, _expected, why) in enumerate(CASES, 1):
        print(f"  {i}. {why}")
    print("-" * 78)
    print(f"{len(CASES) - failures} of {len(CASES)} cases passed.")
    print()
    if failures:
        print("RESULT: FAIL - the allowlist did not behave as specified.")
        sys.exit(1)
    print("RESULT: PASS")
    print()
    print("Every rejected value is discarded before query construction, so no")
    print("user-supplied string reaches a dataset query clause. Rejection is on")
    print("an allowlist, not a denylist: an input is used only if it matches a")
    print("known district or province, so payloads not represented above are")
    print("rejected by the same rule.")
    print("=" * 78)


if __name__ == "__main__":
    main()
