# Code Snippets — one section per story
### ACN-2026-31023

Find your story number. Copy everything under it — **including the ``` fences** — and paste into the work item comment. Azure DevOps renders it as formatted code.

Snippets are repeated where two stories need the same evidence, so you never have to look in another section.

**Stories with no snippet:** 186168, 186170, 186174, 186178, 186180, 186184, 186196, 186212, 186213, 186214, 186217, 186218

---
---

# 186182 — Access tokens rotated according to defined procedures

**The token subsystem, removed.** `hub/client.py` — what now stands where the token handling used to be:

```python
# NOTE: ArcGIS token-based access to private datasets was removed from this
# application's scope during OIS security architecture review (ACN-2026-31023).
# The application queries PUBLIC Zambia GeoHub datasets only, which require no
# authentication. No token is obtained, stored, or transmitted — in particular,
# no credential is ever passed as a URL query parameter.
```

Removed with it: `_ARCGIS_TOKEN`, `set_token()`, `_needs_token()`, `_token_params()`, the token-expiry signalling, and `get_token.py`.

**Verification:**

```
$ grep -rnE "ARCGIS_TOKEN|_token_params|set_token|get_token" --include="*.py" .
(no matches)
```

**The tokens that remain** — both short-lived, platform-issued, never stored. `ai/model_client.py`:

```python
def _get_posit_oauth_token(self) -> str:
    """Get Azure AD token via Posit Connect OAuth token exchange (RFC 8693)."""
    session_token = _os.getenv("CONNECT_CONTENT_SESSION_TOKEN", "")   # injected per session
    resp = _req.post(
        f"{connect_server}/__api__/v1/oauth/integrations/credentials",
        headers={"Authorization": f"Key {connect_api_key}"},
        data={
            "grant_type":         "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token_type": "urn:posit:connect:content-session-token",
            "subject_token":      session_token,
            "audience":           oauth_guid,
        },
        timeout=30,
    )
    return resp.json().get("access_token", "")   # used for one request, then discarded
```

---
---

# 186188 — Only PUBLIC data processed

**A data request as the application actually issues it.** `hub/client.py`:

```python
params = {
    "where": where,
    "outFields": "*",
    "resultRecordCount": geom_limit,
    "f": "geojson",
}
resp = self.session.get(f"{base}/query", params=params, timeout=REQUEST_TIMEOUT)
```

No `token` parameter. No `Authorization` header. No credential of any kind.

**Verification that no credential exists anywhere:**

```
$ grep -rnE "ARCGIS_TOKEN|_token_params|set_token|get_token" --include="*.py" .
(no matches)

$ grep -rn '"token"' --include="*.py" app.py ai/ hub/ utils/ reports/
(no matches)
```

Because the application holds no credential, a non-public layer returns an authorisation error rather than data — demonstrated in the attached control test.

---
---

# 186189 — Restricted data and PII not processed

**Attachment data-handling notice.** `app.py`:

```python
# Data-handling notice for attachments (ACN-2026-31023, story 186189).
# Attached file content is sent to the WBG mAI Factory for analysis, so users
# are told not to attach personal or restricted material.
st.caption(
    "🔒 **Attachments:** content of any file you attach is sent to the WBG mAI Factory "
    "for analysis. Do not attach personal data, or Confidential, Restricted, or "
    "Internal Use Only material. This application is approved for PUBLIC data only."
)

if _chat_result.files:
    st.warning(
        "🔒 You attached a file. Its content will be sent to the WBG mAI Factory "
        "for analysis. Confirm it contains no personal data and no Confidential, "
        "Restricted, or Internal Use Only material — this application is approved "
        "for PUBLIC data only."
    )
```

**File types restricted at the uploader:**

```python
st.chat_input(..., accept_file="multiple",
              file_type=["pdf", "docx", "txt", "png", "jpg", "jpeg", "webp"])
