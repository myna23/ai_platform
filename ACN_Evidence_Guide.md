# One story at a time — paste, screenshot, attach
### ACN-2026-31023

30 stories. Each block is self-contained.

**Three kinds of evidence:**

| | What | How to use |
|---|---|---|
| **Snippet** | `ACN_Code_Snippets.md` | Copy the block **including the ``` fences** and paste into the comment. Azure DevOps renders it as formatted code. |
| **File** | `QA_Evidence/*.txt` | Attach the file. Don't open it in the IDE first — it strips the formatting. |
| **Screenshot** | letters below | Take once, reuse across stories. |

**Screenshots — 12 total, 2 already captured:**

| | Where | Must show |
|---|---|---|
| **A** | Posit Connect → Settings → **Vars** | Only `WB_POSIT`. No `ARCGIS_TOKEN` |
| **B** | Posit Connect → Settings → **Access** | Access mode + user/group list + owner |
| **C** | Posit Connect → Settings → Access → **Integrations** | mAI Factory OAuth integration attached |
| **D** | Posit Connect → Settings → **Advanced/Runtime** | Hosted content, no custom ports |
| **E** | Posit Connect → **Bundles/History** | Deployments with timestamps |
| **F** | Posit Connect → **Logs** | Full session: startup, query, AI call, an error |
| **G** | App: *"How many mines are in Rufunsa?"* | ✅ **captured** |
| **H** | App: *"How many schools are in Lusaka?"* | 328 + source citation + live/offline indicator |
| **I** | App: any answer | Word/PDF download buttons |
| **J** | App: landing page | Chat, map, table, download. No admin screens |
| **K** | Browser DevTools → Network | No token in any request URL |
| **L** | App: attach a file | ✅ **captured** |

---
---

# 1 — 186168 · Access restricted to authorized users

**Paste:**
> Access is enforced by the hosting platform. The application runs on WBG Posit Connect, is reachable only from inside the WBG network, and Posit Connect controls who may open it. The attached configuration shows the authorised viewer list for this QA content item.
>
> The application has no separate login because it serves PUBLIC data only — every authorised user sees identical information, so there is no differentiated access to enforce within the application.

**Screenshot:** B · **Snippet:** none · **File:** none

---

# 2 — 186170 · Administrative access limited to designated administrators

**Paste:**
> The application has no administrative interface and no privileged functions. The attached application screenshot shows the complete user function set — chat, map, data table, download — all read-only.
>
> Administration is platform-level only: deploying, setting environment variables, viewing logs. The attached Posit Connect configuration shows these are limited to the content owner and named collaborators.

**Screenshot:** B + J · **Snippet:** none · **File:** none

---

# 3 — 186174 · User access limited to approved business functions — EXCEPTION

**Paste:**
> **On the mismatch raised:** the SA document reviewed was the June version. The updated SA is attached and confirms the application processes **PUBLIC data only** — private dataset access was removed from scope and the ArcGIS token removed from the code.
>
> **Exception basis:** with public-only data, every user receives identical information. The attached application screenshot shows the full function set, all read-only, with no administrative screens and nothing that can be created, changed, or deleted. There is no differentiated function or dataset to restrict.
>
> Submitted as a formal exception for EA/OIS decision. If the data classification ever changes to include non-public data, RBAC will be implemented first as a prerequisite.

**Screenshot:** B + J · **Snippet:** none · **File:** `ACN_Zambia_GeoHub_AI.docx`

---

# 4 — 186178 · Secrets in approved secure configuration repositories

✅ **ALREADY CLOSED** — no action.

---

# 5 — 186180 · Secrets not hardcoded

**Paste:**
> Secret scan completed with detect-secrets 1.5.0 (27 detector plugins) across all git-tracked files. **Result: PASS — no secrets, credentials, API keys, tokens, or passwords found.**
>
> The scanner raised 143 entropy flags; all were reviewed. 92 are public ArcGIS dataset identifiers appearing in public Zambia GeoHub URLs, 51 are MD5 checksums in the deployment manifest. Zero required action.
>
> The scan also surfaced stale references to credentials the application no longer uses. None were live secrets — all were templates or documentation — and all have been corrected: the `.env.example` placeholder key removed and the file excluded from deployment, two token-management scripts deleted, an unused ArcGIS username/password code path removed from the bundle, and four documentation files fixed that had documented `OPENAI_API_KEY`, `ARCGIS_TOKEN`, and token-in-URL examples.

**Screenshot:** A · **Snippet:** none · **File:** `QA_Evidence/186180_secret_scan.txt`

---

# 6 — 186182 · Access tokens rotated according to defined procedures

**Paste:**
> **The token this control was raised against no longer exists.** The updated SA document is attached; the version reviewed predated the scope change.
>
> The code snippet below shows the token subsystem has been removed entirely — `_ARCGIS_TOKEN`, `set_token()`, `_needs_token()`, `_token_params()`, the expiry signalling, and `get_token.py`. A repository search returns no matches for any of them. The attached Posit Connect configuration shows no `ARCGIS_TOKEN` is set.
>
> The only remaining tokens are the Posit Connect session token and the Azure AD bearer token, both short-lived, platform-issued per session, and discarded after use. No manual rotation procedure is required because no static token is held.

**Screenshot:** A · **Snippet:** *186182 · 186188 · 186211 — No ArcGIS credential* (all 3) · **File:** `ACN_Zambia_GeoHub_AI.docx`

---

# 7 — 186184 · Administrative access to secrets restricted and auditable

**Paste:**
> No application secrets exist, so there is no secret store to restrict — the attached environment configuration shows only a non-sensitive flag. Permission to view or change it is limited to the content owner and named collaborators, shown in the attached access configuration.
>
> Audit logging of platform configuration changes is owned by the Posit Connect platform team; requested.

**Screenshot:** A + B · **Snippet:** none · **File:** none

---

# 8 — 186188 · Only PUBLIC data processed

**Paste:**
> **On the mismatch raised:** the SA reviewed was the June version. The updated SA is attached and states the application processes **only Public** datasets.
>
> Evidence attached:
> 1. Dataset inventory — all **62** catalogue datasets, every one PUBLIC, zero Internal Use Only, zero Restricted
> 2. A live unauthenticated API request returning public school records — no token, no Authorization header, no credential
> 3. A **control test**: a token-required ArcGIS layer requested without a credential returned **`error 499: Token Required`** — demonstrating the application cannot reach non-public data
> 4. The code snippet below shows a data request as the application actually issues it — no token parameter, no Authorization header
>
> The decisive point: no credential exists, so retrieving anything but public data is not possible.

**Screenshot:** A · **Snippet:** *186182 · 186188 · 186211 — Snippet 2* · **File:** `ACN_Zambia_GeoHub_AI.docx` + `QA_Evidence/186188_dataset_inventory.txt` + `QA_Evidence/186188_sample_api_call.txt`

---

# 9 — 186189 · Restricted data and PII not processed

**Paste:**
> The geospatial datasets contain no personal data — facility names, categories, coordinates only. Restricted data cannot be retrieved because no credential exists (see 186188).
>
> We disclosed that users can attach a document whose text is sent to the AI, and that the application does not inspect uploaded content. **A data-handling control has now been added** — see the code snippet below:
>
> 1. A notice permanently displayed beneath the chat input
> 2. A prominent warning on attaching a file, requiring the user to confirm it contains no personal or restricted material
>
> File types are restricted at the uploader. Attached content is never written to disk, exists only in session memory, and goes only to the WBG-approved gateway.

**Screenshot:** L · **Snippet:** *186189 — Attachment data-handling notice* · **File:** none

---

# 10 — 186191 · Data limited to the minimum required

**Paste:**
> The code snippets below show the enforced limits: maximum **200 records** retrieved per query, filtered to the requested district or province, and maximum **15 sample records** sent to the AI. Totals are pre-calculated before transmission so full record sets are never sent. Only the single most relevant dataset is queried.

**Screenshot:** none · **Snippet:** *186191 · 186194 · 186203 — Data minimisation* (Snippets 1 and 2) · **File:** none

---

# 11 — 186192 · User requests and generated content not persistently stored

**Paste:**
> The application is stateless — no database, file store, or cache. Questions, AI responses, retrieved data, and uploads are held in session memory only and released when the session ends. Reports are built in memory and streamed to the browser with no server copy.
>
> The snippet below shows the strongest evidence: a repository search confirms no persistence library is imported anywhere and no write-mode file operation exists in the application code.
>
> The attached logs show a complete session: no prompts, responses, or uploaded content are written.

**Screenshot:** F · **Snippet:** *186192 — Stateless processing* · **File:** none

---

# 12 — 186194 · Temporary files securely disposed of

**Paste:**
> No temporary files are created, so there is no disposal process. The snippet below shows reports assembled in memory and returned as bytes — never written to disk. Uploads and retrieved data are held in memory only, and the application clears uploaded content from session state when an attachment is removed or a new conversation starts.
>
> Nothing is written to the filesystem, so nothing can persist after a session or be recovered from disk.

**Screenshot:** none · **Snippet:** *186191 · 186194 · 186203 — Snippet 3* · **File:** none

---

# 13 — 186196 · Data exports only to authorized users

**Paste:**
> Confirming the point raised: app access in QA is restricted to authorised users through Posit Connect. The attached access configuration shows the assigned users for this content item, and the attached screenshot shows an authenticated authorised user with the Word/PDF download options available.
>
> The application has no role-based restriction within it (see the exception under 186174), but every export contains only PUBLIC data — no restricted data, personal data, or credential can appear in one, because none can be retrieved.

**Screenshot:** B + I · **Snippet:** none · **File:** none

---

# 14 — 186198 · User input validated and sanitised

**Paste:**
> Input validation has been strengthened. A place name taken from user text is now used in a dataset query **only if it appears in a closed allowlist** of known Zambian districts and provinces — 126 entries, loaded at startup from the bundled administrative boundary data. Anything else is rejected before query construction, so no user-supplied string can reach a query clause. See the code snippets below.
>
> This layers on the existing restriction, which already limited candidates to 1–3 plain alphabetic words so punctuation, symbols and query syntax could not be captured.
>
> If a question names a place that is not recognised, the application now tells the user explicitly rather than answering without a location filter.
>
> Validation results cover 8 cases including injection attempts (`' OR 1=1--`, `Robert'); DROP TABLE schools;--`) and script payloads — all rejected — with valid districts still accepted.

**Screenshot:** none · **Snippet:** *186198 — Input validation* (all 3) · **File:** none

---

# 15 — 186199 · Error handling prevents disclosure

**Paste:**
> Fixed. Three error paths were corrected — see the code snippets below:
>
> 1. **AI call failures** — users now receive a generic message; technical detail is retained server-side only.
> 2. **OAuth token exchange failures** — previously included part of the authorisation service's response body; now record only the HTTP status code and a fixed description.
> 3. **Geospatial data fetch failures** — previously displayed the full service URL with query parameters and organisation identifier; now show only *"Could not load live data for [location]. The live GeoHub server may be temporarily unavailable."*
>
> A codebase sweep confirms no exception text is interpolated into any user-facing message. The attached screenshot shows the current behaviour, and the attached logs show a session including an error condition.

**Screenshot:** G + F · **Snippet:** *186199 · 186216 — Error handling and log content* (all 3) · **File:** none

---

# 16 — 186202 · AI routed through approved enterprise platforms

**Paste:**
> The code snippets below show the current QA implementation:
> - Every AI endpoint configured in the application — **only** `azapimdev.worldbank.org`, using the `maifactory/openai` path for GPT and the Bedrock path for Claude
> - A repository search returning **no matches** for `OPENAI_API_KEY`, `GOOGLE_API_KEY`, or the Google generative-AI library — the direct-provider code and its dependency are removed
> - The complete list of outbound hosts in deployed code: only ArcGIS and worldbank.org remain
>
> The attached Posit Connect configuration shows the mAI Factory OAuth integration bound to this content item, which is how the bearer token is obtained.

**Screenshot:** C · **Snippet:** *186202 · 186208 — AI endpoints and approved destinations* (all 3) · **File:** none

---

# 17 — 186203 · Data to AI limited to approved content

**Paste:**
> A real request payload is attached, generated by the application's own prompt-construction code against live public data. It shows **148 records retrieved, exactly 15 transmitted**, and the complete message content: the user's question, dataset metadata, 15 sample records, pre-aggregated totals, and the grounding rules. Nothing else.
>
> No credential, token, session identifier, or user identity appears. Records carry facility name, type and location only.
>
> The code snippets below show the 200/15 caps enforced in configuration.

**Screenshot:** H · **Snippet:** *186191 · 186194 · 186203 — Snippets 1 and 2* · **File:** `QA_Evidence/186203_ai_request_payload.txt`

---

# 18 — 186204 · AI outputs reviewed by users prior to business use

**Paste:**
> QA evidence attached showing the user review step in the running application:
>
> 1. **Low-confidence warning** — asked *"How many mines are in Rufunsa?"*, the application displays a warning banner stating the live service was unavailable and the answer uses offline data that may not reflect the current situation. The AI's own answer repeats the caveat and reports zero records rather than producing an estimate.
> 2. **Source citation** — asked *"How many schools are in Lusaka?"*, the answer displays the source dataset with a link to it on the Zambia GeoHub and an indicator showing whether data was live or offline.
>
> The code snippet below shows the detection logic and the grounding rules sent with every request.
>
> **Remaining gap:** no written procedure requires formal sign-off before AI output is used in a decision, and no user training material exists. If a documented review step is required we will draft it with the Business Owner — please confirm the expected form.

**Screenshot:** G + H · **Snippet:** *186204 — AI output review controls* (both) · **File:** none

---

# 19 — 186205 · AI services do not retain data beyond approved retention

**Paste:**
> **Application:** stateless, nothing retained. Attached logs show a complete session with no prompts, responses, or content written.
>
> **AI gateway:** retention is governed by the WBG mAI Factory service terms, owned by the ITSO/mAI team. This application has no configuration that influences it. Requested and will be attached on receipt.

**Screenshot:** F · **Snippet:** *186192 — Stateless processing* · **File:** ITSO retention terms — **request from WBG ITSO/mAI team**

---

# 20 — 186206 · AI integrations comply with AI governance

**Paste:**
> All inference routes exclusively through the WBG mAI Factory gateway using approved models — the code snippet below shows the configured endpoints and confirms no direct external AI provider access exists. Inference only; no training, fine-tuning, or embedding storage. Only PUBLIC data is sent.
>
> mAI Factory onboarding and model authorisation records are held by the ITSO/mAI team; requested.

**Screenshot:** C · **Snippet:** *186202 · 186208 — Snippets 1 and 2* · **File:** ITSO onboarding records — **request from WBG ITSO/mAI team**

---

# 21 — 186208 · Connections only with approved endpoints

**Paste:**
> **Correction to our earlier comment.** Open-Elevation and OSRM had been removed from the architecture documentation but **remained in the application code** until this update. During remediation we identified further undisclosed outbound calls — OpenStreetMap Overpass mirrors (including a Russian-hosted mirror), an alternative routing service, and a third-party basemap tile provider. **All have now been removed.**
>
> The code snippets below list every outbound host in deployed code. Three destinations remain:
> - Zambia GeoHub ArcGIS REST API — public data, no authentication
> - WBG mAI Factory gateway (`azapimdev.worldbank.org`) — Azure AD bearer token
> - Posit Connect OAuth endpoint — platform session token
>
> The verification snippet confirms `open-elevation`, `project-osrm`, `routing.openstreetmap`, `overpass`, `maps.mail.ru` and `cartocdn` now return no matches anywhere in the codebase.

**Screenshot:** none · **Snippet:** *186202 · 186208 — Snippets 2 and 3* · **File:** none

---

# 22 — 186209 · Certificate validation enforced

**Paste:**
> **Correction first:** Open-Elevation and OSRM remained in the code until this update despite having been removed from the documentation — see our correction on 186208. Both, and several other external services, are now removed. The updated SA document is attached.
>
> Certificate validation evidence in the snippets below:
> - Trust-store injection validating against the OS certificate store, including WBG internal certificate authorities, with the declared `truststore` dependency
> - A repository search for `verify=False`, `ssl._create_unverified` and `CERT_NONE` returning **no matches anywhere in the project**
>
> Three maintenance scripts previously had verification disabled. Verification was restored, and the scripts were removed from the deployment package.

**Screenshot:** none · **Snippet:** *186209 — Certificate validation* (both) · **File:** `ACN_Zambia_GeoHub_AI.docx`

---

# 23 — 186210 · Network traffic restricted

**Paste:**
> **Correction first:** see 186208 — Open-Elevation, OSRM and several other external services remained in the code until this update and are now removed. The updated SA is attached and matches the current architecture.
>
> The code snippet below lists the complete set of outbound hosts in deployed code: only ArcGIS and worldbank.org remain.
>
> The application opens no listening ports, uses no protocol other than HTTPS, and publishes no API — the attached runtime configuration shows it runs as hosted content with no custom ports. Firewall and network segmentation are managed by the platform and are not controllable by the application team.

**Screenshot:** D · **Snippet:** *186202 · 186208 — Snippet 3* · **File:** `ACN_Zambia_GeoHub_AI.docx`

---

# 24 — 186211 · Tokens not exposed in URLs, logs, or monitoring

**Paste:**
> Remediation evidence in the snippets below:
> - The token subsystem has been removed entirely. Eight code locations that could append a token to a URL are gone, along with the storage and refresh machinery. The application no longer reads an ArcGIS token at all.
> - A data request as the application actually issues it — no token parameter, no Authorization header
> - A repository search returning no matches for `ARCGIS_TOKEN` or any token-as-query-parameter pattern
>
> Also attached: Posit Connect configuration showing no `ARCGIS_TOKEN`; browser network activity from a QA session showing no token in any request URL; application logs showing no token values.
>
> mAI Factory and platform tokens are sent only in the HTTP Authorization header, server-side. The interface is rendered on the server, so no token reaches the browser, a link, or browser history.

**Screenshot:** A + F + K · **Snippet:** *186182 · 186188 · 186211 — No ArcGIS credential* (all 3) · **File:** none

---

# 25 — 186212 · Security events logged and monitored — GAP

**Paste:**
> Confirmed not in place at application level. The application performs no user authentication or authorisation of its own, so there are no in-application auth events to log. Platform logging — startup, access requests, runtime errors — exists and is attached. Monitoring, alerting, a triage process, and a named reviewer do not.
>
> Given Low time-criticality, public-only data, and nothing stored, we propose scoping this proportionately alongside 186217 and 186218, and request OIS direction on the minimum expected before building.

**Screenshot:** F · **Snippet:** none · **File:** none

---

# 26 — 186213 · Administrative actions auditable

**Paste:**
> The application has no in-application administrative functions, so there are no application-level admin actions to audit.
>
> Attached evidence for the actions that do exist:
> - Posit Connect deployment history for this content item, with timestamps
> - Source control commit history showing author, date and description for every change
>
> Posit Connect audit records for environment variable and access list changes are owned by the platform team; requested.

**Screenshot:** E · **Snippet:** none · **File:** `QA_Evidence/186213_change_history.txt`

---

# 27 — 186214 · Authentication and authorization failures logged

**Paste:**
> The application has no user login, so there are no in-application login failures. Service-to-service failures are captured: a failed OAuth token exchange or rejected mAI Factory request is caught, logged, and surfaced to the user. Sample logs attached.
>
> **Gaps:** these go to the platform log only, are not forwarded to a SIEM, and raise no alert on repeated failures (see 186217, 186218). No threshold for suspicious repeated failure is defined and no review process is documented.
>
> Platform-level authentication failure logs from Posit Connect and Azure AD are owned by those teams; requested.

**Screenshot:** F · **Snippet:** none · **File:** none

---

# 28 — 186216 · Logs do not contain secrets

**Paste:**
> Fixed. Logged error text now records only the exception type and message — service response bodies, service URLs and query parameters are excluded. Three error paths were corrected: the AI call, the OAuth token exchange, and the geospatial data fetch. See the code snippets below.
>
> Attached logs cover a full session — startup, data query, AI call, and an error condition — showing no tokens, credentials, prompts, uploaded content, or AI responses are written.
>
> Platform-level log redaction is owned by the Posit Connect team.

**Screenshot:** F · **Snippet:** *186199 · 186216 — Error handling and log content* (all 3) · **File:** none

---

# 29 — 186217 · Monitoring detects service failures and abnormal activity — GAP

**Paste:**
> Confirmed: no monitoring or alerting has been configured — no dashboards, thresholds, notification routing, reviewer ownership, or test alerts. We accept that the fallback behaviour previously described is fault tolerance, not detection, and does not satisfy this control.
>
> Nothing exists to screenshot. We request OIS direction on the minimum acceptable for an application of this profile — Low time-criticality, stateless, public-data-only, nothing stored — before building, so that what we implement matches expectations.

**Screenshot:** none · **Snippet:** none · **File:** none — **awaiting OIS direction**

---

# 30 — 186218 · All logs sent to WBG SIEM (Splunk)

**Paste:**
> Confirmed: no Splunk forwarding has been configured by this project. An application running as hosted content on Posit Connect cannot configure SIEM forwarding for the platform's own log pipeline.
>
> We have asked the Posit Connect platform team to confirm whether platform log forwarding to Splunk already covers all hosted content including this QA application. On their response we will attach either their confirmation and the Splunk source configuration, or — if not covered — a scoping proposal for OIS agreement.

**Screenshot:** F · **Snippet:** none · **File:** platform team confirmation — **request from Posit Connect admin**

---
---

# WHAT EACH EVIDENCE FILE IS FOR

| File | Used by |
|---|---|
| `ACN_Zambia_GeoHub_AI.docx` — regenerated SA | 3, 6, 8, 22, 23 |
| `QA_Evidence/186180_secret_scan.txt` | 5 |
| `QA_Evidence/186188_dataset_inventory.txt` | 8 |
| `QA_Evidence/186188_sample_api_call.txt` | 8 |
| `QA_Evidence/186203_ai_request_payload.txt` | 17 |
| `QA_Evidence/186213_change_history.txt` | 26 |

The other four `QA_Evidence/*.txt` files are superseded by the code snippets — keep them as backup but paste the snippets instead.

---

# THREE EMAILS TO SEND

1. **WBG ITSO / mAI team** — mAI Factory retention terms + platform onboarding and model authorisation records *(stories 19, 20)*
2. **Posit Connect admin** — does platform log forwarding to Splunk cover this content item? *(story 30)*
3. **OIS** — what is the minimum acceptable monitoring for this risk profile? *(stories 25, 29)*

These are the only things now standing between you and a complete submission.

---

*Reference: ACN-2026-31023*
