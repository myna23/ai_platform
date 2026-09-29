# Story Answers — paste and attach
### ACN-2026-31023 | Round 2

Each story: the comment to paste, then what to attach. Screenshot letters and evidence files are listed in `ACN_Evidence_Guide.md`.

**Closed:** 186178

---

## 186168 — Access restricted to authorized users

> Access is enforced by the hosting platform. The application runs on WBG Posit Connect, is reachable only from inside the WBG network, and Posit Connect controls who may open it. The attached configuration shows the authorised viewer list for this QA content item.
>
> The application has no separate login because it serves PUBLIC data only — every authorised user sees identical information.

**Attach:** Screenshot B

---

## 186170 — Administrative access limited to designated administrators

> The application has no administrative interface and no privileged functions. The attached application screenshot shows the complete user function set — chat, map, data table, download — all read-only.
>
> Administration is platform-level only: deploying, setting environment variables, viewing logs. The attached Posit Connect configuration shows these are limited to the content owner and named collaborators.

**Attach:** Screenshot B + Screenshot J

---

## 186174 — User access limited to approved business functions — EXCEPTION REQUESTED

> **On the mismatch raised:** the SA document reviewed was the June version. The updated SA is attached and confirms the application processes **PUBLIC data only** — private dataset access was removed from scope and the ArcGIS token removed from the code.
>
> **Exception basis:** with public-only data, every user receives identical information. The attached application screenshot shows the full function set, all read-only, with no administrative screens and nothing that can be created, changed, or deleted. There is no differentiated function or dataset to restrict.
>
> Submitted as a formal exception for EA/OIS decision. If the data classification ever changes to include non-public data, RBAC will be implemented first as a prerequisite.

**Attach:** Regenerated SA doc + Screenshot B + Screenshot J

---

## 186180 — Secrets not hardcoded ✅

> Secret scan completed with detect-secrets 1.5.0 (27 detector plugins) across all git-tracked files. **Result: PASS — no secrets, credentials, API keys, tokens, or passwords found.**
>
> The scanner raised 143 entropy flags; all were reviewed. 92 are public ArcGIS dataset identifiers appearing in public Zambia GeoHub URLs, 51 are MD5 checksums in the deployment manifest. Zero required action.
>
> The scan also surfaced stale references to credentials the application no longer uses. None were live secrets — all were templates or documentation — and all have been corrected: the `.env.example` placeholder key removed and the file excluded from deployment, two token-management scripts deleted, an unused ArcGIS username/password code path removed from the bundle, and four documentation files fixed that had documented `OPENAI_API_KEY`, `ARCGIS_TOKEN`, and token-in-URL examples.

**Attach:** `186180_secret_scan.txt` + Screenshot A

---

## 186182 — Access tokens rotated according to defined procedures ✅

> **The token this control was raised against no longer exists.** The updated SA document is attached; the version reviewed predated the scope change.
>
> Attached evidence shows the Posit Connect environment with **no `ARCGIS_TOKEN`**, and a repository search returning **no matches** for `ARCGIS_TOKEN`, `get_token.py`, or any ArcGIS token handling. The entire subsystem — storage, refresh, persistence to configuration — has been removed.
>
> The only remaining tokens are the Posit Connect session token and the Azure AD bearer token, both short-lived, platform-issued per session, and discarded after use. No manual rotation procedure is required because no static token is held.

**Attach:** Regenerated SA doc + `186182_186188_186211_no_arcgis_token.txt` + Screenshot A

---

## 186184 — Administrative access to secrets restricted and auditable

> No application secrets exist, so there is no secret store to restrict — the attached environment configuration shows only a non-sensitive flag. Permission to view or change it is limited to the content owner and named collaborators, shown in the attached access configuration.
>
> Audit logging of platform configuration changes is owned by the Posit Connect platform team; requested.

**Attach:** Screenshot A + Screenshot B

---

## 186188 — Only PUBLIC data processed ✅

> **On the mismatch raised:** the SA reviewed was the June version. The updated SA is attached and states the application processes **only Public** datasets.
>
> Four pieces of evidence attached:
> 1. Dataset inventory — all **62** catalogue datasets, every one PUBLIC, zero Internal Use Only, zero Restricted
> 2. A live unauthenticated API request returning public school records — no token, no Authorization header, no credential
> 3. A **control test**: a token-required ArcGIS layer requested without a credential returned **`error 499: Token Required`** — demonstrating the application cannot reach non-public data
> 4. Posit Connect environment configuration showing no ArcGIS credential
>
> The decisive point: no credential exists, so retrieving anything but public data is not possible.

**Attach:** Regenerated SA doc + `186188_dataset_inventory.txt` + `186188_sample_api_call.txt` + `186182_186188_186211_no_arcgis_token.txt` + Screenshot A