```

---
---

# 186189 — Required confirmation before an attachment is processed

**The control.** An attached file is held **unprocessed** until the user actively
confirms its classification. Nothing is parsed, stored in session state, or sent
to the WBG mAI Factory before that confirmation. `app.py`:

```python
# ── Required confirmation gate for attachments ───────────────────────────────
# ACN-2026-31023, story 186189. An attached file is held UNPROCESSED until the
# user actively confirms its data classification. Nothing is parsed, stored in
# session state, or sent to the WBG mAI Factory before that confirmation.
if st.session_state.get("_pending_files"):
    _pf = st.session_state["_pending_files"]
    _names = ", ".join(f["name"] for f in _pf)
    st.error(f"🔒 **Confirmation required before this file is processed — {_names}**")
    st.markdown(
        "This application is approved for **PUBLIC data only**. If you continue, the "
        "content of this file will be sent to the WBG mAI Factory for analysis. "
        "It will not be read, stored, or transmitted unless you confirm below."
    )
    _ok = st.checkbox(
        "I confirm this file contains no personal data (PII), and no Confidential, "
        "Restricted, or Internal Use Only material.",
        key="_upload_confirm_box",
    )
    _cc1, _cc2 = st.columns(2)
    if _cc1.button("Confirm and process", disabled=not _ok,
                   type="primary", use_container_width=True):
        for _f in _pf:
            _process_confirmed_upload(_f["name"], _f["bytes"])
        _log_event("upload_confirmed", "INFO", files=len(_pf))
        ...
    if _cc2.button("Cancel and discard", use_container_width=True):
        _log_event("upload_cancelled", "INFO", files=len(_pf))
        ...
    st.stop()   # nothing below runs until the user confirms or cancels
```

**On submit, the file is only held — never parsed:**

```python
if _chat_result:
    # Attachments are held pending explicit confirmation — not parsed here.
    if _chat_result.files:
        _pending = []
        for _af in _chat_result.files:
            _pending.append({"name": _af.name, "bytes": _af.read()})
        if _pending:
            st.session_state["_pending_files"] = _pending
            st.session_state["_upload_pending_question"] = _chat_result.text or ""
            _log_event("upload_awaiting_confirmation", "INFO", files=len(_pending))
            st.rerun()
```

**Three properties that make this a control rather than a notice:**

1. The `Confirm and process` button is `disabled=not _ok` — it cannot be pressed until the checkbox is ticked.
2. `st.stop()` halts the script, so no downstream code runs while a file is pending.
3. Parsing happens only inside `_process_confirmed_upload()`, which is reachable only from the confirm branch.

**Audit trail** — each outcome is logged:

```
ZGIA_EVENT severity=INFO event=upload_awaiting_confirmation files=1
ZGIA_EVENT severity=INFO event=upload_confirmed files=1
ZGIA_EVENT severity=INFO event=upload_cancelled files=1
```

---
---

# 186198 (follow-up) — Prompt handling and report input validation

**Report inputs are not user-controlled.** The report generator receives only the
selected dataset's metadata and the records retrieved from the Zambia GeoHub —
the user's free text is never passed into it. `app.py`:

```python
rpt_text = ai_client.ask(
    system=report_system_prompt(),
    user=report_prompt(
        ds["name"],            # dataset name, from the catalogue
        ds["description"],     # dataset description, from the catalogue
        ds.get("fields", []),  # field names, from the dataset schema
        stats,                 # computed aggregate counts
        sample_features,       # records retrieved from ArcGIS
    ),
    max_tokens=3000,
)
```

`ai/prompts.py`:

```python
def report_prompt(
    dataset_name: str,
    description: str,
    fields: list[dict],
    stats: dict,
    sample_features: list[dict],
) -> str:
```

No user-supplied string reaches the report prompt.

**Prompt handling safeguards for the chat path.** The user's question is passed to
the model, but three constraints bound what it can influence:

1. **It cannot reach a data query.** Only an allowlisted place name and a matched
   topic keyword are used for retrieval — see the *186198* section above.
2. **The system prompt constrains the answer to retrieved records:**

```
- Answer using the dataset names, descriptions, and sample records provided to you.
- Never invent statistics or dataset names. If a tool returns an error, say so.
- Cite the dataset name in your final answer.
```

3. **The payload is capped** — 200 records retrieved, at most 15 transmitted, with
   totals pre-aggregated so full record sets are never sent.

**Disclosed limitation:** there is no dedicated prompt-injection filter. A user's
question is sent to the model as written. The mitigations above bound the
*consequences* — a crafted prompt cannot alter the dataset query, reach non-public
data, or cause a credential to be disclosed, because none is held. We would welcome
OIS direction on an expected prompt-injection testing standard.

---
---

# 186191 — Data limited to the minimum required

**Retrieval cap — 200 records.** `app.py`:

```python
_resp = _req.get(f"{_base_url}/query",
    params={"where": _where, "outFields": "*",
            "resultRecordCount": 200, "f": "geojson"},
    headers=_headers, timeout=30)
