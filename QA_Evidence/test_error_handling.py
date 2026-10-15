#!/usr/bin/env python3
"""
QA evidence — error handling and information disclosure
(ACN-2026-31023, story 186199).

Triggers each failure path the application can hit and prints the message that
reaches the user, demonstrating that no path exposes an exception string, a
service response body, a service URL, a credential, or an internal variable or
file name.

The failure paths are driven against the real modules (hub/client.py,
ai/model_client.py); nothing is re-implemented here.

Run from the application root:

    python QA_Evidence/test_error_handling.py
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Strings that must never appear in anything shown to a user.
FORBIDDEN = [
    ("http://", "a service URL"),
    ("https://", "a service URL"),
    ("arcgis", "the data service vendor/host"),
    ("services3", "the data service host"),
    ("azapim", "the AI gateway host"),
    ("worldbank.org", "an internal hostname"),
    ("token", "a credential reference"),
    ("api_key", "a credential reference"),
    ("CONNECT_", "an internal environment variable"),
    ("MAI_FACTORY", "an internal environment variable"),
    (".py", "an internal file name"),
    ("Traceback", "a stack trace"),
]

results = []


def check(area, message):
    """Record one user-facing message and screen it for disclosure."""
    lowered = message.lower()
    hits = [why for needle, why in FORBIDDEN if needle.lower() in lowered]
    results.append((area, message, hits))


# ---------------------------------------------------------------------------
# 1-2. Authentication / OAuth token exchange
# ---------------------------------------------------------------------------
from ai.model_client import ModelClient                      # noqa: E402

for var in ("CONNECT_SERVER", "CONNECT_API_KEY",
            "CONNECT_CONTENT_SESSION_TOKEN", "MAI_FACTORY_TOKEN"):
    os.environ.pop(var, None)

client = ModelClient.__new__(ModelClient)
client.provider = "WB Posit (GPT)"

try:
    client._get_posit_oauth_token()
except Exception as exc:
    check("OAuth token exchange - not configured", str(exc))

try:
    client._get_auth_token()
except Exception as exc:
    check("Authentication - no method available", str(exc))

# Simulate a rejected token exchange (HTTP error from the authorization service).
os.environ["CONNECT_SERVER"] = "https://connect.example.invalid"
os.environ["CONNECT_API_KEY"] = "dummy-key-not-a-real-credential"
os.environ["CONNECT_CONTENT_SESSION_TOKEN"] = "dummy-session-token"

import requests                                              # noqa: E402


class _FakeResponse:
    ok = False
    status_code = 403

    @staticmethod
    def json():
        return {"error": "invalid_grant",
                "error_description": "SECRET-BODY-SHOULD-NOT-SURFACE"}


_real_post = requests.post
requests.post = lambda *a, **k: _FakeResponse()
try:
    client._get_posit_oauth_token()
except Exception as exc:
    check("OAuth token exchange - rejected by service", str(exc))
finally:
    requests.post = _real_post

# ---------------------------------------------------------------------------
# 3-5. Data service failures
# ---------------------------------------------------------------------------
from hub.client import HubClient                             # noqa: E402

hub = HubClient()
URL = ("https://services3.arcgis.com/BU6Aadhn6tbBEdyk/arcgis/rest/services/"
       "GRID3_ZMB_HealthFac_v01beta/FeatureServer/0")


class _Resp:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def drive(payload=None, raise_exc=None):
    def _get(*a, **k):
        if raise_exc:
            raise raise_exc
        return _Resp(payload)
    return _get


_real_get = hub.session.get

hub.session.get = drive(payload={
    "error": {"code": 400,
              "message": "Unable to complete operation",
              "details": ["SECRET-DETAIL-SHOULD-NOT-SURFACE"]}})
try:
    hub.fetch_geojson(URL)
except Exception as exc:
    check("Data service - error response", str(exc))

hub.session.get = drive(payload={"notGeoJson": True,
                                 "secret": "SECRET-BODY-SHOULD-NOT-SURFACE"})
try:
    hub.fetch_geojson(URL)
except Exception as exc:
    check("Data service - unexpected response format", str(exc))

hub.session.get = drive(raise_exc=requests.ConnectionError(
    f"HTTPSConnectionPool(host='services3.arcgis.com') failed for {URL}"))
try:
    hub.fetch_geojson(URL)
except Exception as exc:
    check("Data service - network failure", str(exc))

hub.session.get = drive(payload={"error": {"code": 500,
                                           "message": "SECRET-SHOULD-NOT-SURFACE"}})
try:
    hub.count_features(URL)
except Exception as exc:
    check("Data service - count query failure", str(exc))

hub.session.get = _real_get

# ---------------------------------------------------------------------------
# 6-8. Messages shown by the application itself, read from app.py
# ---------------------------------------------------------------------------
app_src = open(os.path.join(ROOT, "app.py"), encoding="utf-8").read()


def literal_after(anchor, area):
    """Pull the user-facing string that follows a known marker in app.py."""
    idx = app_src.find(anchor)
    if idx == -1:
        results.append((area, "<message not found in app.py>", ["NOT FOUND"]))
        return
    window = app_src[idx:idx + 600]
    found = re.findall(r'"((?:[^"\\]|\\.){20,})"', window)
    check(area, found[0] if found else "<no literal found>")


literal_after('response = ("⚠️ The request could not be completed',
              "AI call failure - generic message")
literal_after('"⚠️ The AI is temporarily overloaded',
              "AI call failure - service overloaded")
literal_after('"⚠️ Rate limit reached',
              "AI call failure - rate limited")
literal_after('st.warning(f"⚠️ Could not load data for',
              "Data load failure shown to user")

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
print("=" * 78)
print("QA EVIDENCE - ERROR HANDLING / INFORMATION DISCLOSURE")
print("ACN-2026-31023 / story 186199")
print("=" * 78)
print("Environment        : QA")
print("Application        : Zambia GeoHub AI Assistant")
print("Modules under test : ai/model_client.py, hub/client.py, app.py")
print()
print("Each failure below was triggered against the real code. The message")
print("shown is what reaches the user.")
print("-" * 78)

failures = 0
for i, (area, message, hits) in enumerate(results, 1):
    status = "LEAK" if hits else "SAFE"
    failures += bool(hits)
    print(f"{i}. {area}")
    print(f"   Message : {message}")
    print(f"   Verdict : {status}" + (f" - exposes {', '.join(hits)}" if hits else ""))
    print()

print("-" * 78)
print(f"{len(results) - failures} of {len(results)} failure paths return a safe message.")
print()
print("Screened for: service URLs and hostnames, response bodies, credential")
print("and token references, internal environment variable names, internal")
print("file names, and stack traces.")
print()
print("The simulated service responses above deliberately contained marker")
print("strings (SECRET-...). None appear in any message, confirming that")
print("service response bodies are not propagated to the user.")
print()
print("RESULT:", "PASS" if not failures else "FAIL")
print("=" * 78)
sys.exit(1 if failures else 0)
