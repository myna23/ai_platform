# Testing Readiness Tab — Answers to Paste

Accreditation Request (Cloud & 3rd Party Risk) portal → Testing Readiness tab.
`>>> YOU <<<` marks fields only you can fill.

---

**Please enter previous approved case numbers (if applicable to this case)**
`>>> YOU <<<` — ACN case number from the approval notice.

---

**Have all the security controls been implemented using standard methods discussed with the Security Architect?**

**Answer: Yes** — this question is about the controls agreed in the Security Architecture phase, not the seven advisory recommendations issued alongside the approval. Confirm against your SA report before answering; if everything it specifies is in place, "Yes" is correct.

> Yes. The security controls defined during the Security Architecture phase are implemented:
>
> • Data scope restricted to public datasets only — private/token-gated dataset access was removed entirely, eliminating the ArcGIS token dependency and its manual rotation risk.
> • No PII is collected, stored, or transmitted. The application is fully stateless — no user queries, AI responses, or geospatial data are written to disk on the server.
> • AI service authentication uses Posit Connect OAuth 2.0 token exchange (RFC 8693) with short-lived Azure AD Bearer tokens. No API keys are stored in application code or configuration.
> • TLS certificate verification is enforced on all outbound calls (system trust store injection via `truststore`); a prior verification bypass was removed.
> • Third-party public API dependencies (Open-Elevation, OSRM) were removed from the architecture, reducing the external attack surface to two WBG-approved services.
> • AI grounding controls: responses are constrained to data retrieved from the Zambia GeoHub at query time; the model is instructed not to generate statistics, coordinates, or location attributes without supporting source data.
> • Threshold-based low-confidence detection with user-facing disclaimers, triggered when no matching records are found, when offline fallback data is used, or when the record count falls below the defined threshold.
> • Controlled deployment promotion: changes are staged on a development branch and manually promoted to the production branch, which is the only branch that deploys.
>
> Separately, on the seven advisory recommendations issued with the approval: five are addressed (AI grounding, confidence thresholds with user disclaimers, staged deployment promotion, and two that no longer apply following the removal of private-dataset access). Entra ID RBAC is not applicable given the Public-only data classification, with written justification provided. SPLUNK log forwarding is pending confirmation from the Posit Connect platform team on whether it is already handled at the hosting-platform level. Full detail in the attached recommendations response.

---

**Is the Application Development complete?**
`>>> YOU <<<` — core functionality is built and deployed; your call whether to mark it complete given ongoing iteration.

---

**Have the Application UAT and System Integration tests completed?**

**Answer: Yes**

> Yes. System integration testing has been completed end-to-end in the deployed environment, covering all external integrations in scope: authentication to the WBG mAI Factory via Posit Connect OAuth 2.0 token exchange (verified with live model responses), live geospatial data retrieval from the Zambia GeoHub ArcGIS REST API (verified against exact record counts), and deployment through the WBG Posit Connect hosting platform. Application functionality has been tested across representative user scenarios including natural-language queries, two-area comparisons, dataset summarization, and the low-confidence disclaimer logic under zero-result, offline-fallback, and normal-data conditions. Test evidence can be provided on request. If OIS requires results recorded against a specific UAT template or test-case format, please share it and we will document accordingly.

---

**There is no deviations between the implementation and the SA report.**

**Answer: Yes (no deviations)** — with one noted platform change; see below. Confirm your SA report version matches the current architecture diagram before submitting.

> Correct — the implementation matches the approved Security Architecture. The scope reductions incorporated during the review (removal of private/token-gated dataset access and removal of third-party public APIs) were made in response to OIS review feedback and are reflected in the approved architecture.
>
> One subsequent change to note: the WBG mAI Factory team migrated their API endpoints from the legacy `conversationalai/` path to the new `maifactory/` endpoints (legacy endpoints deprecated 31 August 2026, disabled 30 September 2026), and introduced the Azure APIM Gateway (COM Gateway) layer. The application was updated accordingly. This is a WBG platform-mandated migration rather than an architecture change initiated by this project; the updated architecture diagram reflecting it is attached.

---

**What is the confirmed Go-Live date?**
`>>> YOU <<<`

---

**List all AI/ML components, models, agents, APIs, and related resources used by the application, including their resource names and intended usage; if no AI resources are in scope, enter "N/A".**

> GPT-5, GPT-5 mini, GPT-4o, GPT-4o mini (Azure OpenAI) — accessed via WBG mAI Factory through the Azure APIM Gateway (COM Gateway) to the mAI LLM End Points. Used for natural-language question answering, two-area comparison, and dataset summarization over Zambia GeoHub data.
>
> Claude Sonnet 4.6, Claude Haiku 4.5 (Amazon Bedrock) — accessed via the same WBG mAI Factory / Azure APIM Gateway path. Same intended usage; user-selectable alternative to GPT.
>
> Both are used for inference only — no model training, fine-tuning, or embedding storage. All responses are grounded in records retrieved from the Zambia GeoHub at query time. No user data or query history is used to train any model.

---

**Please list all application QA endpoints in scope for testing**

**Answer:** paste the app's browser URL — the rest is confirmed below.

> The application is deployed on the WBG Posit Connect QA environment (`datanalytics-int.worldbank.org`), running on host `rstudio-connect-qa-*`.
>
> Application URL: `>>> YOU — paste the app URL from your browser <<<`
> Content GUID: `9232cadb-b455-4a05-9af9-08648ce85d66`
> Content ID: `1702`
>
> This is the single endpoint in scope for testing — the application is a web interface with no separate API endpoints.

---

**Please list all APIs in scope for testing. If yes, upload Swagger/API collection files**

> N/A — this application does not expose any API. It is a Streamlit web interface with no external API surface. It consumes two external APIs (Zambia GeoHub ArcGIS REST API and the WBG mAI Factory via Azure APIM Gateway), both documented in the attached Solution Architecture document.

---

**Have DevSecOps security tools been enabled in your pipeline? Please provide the Azure Pipeline URL to review SAST and SCA reports**

**Answer: No**

> No. Deployment is git-backed from GitHub to WBG Posit Connect; there is no Azure Pipeline and no SAST/SCA scanning currently configured. Requesting guidance from OIS on whether an Azure Pipeline is mandatory for this application's size and risk profile, or whether an alternative scan approach is acceptable.

---

**Please provide the email IDs of project team members who will collaborate with C&A and require ADO access**
`>>> YOU <<<`

---

**Please provide the list of cloud resources in scope for this ACN, aligned with the Security Assessment (SA) report**

> WBG Posit Connect (application hosting); Azure APIM Gateway / COM Gateway (azapim.worldbank.org); Azure OpenAI (GPT model access); Amazon Bedrock (Claude model access); Azure AD (OAuth 2.0 token exchange, RFC 8693). Zambia GeoHub / ArcGIS Online (Esri) is accessed read-only over public HTTPS with no authentication and is externally operated — out of scope per the approved architecture.

---

**To expedite testing, please upload relevant artifacts**

> Upload: the architecture diagrams (Figure 1 deployment architecture + Figure 2 process flow), `ACN_Zambia_GeoHub_AI_Solution_Architecture.md`, and `ACN_Recommendations_Response.md`.

---

## Before you submit
- [ ] Previous approved case number
- [ ] Go-Live date
- [ ] Decide: Application Development complete — yes or no
- [ ] Check SA report version against current architecture before answering the deviations question
- [ ] Paste the application's QA URL (environment itself confirmed as QA)
- [ ] Team email IDs for ADO access