```

**Transmission cap — 15 records.** `ai/prompts.py`:

```python
if sample_features:
    sample_block = (
        f"Sample records from top dataset ({len(sample_features)} records loaded):\n"
        f"```json\n{json.dumps(sample_features[:15], indent=2)}\n```\n"   # <- cap
    )
```

Totals are pre-aggregated before transmission so full record sets never need sending.

---
---

# 186192 — User requests and generated content not persistently stored

**No persistence layer exists.** The strongest evidence is what is absent:

```
$ grep -rniE "sqlite|psycopg|pymongo|redis|sqlalchemy|boto3" \
      --include="*.py" app.py ai/ hub/ utils/ reports/
(no matches — no persistence library is imported)

$ grep -rnE "open\([^)]*['\"][wa]" --include="*.py" app.py ai/ hub/ utils/ reports/
(no matches — no write-mode file operation exists)
```

**Reports assembled in memory and returned as bytes.** `reports/builder.py`:

```python
from io import BytesIO
...
buf = BytesIO()
doc.save(buf)
return buf.getvalue()        # streamed to the browser; no file written
```

---
---

# 186194 — Temporary files securely disposed of

**Nothing is written to disk, so there is nothing to dispose of.** `reports/builder.py`:

```python
from io import BytesIO
...
buf = BytesIO()
doc.save(buf)
return buf.getvalue()        # streamed to the browser; no file written
```

**Verification that no write-mode file operation exists anywhere:**

```
$ grep -rnE "open\([^)]*['\"][wa]" --include="*.py" app.py ai/ hub/ utils/ reports/
(no matches)
```

Uploaded content is held in session memory and cleared from session state when an attachment is removed or a new conversation starts.

---
---

# 186198 — User input validated and sanitised

**The allowlist.** `app.py`:

```python
def _build_place_allowlist():
    """
    Closed set of valid Zambian district and province names, loaded from the
    bundled administrative boundary data (116 districts).

    Input validation control (ACN-2026-31023, story 186198): a place name taken
    from user text is only used in a dataset query if it appears in this list.
    Anything else is rejected before query construction, so no user-supplied
    string can reach a query clause.
    """
    names = set()
    for feat in _CONTEXT_LAYERS[0]["geojson"].get("features", []):
        props = feat.get("properties", {}) or {}
        for key in ("DISTRICT", "District", "PROVINCE", "Province"):
            if props.get(key):
                names.add(str(props[key]).strip().lower())
    names |= _ZAMBIA_PROVINCES
    return names


_PLACE_ALLOWLIST = _build_place_allowlist()      # 126 entries


def _is_valid_place(name: str) -> bool:
    """True only if `name` is a known Zambian district or province."""
    return bool(name) and name.strip().lower() in _PLACE_ALLOWLIST