---

## 186189 — Restricted data and PII not processed ✅

> The geospatial datasets contain no personal data — facility names, categories, coordinates only. Restricted data cannot be retrieved because no credential exists (see 186188).
>
> **We disclosed that users can attach a document whose text is sent to the AI, and that the application does not inspect uploaded content. A data-handling control has now been added:**
>
> 1. A notice is permanently displayed beneath the chat input: *"content of any file you attach is sent to the WBG mAI Factory for analysis. Do not attach personal data, or Confidential, Restricted, or Internal Use Only material. This application is approved for PUBLIC data only."*
> 2. On attaching a file, a prominent warning requires the user to confirm it contains no personal or restricted material.
>
> Attached content is never written to disk, exists only in session memory, and goes only to the WBG-approved gateway.

**Attach:** Screenshot L (chat input notice + attachment warning)

---

## 186191 — Data limited to the minimum required

> Attached evidence shows the enforced limits: maximum **200 records** retrieved per query, filtered to the requested district or province, and maximum **15 sample records** sent to the AI. Totals are pre-calculated before transmission so full record sets are never sent. Only the single most relevant dataset is queried.

**Attach:** `186203_data_minimisation.txt`

---

## 186192 — User requests and generated content not persistently stored

> The application is stateless — no database, file store, or cache. Questions, AI responses, retrieved data, and uploads are held in session memory only and released when the session ends. Reports are built in memory and streamed to the browser with no server copy.
>
> The attached logs show a complete session: no prompts, responses, or uploaded content are written.

**Attach:** Screenshot F

---

## 186194 — Temporary files securely disposed of

> No temporary files are created, so there is no disposal process. Reports are constructed in memory and streamed directly to the browser; uploads and retrieved data are held in memory only. The application clears uploaded content from session state when an attachment is removed or a new conversation starts.
>
> Nothing is written to the filesystem, so nothing can persist after a session or be recovered from disk.

**Attach:** `186203_data_minimisation.txt`

---

## 186196 — Data exports only to authorized users

> Confirming the point raised: app access in QA is restricted to authorised users through Posit Connect. The attached access configuration shows the assigned users for this content item, and the attached screenshot shows an authenticated authorised user with the Word/PDF download options available.
>
> The application has no role-based restriction within it (see the exception under 186174), but every export contains only PUBLIC data — no restricted data, personal data, or credential can appear in one, because none can be retrieved.

**Attach:** Screenshot B + Screenshot I

---

## 186198 — User input validated and sanitised ✅

> Input validation has been strengthened. A place name taken from user text is now used in a dataset query **only if it appears in a closed allowlist** of known Zambian districts and provinces — 126 entries, loaded at startup from the bundled administrative boundary data. Anything else is rejected before query construction, so no user-supplied string can reach a query clause.
>
> This layers on the existing restriction, which already limited candidates to 1–3 plain alphabetic words so punctuation, symbols and query syntax could not be captured.
>
> Attached test results cover 8 cases including injection attempts (`' OR 1=1--`, `Robert'); DROP TABLE schools;--`) and script payloads — all rejected — with valid districts still accepted.

**Attach:** `186198_input_validation.txt`

---

## 186199 — Error handling prevents disclosure ✅

> Fixed. The application no longer shows technical error text to users — unexpected failures return a generic message directing the user to retry or contact the application owner. Technical detail is retained server-side only.
>
> The two OAuth failure paths that previously included part of the authorisation service's response body have been corrected: they now record only the HTTP status code and a fixed description. No service response body appears in any error path.
>
> Attached logs show a session including an error condition, with no sensitive content.

**Attach:** Screenshot F

---

## 186202 — AI routed through approved enterprise platforms ✅

> Attached evidence shows the current QA implementation:
> - All AI endpoints configured in the application — **only** `azapimdev.worldbank.org`, using the `maifactory/openai` path for GPT and the Bedrock path for Claude
> - A repository search returning **no matches** for `OPENAI_API_KEY`, `GOOGLE_API_KEY`, or the Google generative-AI library — the direct-provider code and its dependency are removed
> - A complete list of every outbound host in deployed code: only ArcGIS and worldbank.org remain
>
> The attached Posit Connect configuration shows the mAI Factory OAuth integration bound to this content item, which is how the bearer token is obtained.

**Attach:** `186202_186208_186209_186210_approved_endpoints.txt` + Screenshot C

---

## 186203 — Data to AI limited to approved content ✅

