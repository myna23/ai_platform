# Zambia Geospatial Intelligence Assistant — Response to OIS Post-Approval Recommendations

Following the approval of the LEAP/ACN request, this document responds to each of the seven recommendations in the review documentation.

---

**1. Enterprise identity-based authorization (Entra ID groups, least-privilege RBAC)**
**Status: Not implemented — justified by data classification, open to revisit**
The application's data classification is **Public only** — private and Internal Use Only datasets were removed from scope earlier in this review process (see prior architecture update). Every user who reaches the application sees the same public information regardless of identity, so there is no data to differentiate access to. Access to the application itself is already restricted to WBG's internal network. If the data classification changes in the future to include non-public data, we will implement Entra ID group-based RBAC at that point.

**2. Centralized logging, monitoring, and audit trails (SPLUNK)**
**Status: Pending confirmation from Posit Connect platform administrators**
This application is hosted on WBG-managed Posit Connect infrastructure. We are confirming with the Posit Connect platform team whether log forwarding to SPLUNK is already handled at the platform/hosting level for all content deployed there. We will report back with the outcome; if it is not already covered, we will scope an application-level logging integration.

**3. Enterprise secrets management / automated ArcGIS token rotation**
**Status: Not applicable — dependency removed**
This recommendation addressed manual rotation of an ArcGIS Bearer token used for private/restricted dataset access. That access path was removed from the application's scope earlier in this review (see Item 1) — the application now queries only public GeoHub datasets, which require no authentication token at all. There is no token to rotate.

**4. Dataset-level authorization and classification tagging for Internal Use Only datasets**
**Status: Not applicable — dependency removed**
Same basis as Item 3: the application's scope was narrowed to public datasets only. No Internal Use Only or private datasets are accessed, so there is no dataset-level access governance gap to close.

**5. Multi-stage deployment model (Dev / Test-UAT / Production) with CI/CD**
**Status: Accepted — phased implementation**
Immediate: we are adopting a git branch-based workflow — a `dev` branch for testing changes (validated locally and, where practical, against a separate staging deployment) before merging to `main`, which is the only branch that redeploys production. This enforces a manual promotion gate and keeps an auditable change history without requiring a full CI/CD platform.
Future: if usage or team size grows, we will evaluate a formal CI/CD pipeline with automated promotion gates and environment-specific secrets management.

**6. AI responses grounded in retrieved data only**
**Status: Already implemented**
The application's system prompt requires the AI to answer only from data retrieved from the Zambia GeoHub for the specific query — no fabricated statistics, coordinates, distances, or location attributes. When a query returns no matching records for a location, the application explicitly states that the data is unavailable rather than generating a synthesized answer (verified in production: e.g., a comparison query for a district with no matching records returns "no data available" rather than an estimate).

**7. Confidence scoring on AI-generated responses**
**Status: Implemented**
Threshold-based low-confidence detection is live and tested. The application flags a response as low-confidence — both as a visible warning banner in the UI and as an explicit instruction to the AI model — when any of the following occur: (a) the retrieved sample contains no records specifically matching the requested location, (b) the live GeoHub server was unavailable and the answer falls back to offline/static data, or (c) the matching record count falls below a defined threshold (fewer than 3 records) to support a general conclusion. In each case a user disclaimer is displayed and the AI is instructed to state the limitation explicitly rather than generalize from insufficient data.

This satisfies the recommendation as written: the recommendation specifies that low-confidence responses should trigger a *user disclaimer, alternative query suggestions, human-in-the-loop review, **or** response suppression* — the user disclaimer path is implemented, with confidence assessed against defined thresholds. The mechanism is deterministic and rule-based rather than model-derived, which is appropriate for this application: the confidence signals available (record match, data source freshness, sample size) are objective and directly measurable, making a trained scoring model unnecessary for this use case.

---

*Prepared by: [Your Name], [Your Role]*
*Date: [submission date]*