```

**Enforcement before any query is built:**

```python
match = _re.search(r'\b(?:in|within|around|near|at)\s+([a-zA-Z][a-z]{2,}...)', text)
if match:
    loc = _re.sub(r'\s+(?:district|province|region)\s*$', '', match.group(1).strip()).title()
    if _is_valid_place(loc):          # <- allowlist check
        return (loc, "district")
return (None, None)                    # rejected: no location filter applied
```

**Unrecognised place names are reported to the user** rather than silently ignored:

```python
if not _location and not _draw_bbox and not _is_meta:
    _unknown_place = _rejected_place(question)
    if _unknown_place:
        _low_confidence_user = (
            f"“{_unknown_place}” was not recognised as a Zambian district "
            "or province, so the answer below is not filtered to that "
            "location. Check the spelling, or try a nearby district."
        )
```

**Validation results:**

```
input                             accepted   outcome
Lusaka                            yes        valid province — query proceeds
Chadiza                           yes        valid district — query proceeds
Rufunsa                           yes        valid district — query proceeds
Nairobi                           no         not a Zambian place — rejected
Atlantis                          no         not a Zambian place — rejected
' OR 1=1--                        no         injection attempt — rejected
Robert'); DROP TABLE schools;--   no         injection attempt — rejected
<script>alert(1)</script>         no         script payload — rejected
```

---
---

# 186199 — Error handling prevents disclosure

**1. OAuth failures no longer include the response body.** `ai/model_client.py`:

```python
if not resp.ok:
    # Response body deliberately excluded — it may echo request material.
    # Only the status code is recorded (ACN-2026-31023, stories 186199/186216).
    raise RuntimeError(f"Posit OAuth token exchange failed (HTTP {resp.status_code})")
token = resp.json().get("access_token", "")
if not token:
    # Response content deliberately excluded (ACN-2026-31023).
    raise RuntimeError("Posit OAuth token exchange returned no access_token")
```

**2. Data-fetch failures no longer show the service URL.** `app.py`:

```python
# Technical detail (service URLs, query parameters, org identifiers)
# is logged server-side only and never shown to the user
# (ACN-2026-31023, stories 186199 / 186216).
if _live_error:
    print(f"GEOHUB FETCH ERROR [{_location}]: {_live_error}", flush=True)
st.warning(
    f"⚠️ Could not load live data for **{_location}**. "
    f"The live GeoHub server may be temporarily unavailable — "
    f"the answer below uses pre-loaded offline data."
)
```

**3. AI failures show a generic message.** `app.py`:

```python
_err_str = str(e)
# Server-side only: log the exception type and message, never a
# service response body or token (ACN-2026-31023, story 186216).
print(f"AI ERROR [{type(e).__name__}]: {_err_str}", flush=True)
...
else:
    # Generic message only — technical detail is not shown to
    # the user (ACN-2026-31023, story 186199).
    response = ("⚠️ The request could not be completed. Please try again. "
                "If the problem continues, contact the application owner.")
```

---
---

# 186202 — AI routed through approved enterprise platforms

**Every AI endpoint configured in the application.** `ai/model_client.py`:

```python
PROVIDERS = {
    "WB Desktop (GPT)": {
        "models":   ["gpt-5", "gpt-5-mini", "gpt-4o", "gpt-4o-mini"],
        "mai_base": "https://azapimqa.worldbank.org/maifactory/openai",
    },
    "WB Desktop (Claude)": {
        "models": ["us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-haiku-4-5"],
        "bedrock_base": "https://azapimqa.worldbank.org/conversationalai/bedrock/model/",
    },
    "WB Posit (GPT)": {
        "models":   ["gpt-5", "gpt-5-mini", "gpt-4o", "gpt-4o-mini"],
        "env_key":  "WB_POSIT",
        "mai_base": "https://azapimqa.worldbank.org/maifactory/openai",
    },
    "WB Posit (Claude)": {
        "models": ["us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-haiku-4-5"],
        "bedrock_base": "https://azapimqa.worldbank.org/conversationalai/bedrock/model/",
    },
    # NOTE: direct external AI provider paths (OpenAI API, Google Gemini) were
    # removed under OIS security review (ACN-2026-31023). All AI inference is
    # routed exclusively through the WBG-approved mAI Factory gateway. Do not
    # reintroduce a provider that calls an external AI service directly.
}
```

Every AI destination is `azapimqa.worldbank.org`. There is no other.

**Verification that external providers are gone:**

```
$ grep -rniE "OPENAI_API_KEY|GOOGLE_API_KEY|generativeai|api\.openai\.com" \
      --include="*.py" app.py ai/ hub/