> A real request payload is attached, generated by the application's own prompt-construction code against live public data. It shows **148 records retrieved, exactly 15 transmitted**, and the complete message content: the user's question, dataset metadata, 15 sample records, pre-aggregated totals, and the grounding rules. Nothing else.
>
> No credential, token, session identifier, or user identity appears. Records carry facility name, type and location only.
>
> Attached code evidence shows the 200/15 caps enforced in configuration.

**Attach:** `186203_ai_request_payload.txt` + `186203_data_minimisation.txt` + Screenshot H

---

## 186204 — AI outputs reviewed by users prior to business use

> QA evidence attached showing the user review step in the running application:
>
> 1. **Low-confidence warning** — asked *"How many mines are in Rufunsa?"*, the application displays a warning banner and the AI states no records exist rather than producing a number.
> 2. **Source citation** — asked *"How many schools are in Lusaka?"*, the answer displays the source dataset with a link to it on the Zambia GeoHub and an indicator showing whether data was live or offline.
>
> Together these show the user is presented with the data source, its freshness, and an explicit reliability warning before acting on any answer.
>
> **Remaining gap:** no written procedure requires formal sign-off before AI output is used in a decision, and no user training material exists. If a documented review step is required we will draft it with the Business Owner — please confirm the expected form.

**Attach:** Screenshot G + Screenshot H

---

## 186205 — AI services do not retain data beyond approved retention

> **Application:** stateless, nothing retained. Attached logs show a complete session with no prompts, responses, or content written.
>
> **AI gateway:** retention is governed by the WBG mAI Factory service terms, owned by the ITSO/mAI team. This application has no configuration that influences it. Requested and will be attached on receipt.

**Attach:** Screenshot F — plus ITSO retention terms when received

---

## 186206 — AI integrations comply with AI governance

> All inference routes exclusively through the WBG mAI Factory gateway using approved models — attached evidence shows the configured endpoints and confirms no direct external AI provider access exists. Inference only; no training, fine-tuning, or embedding storage. Only PUBLIC data is sent.
>
> mAI Factory onboarding and model authorisation records are held by the ITSO/mAI team; requested.

**Attach:** `186202_186208_186209_186210_approved_endpoints.txt` + Screenshot C — plus ITSO records when received

---

## 186208 — Connections only with approved endpoints ✅

> **Correction to our earlier comment.** Open-Elevation and OSRM had been removed from the architecture documentation but **remained in the application code** until this update. During remediation we identified further undisclosed outbound calls — OpenStreetMap Overpass mirrors (including a Russian-hosted mirror), an alternative routing service, and a third-party basemap tile provider. **All have now been removed.**
>
> The attached evidence lists every outbound host in deployed code. Three destinations remain:
> - Zambia GeoHub ArcGIS REST API — public data, no authentication
> - WBG mAI Factory gateway (`azapimdev.worldbank.org`) — Azure AD bearer token
> - Posit Connect OAuth endpoint — platform session token
>
> The evidence confirms `open-elevation`, `project-osrm`, `routing.openstreetmap`, `overpass`, `maps.mail.ru` and `cartocdn` now return no matches anywhere in the codebase.

**Attach:** `186202_186208_186209_186210_approved_endpoints.txt`

---

## 186209 — Certificate validation enforced ✅

> **Correction first:** Open-Elevation and OSRM remained in the code until this update despite having been removed from the documentation — see our correction on 186208. Both, and several other external services, are now removed. The updated SA document is attached.
>
> Certificate validation evidence attached, showing:
> - A repository search for `verify=False`, `ssl._create_unverified` and `CERT_NONE` returning **no matches anywhere in the project**
> - Trust-store injection validating against the OS certificate store, including WBG internal certificate authorities
> - The declared `truststore` dependency
>
> Three maintenance scripts previously had verification disabled. Verification was restored, and the scripts were removed from the deployment package.

**Attach:** Regenerated SA doc + `186209_certificate_validation.txt` + `186202_186208_186209_186210_approved_endpoints.txt`

---

## 186210 — Network traffic restricted ✅

> **Correction first:** see 186208 — Open-Elevation, OSRM and several other external services remained in the code until this update and are now removed. The updated SA is attached and matches the current architecture.
>
> The attached evidence lists the complete set of outbound hosts in deployed code: only ArcGIS and worldbank.org remain.
>
> The application opens no listening ports, uses no protocol other than HTTPS, and publishes no API — the attached runtime configuration shows it runs as hosted content with no custom ports. Firewall and network segmentation are managed by the platform and are not controllable by the application team.

**Attach:** Regenerated SA doc + `186202_186208_186209_186210_approved_endpoints.txt` + Screenshot D

---

## 186211 — Tokens not exposed in URLs, logs, or monitoring ✅

