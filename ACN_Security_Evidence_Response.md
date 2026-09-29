# Security Evidence Response
### Zambia Geospatial Intelligence Assistant | ACN-2026-31023

Responses to the security evidence request. The original request contained repeated items; these have been consolidated into 15 unique questions, answered below.

**How to read the status labels:**
- **Evidenced** — the control is in place and we can demonstrate it
- **Gap** — not in place; stated plainly, with what we propose to do about it
- **Platform-owned** — controlled by the WBG hosting or platform teams, not by this application

---

## 1. Authentication to integrated services uses approved federated identity
**Status: Evidenced**

The application connects to two external services. Neither requires the application to hold a password, API key, or any other stored credential.

**WBG mAI Factory (AI service):** Authentication uses the Posit Connect OAuth 2.0 token exchange (RFC 8693). The process works as follows:

1. When a user opens the application, Posit Connect automatically issues a session token for that user. The application does not create or configure this — the hosting platform provides it.
2. The application presents that session token to Posit Connect and exchanges it for a short-lived Azure AD access token, scoped specifically to the mAI Factory service.
3. That access token is used for one request and then discarded. It is never written to disk, never stored, and never reused after the session.

Because the token is issued fresh per session by the platform, **there is no credential stored anywhere in the application** — not in the code, not in configuration files, not in the deployment package.

**Zambia GeoHub (geospatial data):** No authentication is used at all. The application only reads **public** datasets, which are openly available and require no credential. Private dataset access was removed from the application during the security architecture review.

**Evidence we can provide:** a screenshot of the Posit Connect settings page showing the mAI Factory integration attached to this application; a walkthrough of the token exchange sequence.

---

## 2. User input is validated and sanitised before processing
**Status: Partially in place — genuine gaps stated below**

**What is in place:**

- **File upload restrictions.** Users may only upload PDF, Word, text, and common image file types. Any other file type is rejected before it reaches the application. Upload size is capped by the hosting platform.
- **User text is not passed directly into data queries.** When a user asks a question in plain English, the application does not take their words and insert them into a database or API query. Instead, it extracts only a place name and a topic, using a strict pattern that accepts nothing but ordinary alphabetic words (maximum three). Punctuation, symbols, query syntax, and command characters cannot get through this step. This substantially limits what a malicious input could achieve.
- **The AI is constrained to retrieved data.** The AI is instructed to answer only from records actually retrieved from the Zambia GeoHub, and is prohibited from producing statistics, coordinates, distances, or location details that are not supported by that data.

**What is not in place — stated plainly:**

- There is **no dedicated input sanitisation layer**, and **no specific defence against prompt injection** beyond the instructions given to the AI. A user's typed question is passed to the AI service as written.
- Where a place name is used to filter data, it is inserted into the query as text rather than through a parameterised query mechanism. The strict word-pattern restriction described above is the mitigating control, but it is a restriction on input shape rather than a structural separation of data from query.
- **No formal secure code review has been carried out, and there is no automated test suite.** Testing to date has been hands-on functional testing in the QA environment.

**What we propose:** validate the extracted place name against a fixed list of known Zambian districts and provinces before it is used — so that only a name from a known, closed list can ever reach a data query. We would also welcome guidance on an expected standard for prompt-injection testing. Timeline to be agreed with OIS.

---

## 3 & 13. All AI requests route through the approved enterprise AI platform, using approved models only
**Status: Evidenced**

Every AI request from this application goes to the **WBG mAI Factory gateway**. There is no other AI destination configured.

**Approved models in use, all reached through that gateway:**
- GPT-5, GPT-5 mini, GPT-4o, GPT-4o mini (via Azure OpenAI)
- Claude Sonnet 4.6, Claude Haiku 4.5 (via Amazon Bedrock)

Access uses the Azure AD token described in Question 1 — the application cannot reach the AI service without a token issued by the platform.

**Endpoint migration:** the WBG mAI Factory team announced in August 2026 that their existing API addresses were being retired (deprecated 31 August 2026, disabled 30 September 2026). The application was updated to the replacement addresses in line with that notice.

**Previously identified issue, now fixed:** the application originally included the ability to call OpenAI and Google Gemini directly, left over from early development before the WBG AI service was available. Those were never used in this deployment, but the capability existed in the software. **Both have now been completely removed** — the configuration, the connection code, and the supporting software library. The application now has no technical means of contacting an AI provider directly; the only route available to it is the WBG gateway.

---

## 4. Authentication tokens are not exposed in URLs, logs, browser history, or client-side code
**Status: Evidenced — the issue raised has been fixed**

The reviewer correctly identified that the original design passed an ArcGIS access token as part of the web address (a URL parameter), which would expose it in server logs and browser history. This has been addressed:

- **The feature that needed that token — access to private datasets — was removed from the application's scope** during the security architecture review. The application now reads public data only.
- **The underlying capability has now been removed from the software entirely.** This included eight separate places where a token could have been added to a web address, plus the supporting machinery that stored the token, refreshed it, and wrote it back to a configuration file. All of it is gone. The application no longer looks for an ArcGIS token at all.
- The result is that this is now **structurally impossible rather than merely switched off** — there is no code left that could place a credential in a web address, regardless of configuration.

**AI service tokens** are sent only in the request's authorisation header, from the server, never in a web address. They exist in server memory for the duration of a single request. The application's user interface is generated entirely on the server, so no token is ever sent to the user's browser or visible in page source.

**Logging:** the application does not write tokens to logs. Redaction at the hosting-platform level is **platform-owned** and we are requesting that configuration from the Posit Connect team.

---

## 5 & 9. Logs forwarded to WBG SIEM/Splunk; security events logged and monitored
**Status: Gap — partly dependent on the hosting platform**

**Stated plainly: this is not in place.** The application does not generate its own security event log, and this project has not configured any forwarding to Splunk.

What does exist is the standard logging provided by the Posit Connect hosting platform — application start-up, access requests, and error records — which we can show from the platform's log viewer.

**Platform dependency:** whether Posit Connect already forwards its logs to WBG Splunk is a property of the hosting platform, not something this application controls or can configure. **We have asked the Posit Connect platform team to confirm** whether such forwarding already applies to everything hosted there.

This is one of the outstanding conditions of the conditional approval. The next step depends on the platform team's answer:
- If forwarding already exists at platform level, we will supply their confirmation and configuration.
- If it does not, application-level logging and forwarding will need to be built, and we would ask OIS to agree a scope and timeline.

---

## 6. AI services do not retain data beyond approved retention requirements
**Status: Evidenced for the application — platform-owned for the AI gateway**

**The application itself stores nothing.** This is a design property, not a configuration setting:

- There is no database, no file storage, and no cache anywhere in the application.
- Questions, AI answers, retrieved map data, and any uploaded document exist only in temporary server memory while the user's session is active, and are discarded when it ends.
- Word and PDF reports are assembled in memory and sent straight to the user's browser. No copy is written to the server.
- No question history is kept, and nothing is used to train or fine-tune any AI model.

**What is sent to the AI service:** the user's question, a description of the dataset being used, up to 15 sample records from that public dataset, and pre-calculated totals. All of it is public infrastructure data — facility names, categories, and map coordinates. **No personal data is sent.**

**AI gateway retention — platform-owned:** how long the WBG mAI Factory retains the requests it processes is governed by that service's own terms, which belong to the WBG ITSO/mAI team. This application has no setting that influences it. We are requesting that documentation from them to attach.

---

## 7. AI-generated output is reviewed by users before business use
**Status: Evidenced, with one gap**

Three safeguards are built into the product:

- **Low-confidence warnings.** The application displays a prominent warning when the answer should not be relied on — specifically when no records were found for the place asked about, when live data was unavailable and an offline copy was used instead, or when too few records were found to support a general conclusion. The AI is separately instructed to state the limitation in its own answer, so the caveat appears in both places. This has been tested in the QA environment against all three conditions.
- **Source citation.** Every answer displays which dataset it came from, with a link to that dataset on the Zambia GeoHub, and an indicator showing whether the data was retrieved live or from the offline copy.
- **No-guessing rule.** The AI is instructed to state plainly when data is unavailable rather than estimate. This was verified in testing: asked about mines in a district with no mining records, the application reported that no records existed and advised checking the live data source, rather than producing a figure.

**Gap:** these are safeguards built into the software. There is **no written procedure requiring a person to formally review and sign off** on AI output before it is used in a business decision, and no user training material. If OIS requires a documented review step, that procedure needs to be written and agreed with the Business Owner.

**Evidence we can provide:** screenshots of the warning banner and source citation; test records from the QA environment.

---

## 8 & 12. Certificate validation enforced; encrypted transport (TLS 1.2+)
**Status: Evidenced — an issue was found and fixed**

**All connections are encrypted (HTTPS) and certificates are verified.** The application uses the operating system's certificate store for validation, which allows it to correctly verify WBG's internal certificates. If a certificate were invalid, expired, self-signed, or issued to the wrong host, the connection would be rejected.

**Note on scope:** the request mentions Open-Elevation and OSRM. **These services were removed from the application** during the architecture review. The application now connects to only three destinations: the Zambia GeoHub, the WBG mAI Factory gateway, and the Posit Connect authentication service.

**Issue found and fixed:** three maintenance scripts in the project had certificate checking switched off. These were tools used by the developer, not part of the running application — but they were being copied to the server with the application, so a security scan would have flagged them. Two corrections were made: certificate checking was restored in all three scripts, and the scripts were removed from the deployment package altogether, since they serve no purpose on the server. **There is now no place anywhere in the project where certificate verification is disabled.**

**TLS version enforcement and server certificates** are determined by the Posit Connect hosting platform and by the services being called — **platform-owned**. The application makes no unencrypted connections and does not negotiate down to older protocol versions.

---