(no matches)
```

**How the bearer token is obtained:**

```python
def _get_posit_oauth_token(self) -> str:
    """Get Azure AD token via Posit Connect OAuth token exchange (RFC 8693)."""
    session_token = _os.getenv("CONNECT_CONTENT_SESSION_TOKEN", "")
    resp = _req.post(
        f"{connect_server}/__api__/v1/oauth/integrations/credentials",
        headers={"Authorization": f"Key {connect_api_key}"},
        data={
            "grant_type":         "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token_type": "urn:posit:connect:content-session-token",
            "subject_token":      session_token,
            "audience":           oauth_guid,
        },
        timeout=30,
    )
    return resp.json().get("access_token", "")
```

---
---

# 186203 — Data to AI limited to approved content

**Retrieval cap — 200 records.** `app.py`:

```python
_resp = _req.get(f"{_base_url}/query",
    params={"where": _where, "outFields": "*",
            "resultRecordCount": 200, "f": "geojson"},
    headers=_headers, timeout=30)
```

**Transmission cap — 15 records.** `ai/prompts.py`:

```python
if sample_features:
    sample_block = (
        f"Sample records from top dataset ({len(sample_features)} records loaded):\n"
        f"```json\n{json.dumps(sample_features[:15], indent=2)}\n```\n"   # <- cap
    )
```

**Totals pre-aggregated before transmission** so full record sets are never sent:

```python
total_count_note = (
    f"\n⚡ EXACT TOTAL COUNT (from live API): "
    f"There are {total_count:,} records in {location} in this dataset."
)
```

---
---

# 186204 — AI outputs reviewed by users prior to business use

**Low-confidence detection.** `app.py`:

```python
_low_confidence_reason = ""   # instruction sent to the model
_low_confidence_user   = ""   # message shown to the user

if _location and not _draw_bbox and not context_dataset and not _is_meta:
    if not sample_features or not _sample_matches_location(sample_features, _location):
        _low_confidence_user = (
            f"No records for {_location} were found in this dataset. "
            "The answer below should not be relied on for a count — "
            "try a nearby district, or a different topic."
        )
    elif not st.session_state.get("_last_fetch_was_live", False):
        _low_confidence_user = (
            "The live Zambia GeoHub service was unavailable, so this answer "
            "uses a pre-loaded offline copy of the data. Figures may not "
            "reflect the current situation — verify against the live dataset "
            "before relying on them."
        )
    elif _total_count is not None and _total_count < 3:
        _low_confidence_user = (
            f"Only {_total_count} record(s) exist for {_location} in this "
            "dataset — too few to draw a general conclusion from."
        )

if _low_confidence_reason:
    st.warning(f"⚠️ **Low confidence** — {_low_confidence_user}")
```

The warning is shown in the interface **and** the model is separately instructed to state the limitation, so the caveat appears in both places.

**Grounding rules sent with every request.** `ai/prompts.py`:

```
- Answer using the dataset names, descriptions, and sample records provided to you.
- Never invent statistics or dataset names. If a tool returns an error, say so.
- Cite the dataset name in your final answer.
```

---
---

# 186205 — AI services do not retain data beyond approved retention

**Application side — no persistence layer exists:**

```
$ grep -rniE "sqlite|psycopg|pymongo|redis|sqlalchemy|boto3" \
      --include="*.py" app.py ai/ hub/ utils/ reports/
