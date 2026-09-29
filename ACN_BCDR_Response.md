# Zambia Geospatial Intelligence Assistant (ZGIA)
## Business Continuity & Disaster Recovery Statement

Prepared for the BC-DR no-objection review under ACN-2026-31023.

---

## 1. Summary

The application is a **stateless, read-only analytical tool**. It stores no data, holds no system of record, and supports no transactional business process. Consequently its continuity profile is materially simpler than a typical business application: there is no application data that can be lost, and recovery consists of redeploying code that is already version-controlled off-platform.

Business criticality is **Low** (consistent with the Time Criticality classification submitted in the accreditation intake). An outage delays analytical queries; it does not interrupt any operational, financial, or service-delivery process.

---

## 2. Recovery Objectives

| Objective | Target | Basis |
|---|---|---|
| **RPO** (Recovery Point Objective) | **Not applicable — no data at risk** | The application persists nothing server-side. No user queries, AI responses, geospatial records, or generated documents are written to disk. There is no application database, file store, or cache to restore. |
| **RTO** (Recovery Time Objective) | **4 hours** for application-level recovery | Recovery is a redeployment from the GitHub source repository to WBG Posit Connect — a git-backed pull requiring no data restoration or reconfiguration. Achievable well inside this target; 4 hours allows margin for staff availability rather than technical constraint. |
| **Platform dependency** | Inherited from WBG Posit Connect | Where the outage is at the hosting-platform level, restoration timing is governed by the WBG Posit Connect platform team's own continuity commitments, outside this project's control. |

---

## 3. Failure Modes and Response

| Scenario | Impact | Mitigation / Response | Service state |
|---|---|---|---|
| **Zambia GeoHub (ArcGIS Online) unavailable** | Live geospatial queries fail | Application automatically falls back to pre-bundled offline GeoJSON datasets shipped with the deployment. Users are shown an explicit disclaimer that the answer is drawn from offline data and may not reflect current records. | **Degraded — functional.** Verified in testing. |
| **WBG mAI Factory / COM Gateway unavailable** | AI-generated analysis unavailable | Error is caught and surfaced to the user with a clear message. Non-AI functionality — district/province overview counts, interactive maps, data tables — continues to operate, as these query the GeoHub directly without model inference. | **Partially degraded.** |
| **Faulty release deployed** | Application error or regression | Two independent rollback paths: (a) reactivate the previous bundle retained in Posit Connect's bundle history; (b) revert the commit in Git and redeploy. Changes reach production only via merge to the `main` branch, providing a deliberate promotion gate. | **Recoverable in minutes.** |
| **WBG Posit Connect platform outage** | Full application outage | No project-level mitigation available; recovery follows the hosting platform's continuity process. Application can be redeployed to an alternative Posit Connect instance from source if required. | **Full outage — platform-dependent.** |
| **Source code loss on a developer machine** | None to running service | Source of record is the GitHub repository with full commit history. The running deployment is unaffected. | **No service impact.** |

---

## 4. Backup and Restoration

- **Application data:** none exists. No backup required or possible.
- **Source code:** maintained in GitHub with full version history; every deployed state is identifiable by commit.
- **Deployed artefacts:** Posit Connect retains prior deployment bundles, each independently reactivatable without rebuilding from source.
- **Configuration and secrets:** environment configuration is held in Posit Connect at the content level, not in source control. Credentials are not stored at all — authentication to AI services uses a per-session OAuth 2.0 token exchange (RFC 8693), so there are no long-lived secrets requiring backup, rotation, or recovery.
- **Reference datasets:** the offline fallback GeoJSON files are versioned in the source repository and deploy with the application.

---

## 5. Dependencies

| Dependency | Owner | Continuity implication |
|---|---|---|
| WBG Posit Connect | WBG (ITS) | Hosting platform. Availability and recovery inherited. |
| WBG mAI Factory / Azure APIM Gateway | WBG (ITSO / mAI team) | Required for AI responses only. Application degrades partially without it. |
| Zambia GeoHub (ArcGIS Online) | World Bank / Esri | Required for live data. Offline fallback mitigates. |

No dependency is single-point-of-failure for total data loss, as the application holds no data of its own.

---

## 6. Open Items

- Formal continuity testing (simulated platform outage and timed recovery drill) has not been performed. Given the stateless architecture and low criticality classification, we propose this be scoped proportionately — a documented redeployment-from-source exercise rather than a full DR invocation — and are open to BC-DR guidance on whether that is sufficient.
- RTO above is a proposed target based on technical recovery time; it has not been formally agreed with a business owner. Confirmation from the Business Owner/Sponsor is required.

---

*Prepared by: [Your Name], [Your Role]*
*Date: [submission date]*
*Reference: ACN-2026-31023*