> Remediation evidence attached:
> - Repository search showing **no matches** for `ARCGIS_TOKEN` or any token-as-query-parameter pattern. Eight code locations that could append a token to a URL have been removed, along with the subsystem that stored and refreshed it. The application no longer reads an ArcGIS token at all.
> - Posit Connect environment configuration showing **no `ARCGIS_TOKEN`**
> - Browser network activity from a QA session showing no token in any request URL
> - Application logs showing no token values
>
> mAI Factory and platform tokens are sent only in the HTTP Authorization header, server-side. The interface is rendered on the server, so no token reaches the browser, a link, or browser history.

**Attach:** `186182_186188_186211_no_arcgis_token.txt` + Screenshot A + Screenshot F + Screenshot K

---

## 186212 — Security events logged and monitored — GAP

> Confirmed not in place at application level. The application performs no user authentication or authorisation of its own, so there are no in-application auth events to log. Platform logging — startup, access requests, runtime errors — exists and is attached. Monitoring, alerting, a triage process, and a named reviewer do not.
>
> Given Low time-criticality, public-only data, and nothing stored, we propose scoping this proportionately alongside 186217 and 186218, and request OIS direction on the minimum expected before building.

**Attach:** Screenshot F

---

## 186213 — Administrative actions auditable

> The application has no in-application administrative functions, so there are no application-level admin actions to audit.
>
> Attached evidence for the actions that do exist:
> - Posit Connect deployment history for this content item, with timestamps
> - Source control commit history showing author, date and description for every change
>
> Posit Connect audit records for environment variable and access list changes are owned by the platform team; requested.

**Attach:** `186213_change_history.txt` + Screenshot E

---

## 186214 — Authentication and authorization failures logged

> The application has no user login, so there are no in-application login failures. Service-to-service failures are captured: a failed OAuth token exchange or rejected mAI Factory request is caught, logged, and surfaced to the user. Sample logs attached.
>
> **Gaps:** these go to the platform log only, are not forwarded to a SIEM, and raise no alert on repeated failures (see 186217, 186218). No threshold for suspicious repeated failure is defined and no review process is documented.
>
> Platform-level authentication failure logs from Posit Connect and Azure AD are owned by those teams; requested.

**Attach:** Screenshot F

---

## 186216 — Logs do not contain secrets ✅

> Fixed. Logged error text now records only the exception type and message — service response bodies are excluded. The two OAuth failure paths that previously included part of the authorisation service's response now record only the HTTP status code and a fixed description.
>
> Attached logs cover a full session — startup, data query, AI call, and an error condition — showing no tokens, credentials, prompts, uploaded content, or AI responses are written.
>
> Platform-level log redaction is owned by the Posit Connect team.

**Attach:** Screenshot F

---

## 186217 — Monitoring detects service failures and abnormal activity — GAP

> Confirmed: no monitoring or alerting has been configured — no dashboards, thresholds, notification routing, reviewer ownership, or test alerts. We accept that the fallback behaviour previously described is fault tolerance, not detection, and does not satisfy this control.
>
> Nothing exists to screenshot. We request OIS direction on the minimum acceptable for an application of this profile — Low time-criticality, stateless, public-data-only, nothing stored — before building, so that what we implement matches expectations.

**Attach:** nothing — awaiting OIS direction on scope

---

## 186218 — All logs sent to WBG SIEM (Splunk) — PENDING PLATFORM ANSWER

> Confirmed: no Splunk forwarding has been configured by this project. An application running as hosted content on Posit Connect cannot configure SIEM forwarding for the platform's own log pipeline.
>
> We have asked the Posit Connect platform team to confirm whether platform log forwarding to Splunk already covers all hosted content including this QA application. On their response we will attach either their confirmation and the Splunk source configuration, or — if not covered — a scoping proposal for OIS agreement.

**Attach:** Screenshot F — plus platform team confirmation when received

---
---

# STATUS

**Evidence ready — 16 stories:** 186168, 186170, 186174, 186180, 186182, 186184, 186188, 186189, 186191, 186192, 186194, 186196, 186198, 186199, 186202, 186203, 186208, 186209, 186210, 186211, 186213, 186216

**Needs a screenshot session — 2:** 186204 (G + H), plus L for 186189

**Waiting on someone else — 5:**
| Story | Who | What |
|---|---|---|
| 186205, 186206 | WBG ITSO / mAI team | Retention terms, onboarding records |
| 186218 | Posit Connect admin | Does platform logging forward to Splunk? |
| 186212, 186217 | OIS | Minimum monitoring scope for this risk profile |

**Fixed this round:** error disclosure (186199, 186216), input validation allowlist (186198), upload data-handling notice (186189), secret scan + stale credential cleanup (186180), dataset inventory and live API proof (186188), AI payload sample (186203).

---

*Reference: ACN-2026-31023*