(no matches — no persistence library is imported)

$ grep -rnE "open\([^)]*['\"][wa]" --include="*.py" app.py ai/ hub/ utils/ reports/
(no matches — no write-mode file operation exists)
```

**Reports assembled in memory and streamed.** `reports/builder.py`:

```python
buf = BytesIO()
doc.save(buf)
return buf.getvalue()        # no file written
```

**What is sent to the AI service** — nothing beyond this:

```python
user_p = chatbot_user_prompt(
    question,          # the user's question
    datasets,          # dataset name, description, field names
    sample_features,   # up to 15 public records
    total_count=...,   # pre-aggregated count
    location=...,
)
```

---
---

# 186206 — AI integrations comply with AI governance

**Every AI endpoint configured in the application.** `ai/model_client.py`:

```python
PROVIDERS = {
    "WB Posit (GPT)": {
        "models":   ["gpt-5", "gpt-5-mini", "gpt-4o", "gpt-4o-mini"],
        "env_key":  "WB_POSIT",
        "mai_base": "https://azapimqa.worldbank.org/maifactory/openai",
    },
    "WB Posit (Claude)": {
        "models": ["us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-haiku-4-5"],
        "bedrock_base": "https://azapimqa.worldbank.org/conversationalai/bedrock/model/",
    },
    # NOTE: direct external AI provider paths (OpenAI API, Google Gemini) were
    # removed under OIS security review (ACN-2026-31023). All AI inference is
    # routed exclusively through the WBG-approved mAI Factory gateway.
}
```

**Approved models only, inference only** — no training, fine-tuning, or embedding storage. The application sends a request and receives a response:

```python
resp = client.chat.completions.create(model=self.model, messages=full_messages, ...)
```

**Verification that no external provider can be reached:**

```
$ grep -rniE "OPENAI_API_KEY|GOOGLE_API_KEY|generativeai|api\.openai\.com" \
      --include="*.py" app.py ai/ hub/
(no matches)
```

---
---

# 186208 — Connections only with approved endpoints

**Complete list of outbound hosts in deployed code:**

```
ai.worldbank.org            <- documentation link shown in UI, not an API call
azapimqa.worldbank.org     <- WBG mAI Factory gateway
services.arcgis.com         <- Zambia GeoHub (public datasets)
services3.arcgis.com        <- Zambia GeoHub (public datasets)
services6.arcgis.com        <- Zambia GeoHub (public datasets)
services7.arcgis.com        <- Zambia GeoHub (public datasets)
services9.arcgis.com        <- Zambia GeoHub (public datasets)
utility.arcgis.com          <- appears only in the excluded-hosts blocklist
www.arcgis.com              <- Zambia GeoHub catalogue search
zmb-geowb.hub.arcgis.com    <- Zambia GeoHub portal
```

**Verification that the removed services are gone:**

```
$ grep -rniE "open-elevation|project-osrm|routing\.openstreetmap|overpass|maps\.mail\.ru|cartocdn" \
      --include="*.py" app.py ai/ hub/
(no matches)

$ grep -rniE "OPENAI_API_KEY|GOOGLE_API_KEY|generativeai|api\.openai\.com" \
      --include="*.py" app.py ai/ hub/
(no matches)
```

**The routing function that previously called external services.** `app.py`:

```python
def _osrm_route(lon1, lat1, lon2, lat2):
    """
    Road routing. Returns (road_km, drive_seconds, coords) or (None, None, None).

    External routing services (OSRM / OpenStreetMap routing) were removed under OIS
    security review (ACN-2026-31023): outbound connections are restricted to the
    approved WBG endpoints only. Callers fall back to the built-in offline Zambia
    road graph, which requires no external call.
    """
    return None, None, None
