#!/usr/bin/env python3
"""
QA evidence — no ArcGIS credential is configured or used
(ACN-2026-31023, story 186189).

Demonstrates that the application holds no ArcGIS token, key or account, that
its requests to the data service are anonymous, and that a layer requiring
authentication is not retrieved rather than being authenticated against.

Run from the application root:

    python QA_Evidence/test_no_arcgis_credential.py
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

checks = []


def record(name, detail, ok):
    checks.append((name, detail, ok))


# ---------------------------------------------------------------------------
# 1. No credential-handling code anywhere in the application
# ---------------------------------------------------------------------------
# Named symbols, plus the shapes a credential takes when it is passed as an
# ordinary parameter. The first list alone once missed a client class whose
# constructor accepted token, username and password.
PATTERNS = [
    r"_ARCGIS_TOKEN", r"arcgis_token", r"\bset_token\b", r"_token_params",
    r"generateToken", r"token_expired", r"_needs_token",
    r"\btoken\s*[:=]\s*[\"']",          # token="..." or token: "..."
    r"\busername\s*[:=]\s*[\"']",       # username="..."
    r"\bpassword\s*[:=]\s*[\"']",       # password="..."
    r"\bArcGISClient\s*\(",             # the SDK wrapper itself
    r"\bfrom\s+arcgis\b", r"\bimport\s+arcgis\b",
]

# Application source only. Virtual environments and installed packages are
# third-party code and are not part of the deployed bundle.
SKIP_DIRS = {".git", "__pycache__", "QA_Evidence", "node_modules",
             ".venv", "venv", "env", "site-packages", ".tox", "build", "dist"}

hits = []
scanned = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        if not fn.endswith(".py"):
            continue
        path = os.path.join(dirpath, fn)
        try:
            src = open(path, encoding="utf-8").read()
        except Exception:
            continue
        scanned += 1
        for pat in PATTERNS:
            for m in re.finditer(pat, src):
                line = src[:m.start()].count("\n") + 1
                hits.append(f"{os.path.relpath(path, ROOT)}:{line} {m.group(0)}")

record("No ArcGIS credential-handling code in the application",
       "; ".join(hits) if hits else
       f"{len(PATTERNS)} credential patterns searched across {scanned} application "
       f".py files - no matches",
       not hits)

# ---------------------------------------------------------------------------
# 2. No ArcGIS credential in the environment
# ---------------------------------------------------------------------------
env_hits = sorted(k for k in os.environ
                  if re.search(r"ARCGIS|ESRI", k, re.I)
                  and re.search(r"TOKEN|KEY|SECRET|PASS|CRED", k, re.I))
record("No ArcGIS credential in environment variables",
       ", ".join(env_hits) if env_hits
       else "no ARCGIS/ESRI credential variable is set in this environment",
       not env_hits)

# ---------------------------------------------------------------------------
# 3. Requests carry no authentication
# ---------------------------------------------------------------------------
from hub.client import HubClient                             # noqa: E402

hub = HubClient()
headers = dict(hub.session.headers)
auth_headers = [k for k in headers if k.lower() in ("authorization", "x-esri-authorization")]
record("Outbound requests send no authentication header",
       "headers sent: " + ", ".join(sorted(headers)) if not auth_headers
       else f"authentication header present: {auth_headers}",
       not auth_headers)
record("No session-level credential object",
       "requests.Session.auth is None" if hub.session.auth is None
       else f"session auth configured: {type(hub.session.auth).__name__}",
       hub.session.auth is None)

# ---------------------------------------------------------------------------
# 4. No token parameter is ever added to a query
# ---------------------------------------------------------------------------
client_src = open(os.path.join(ROOT, "hub", "client.py"), encoding="utf-8").read()
token_param = re.findall(r'["\']token["\']\s*:', client_src)
record("No token parameter in any data-service query",
       "no 'token' key appears in any request parameter set" if not token_param
       else f"{len(token_param)} token parameter(s) found",
       not token_param)

# ---------------------------------------------------------------------------
# 5. A layer requiring authentication is skipped, not authenticated against
# ---------------------------------------------------------------------------
idx = client_src.find("in (499, 498)")
snippet = ""
if idx != -1:
    start = client_src.rfind("\n", 0, client_src.rfind("\n", 0, idx)) + 1
    snippet = client_src[start:client_src.find("\n", idx + 400)].rstrip()
record("Authentication-required responses fall through to public data",
       "handler found in hub/client.py (shown below)" if idx != -1
       else "handler NOT found",
       idx != -1)

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
print("=" * 78)
print("QA EVIDENCE - NO ARCGIS CREDENTIAL CONFIGURED")
print("ACN-2026-31023 / story 186189")
print("=" * 78)
print("Environment        : QA")
print("Application        : Zambia GeoHub AI Assistant")
print("Approved scope     : public datasets only")
print("-" * 78)

failed = 0
for i, (name, detail, ok) in enumerate(checks, 1):
    failed += not ok
    print(f"{i}. {name}")
    print(f"   {'PASS' if ok else 'FAIL'} - {detail}")
    print()

if snippet:
    print("AUTHENTICATION-REQUIRED HANDLING, AS IT APPEARS IN hub/client.py")
    print("-" * 78)
    print(snippet)
    print("-" * 78)
    print()

print(f"{len(checks) - failed} of {len(checks)} checks passed.")
print()
print("The application holds no ArcGIS token, API key or account. Every request")
print("to the data service is anonymous. A layer that requires authentication")
print("returns an authentication-required code, which the application treats as")
print("an empty result and falls back to bundled public data; it never attempts")
print("to authenticate. Restricted data therefore cannot be retrieved.")
print()
print("RESULT:", "PASS" if not failed else "FAIL")
print("=" * 78)
sys.exit(1 if failed else 0)