## 10. Monitoring detects service failures and abnormal activity
**Status: Gap**

**Stated plainly: no monitoring, alerting, dashboards, or alert thresholds have been set up by this project.** There are no alert examples, no escalation procedure, and no named person reviewing alerts.

What does exist is fault tolerance built into the product rather than monitoring: if the Zambia GeoHub is unreachable the application falls back to a bundled offline copy of the data and tells the user it has done so; if the AI service fails, the error is caught and shown to the user without crashing the session. This keeps the service usable during a failure, but it does not notify anyone that a failure occurred.

Availability monitoring of the Posit Connect platform itself is **platform-owned**.

Given this application is classified Low time-criticality and stores no data, we propose scoping monitoring proportionately, and would welcome OIS guidance on the minimum expected for an application of this size and risk.

---

## 11. Network traffic restricted to required business communications
**Status: Evidenced for the application — platform-owned for network controls**

By design, the application communicates with only three external destinations, all over HTTPS:

| Destination | Purpose | Authentication |
|---|---|---|
| Zambia GeoHub (ArcGIS) | Reading public geospatial data | None — public data |
| WBG mAI Factory gateway | AI analysis | Azure AD token from platform exchange |
| Posit Connect authentication service | Obtaining that token | Platform-issued session token |

Incoming traffic is HTTPS from the user's browser through Posit Connect only. The application opens no network ports of its own and publishes no API for other systems to call.

Two third-party services that were previously used (Open-Elevation and OSRM) were **removed** during the architecture review, reducing the number of external destinations.

**Firewall rules, security groups, and network segmentation** are **platform-owned** — the application runs as hosted content on Posit Connect and has no control over network policy. We are requesting this evidence from the platform team.

**Evidence we can provide:** the approved architecture diagram showing every connection the application makes.

---

## 14. User access limited to approved business functions
**Status: Gap — formal exception requested**

**Stated plainly: the application does not have role-based access control.** Everyone who can open it sees the same thing.

Access is controlled at two levels outside the application: it is reachable only from inside the WBG network, and Posit Connect controls who may open the content.

**Why we are requesting an exception rather than building this:** the application handles **public data only**. Every user receives identical public information regardless of who they are. There are no administrative screens, no ability to change or delete anything, and no privileged operations — it is read-only against public data. There is therefore no differentiated access to control.

This corresponds to condition #1 of the conditional approval, and we are submitting it as a **formal exception request** for EA/OIS decision, rather than treating it as closed on our own judgement. **If the data classification ever changes to include non-public data, role-based access control would be implemented first, as a prerequisite to that change.**

---

## 15. The application processes only PUBLIC-classified data
**Status: Evidenced**

- **Public-only is enforced by design.** Access to private and restricted datasets was removed from the application during the security architecture review, in direct response to earlier OIS feedback.
- **The strongest evidence is that no credential exists.** Restricted datasets cannot be read without authentication, and the application holds no ArcGIS credential of any kind. It is therefore not capable of retrieving anything other than public data.
- **No personal data is involved.** The datasets are infrastructure and facility records — schools, health facilities, settlements, roads, administrative boundaries — containing facility names, categories, and map coordinates.
- **What reaches the AI service** is limited to the user's question, a dataset description, up to 15 sample public records, and summary counts.

**Evidence we can provide:** the dataset list with classifications; a sample request and response showing an unauthenticated public query and the fields returned; the architecture diagram showing what is sent to the AI service.

---

## Summary

| # | Question | Status |
|---|---|---|
| 1 | Federated identity for integrated services | Evidenced |
| 2 | Input validation and sanitisation | Partial — gaps stated, remediation proposed |
| 3 & 13 | Approved AI platform and models only | Evidenced — direct external AI access removed |
| 4 | Tokens not exposed in URLs or logs | Evidenced — issue raised has been fixed |
| 5 & 9 | Splunk forwarding and security event logging | Gap — awaiting platform team confirmation |
| 6 | AI data retention | Evidenced for application; gateway terms platform-owned |
| 7 | AI output reviewed before business use | Evidenced — no formal written procedure |
| 8 & 12 | Certificate validation and TLS 1.2+ | Evidenced — issue found and fixed |
| 10 | Monitoring for failures and abnormal activity | Gap — proportionate scoping proposed |
| 11 | Network traffic restricted | Evidenced for application; network controls platform-owned |
| 14 | User access limited to approved functions | Exception requested — public data only |
| 15 | Processes PUBLIC-classified data only | Evidenced |

**Three items were identified and fixed during preparation of this response:** the ability to place a credential in a web address (Question 4), certificate checking disabled in maintenance scripts that were being copied to the server (Question 8), and unused direct connections to external AI providers (Question 3).

**Three items remain genuinely open:** Splunk log forwarding, monitoring and alerting, and role-based access control — the last submitted as an exception request on the basis that the application handles public data only.

---

*Prepared by: [Your Name], [Your Role]*
*Date: [submission date]*
*Reference: ACN-2026-31023*