```

---
---

# 186209 — Certificate validation enforced

**Trust store injection.** `hub/client.py`:

```python
try:
    import truststore
    truststore.inject_into_ssl()      # use the OS trust store, incl. WBG internal CAs
except Exception:
    pass
```

`requirements.txt`:

```
truststore>=0.9.1
```

**Verification that verification is never disabled:**

```
$ grep -rnE "verify=False|ssl\._create_unverified|CERT_NONE" --include="*.py" .
(no matches anywhere in the project)
```

All outbound calls use the `requests` default of `verify=True`, validated against the OS trust store. An invalid, expired, self-signed, or hostname-mismatched certificate causes the connection to be rejected.

**Scope note** — the services named in the control text are no longer present:

```
$ grep -rniE "open-elevation|project-osrm|routing\.openstreetmap" \
      --include="*.py" app.py ai/ hub/
(no matches)
```

---
---

# 186210 — Network traffic restricted

**Complete list of outbound hosts in deployed code:**

```
ai.worldbank.org            <- documentation link shown in UI, not an API call
azapimqa.worldbank.org     <- WBG mAI Factory gateway
services.arcgis.com         <- Zambia GeoHub (public datasets)
services3.arcgis.com        <- Zambia GeoHub (public datasets)
services6.arcgis.com        <- Zambia GeoHub (public datasets)
services7.arcgis.com        <- Zambia GeoHub (public datasets)
services9.arcgis.com        <- Zambia GeoHub (public datasets)
utility.arcgis.com          <- appears only in the excluded-hosts blocklist
www.arcgis.com              <- Zambia GeoHub catalogue search
zmb-geowb.hub.arcgis.com    <- Zambia GeoHub portal
```

**Three destinations are actually used:**

| Destination | Purpose | Authentication |
|---|---|---|
| Zambia GeoHub ArcGIS REST API | Public geospatial records | None — public data |
| `azapimqa.worldbank.org` | AI inference | Azure AD bearer token |
| Posit Connect OAuth endpoint | Obtaining that token | Platform session token |

**Verification that previously-used external services are gone:**

```
$ grep -rniE "open-elevation|project-osrm|routing\.openstreetmap|overpass|maps\.mail\.ru|cartocdn" \
      --include="*.py" app.py ai/ hub/
(no matches)
```

The application opens no listening ports and publishes no API — it runs as hosted content on Posit Connect.

---
---

# 186211 — Tokens not exposed in URLs, logs, or monitoring

**The token subsystem, removed.** `hub/client.py` — what now stands where the token handling used to be:

```python
# NOTE: ArcGIS token-based access to private datasets was removed from this
# application's scope during OIS security architecture review (ACN-2026-31023).
# The application queries PUBLIC Zambia GeoHub datasets only, which require no
# authentication. No token is obtained, stored, or transmitted — in particular,
# no credential is ever passed as a URL query parameter.
```

Eight code locations that could append a token to a URL were removed, along with `_ARCGIS_TOKEN`, `set_token()`, `_needs_token()`, `_token_params()`, and the expiry signalling.

**A data request as the application actually issues it:**

```python
params = {
    "where": where,
    "outFields": "*",
    "resultRecordCount": geom_limit,
    "f": "geojson",
}
resp = self.session.get(f"{base}/query", params=params, timeout=REQUEST_TIMEOUT)
```

No token parameter, no Authorization header.

**Verification:**

```
$ grep -rnE "ARCGIS_TOKEN|_token_params|set_token|get_token" --include="*.py" .
(no matches)

$ grep -rn '"token"' --include="*.py" app.py ai/ hub/ utils/ reports/
(no matches — no credential is passed as a URL query parameter)
```

**AI tokens are sent only in the Authorization header, server-side.** `ai/model_client.py`:

```python
resp = _req.post(url, json=payload, headers={
    "Authorization": f"Bearer {token}",      # header only, never a URL parameter
    "Content-Type": "application/json",
}, timeout=60)
```

---
---

# 186212 · 186217 — Structured event logging

**The event emitter.** `app.py`:

```python
def _log_event(event: str, severity: str = "INFO", **fields):
    """
    Structured security/operational event log (ACN-2026-31023, stories 186212,
    186214, 186217).

    One line per event, machine-parseable as key=value so a SIEM can alert on
    it directly. Never records prompt text, AI responses, uploaded content,
    credentials, service URLs, or query parameters — only the event type and
    non-sensitive context.
    """
    parts = " ".join(f"{k}={v}" for k, v in fields.items() if v not in (None, ""))
    print(f"ZGIA_EVENT severity={severity} event={event} {parts}".rstrip(), flush=True)
```

**Where events are emitted:**

```python
# AI request failure
_log_event("ai_request_failed", "ERROR", error_type=type(e).__name__)

# Live geospatial fetch failed
_log_event("geohub_fetch_failed", "WARN", location=_location)

# Live fetch returned nothing; fell back to the offline dataset
_log_event("geohub_fallback_offline", "WARN", location=_location)

# Supplementary context fetch failed
_log_event("geohub_context_fetch_failed", "WARN",
           location=_location, error_type=type(_ctx_e).__name__)

# Export / download activity
_log_event("data_export", "INFO", format="csv",
           dataset=ds_name.replace(" ", "_"), rows=len(rows))
```

**Sample output a SIEM would receive:**

```
ZGIA_EVENT severity=ERROR event=ai_request_failed error_type=APIConnectionError
ZGIA_EVENT severity=WARN  event=geohub_fetch_failed location=Chadiza
ZGIA_EVENT severity=WARN  event=geohub_fallback_offline location=Rufunsa
ZGIA_EVENT severity=WARN  event=geohub_context_fetch_failed location=Lusaka error_type=HTTPError
ZGIA_EVENT severity=INFO  event=data_export format=csv dataset=GRID3_ZMB_Schools rows=328
```

**Verification that no user content is logged:**

```
$ grep -rnE "print\(.*(question|user_p|response|_doc_text|uploaded|token)" \
      --include="*.py" app.py ai/ hub/
(no matches — no prompt, response, or credential is written to the log)
```

---
---

# 186216 — Logs do not contain secrets

**1. OAuth failures no longer log the response body.** `ai/model_client.py`:

```python
if not resp.ok:
    # Response body deliberately excluded — it may echo request material.
    # Only the status code is recorded (ACN-2026-31023, stories 186199/186216).
    raise RuntimeError(f"Posit OAuth token exchange failed (HTTP {resp.status_code})")
token = resp.json().get("access_token", "")
if not token:
    # Response content deliberately excluded (ACN-2026-31023).
    raise RuntimeError("Posit OAuth token exchange returned no access_token")
```

**2. Data-fetch errors log server-side only, without the service URL.** `app.py`:

```python
# Technical detail (service URLs, query parameters, org identifiers)
# is logged server-side only and never shown to the user
# (ACN-2026-31023, stories 186199 / 186216).
if _live_error:
    print(f"GEOHUB FETCH ERROR [{_location}]: {_live_error}", flush=True)
```

**3. AI errors log the exception type and message only.** `app.py`:

```python
# Server-side only: log the exception type and message, never a
# service response body or token (ACN-2026-31023, story 186216).
print(f"AI ERROR [{type(e).__name__}]: {_err_str}", flush=True)
```

**Operational events are logged in a structured, non-sensitive form** — see the *186212 · 186217* section for the emitter and sample output.

**No prompts, responses, or uploaded content are logged** — they exist only in session memory:

```
$ grep -rnE "print\(.*(question|user_p|response|_doc_text|uploaded)" --include="*.py" app.py
(no matches — user content is never written to the log)
```

---

*Reference: ACN-2026-31023*
