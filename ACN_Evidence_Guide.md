# Evidence Pack — what to attach, per story
### ACN-2026-31023 | Round 2, responding to OIS PT Review

Reviewers accepted the written answers but asked for evidence rather than statements. This is the evidence, and where each piece goes.

---

## DO THIS FIRST — one action unblocks five stories

**Attach the regenerated `ACN_Zambia_GeoHub_AI.docx` to 186174, 186182, 186188, 186209, 186210.**

The SA document OIS has been reading is the June version. It still states the app processes *"WBG Internal Use Only (private GeoHub datasets accessible via ArcGIS token)"*, that the token is *"passed as a `?token=` query param"* with *"14-day expiry… rotated via get_token.py"*, and lists Open-Elevation and OSRM as active integrations.

That single file is the source of every *"the SA document still says…"* objection. It has been regenerated and verified clean.

---

## POST THIS CORRECTION on 186208, 186209, 186210

Open-Elevation and OSRM had been removed from the documentation in July but **remained live in the application code** until this week. Remediation also found further undisclosed outbound calls. All are now removed — but the earlier comment claiming they were already gone needs correcting.

> Correction to our earlier comment: Open-Elevation and OSRM had been removed from the architecture documentation but remained in the application code until this update. During remediation we identified additional undisclosed outbound calls — OpenStreetMap Overpass mirrors (including a Russian-hosted mirror), an alternative routing service, and a third-party basemap tile provider. All have now been removed. The application's outbound connections are limited to Zambia GeoHub (ArcGIS), the WBG mAI Factory gateway, and Posit Connect. Evidence attached.

---
---

# THE EVIDENCE PACK — `QA_Evidence/`

Nine files, generated from the live QA build. Attach the `.txt` directly, or screenshot its contents.

| File | Proves | Goes to |
|---|---|---|
| `186180_secret_scan.txt` | detect-secrets scan, 0 findings requiring action | 186180 |
| `186182_186188_186211_no_arcgis_token.txt` | No ArcGIS token anywhere; no credential in any URL | 186182, 186188, 186211 |
| `186188_dataset_inventory.txt` | All 62 catalogue datasets classified PUBLIC | 186188 |
| `186188_sample_api_call.txt` | Live unauthenticated retrieval + restricted layer refused | 186188 |
| `186202_186208_186209_186210_approved_endpoints.txt` | Complete outbound host list; external services absent | 186202, 186208, 186209, 186210 |
| `186203_ai_request_payload.txt` | Real AI payload — question + metadata + 15 records + totals | 186203 |
| `186203_data_minimisation.txt` | The 200/15 record caps, in code | 186191, 186194, 186203 |
| `186209_certificate_validation.txt` | No `verify=False` anywhere; trust store in use | 186209 |
| `186213_change_history.txt` | Commit history with author, date, description | 186213 |

Regenerate any time: `bash QA_Evidence/00_generate.sh`

**Two of these are worth highlighting to the reviewer:**

- **`186188_sample_api_call.txt`** contains a live control test: a token-required ArcGIS layer was requested without a credential and returned **`error 499: Token Required`**. That demonstrates the app *cannot* reach non-public data, rather than asserting it.
- **`186203_ai_request_payload.txt`** is a real payload built by the application's own prompt code — 148 records retrieved, exactly 15 transmitted, no credential or personal data present.

---
---

# SCREENSHOTS — 10 to capture

### Posit Connect

| # | Where | Must show | Goes to |
|---|---|---|---|
| **A** | Settings → **Vars** | Only `WB_POSIT`. No `ARCGIS_TOKEN` | 186180, 186182, 186184, 186188, 186211 |
| **B** | Settings → **Access** | Access mode + viewer/collaborator list + owner | 186168, 186170, 186174, 186184, 186196 |
| **C** | Settings → Access → **Integrations** | mAI Factory OAuth integration attached | 186202, 186206 |
| **D** | Settings → **Advanced / Runtime** | Runs as hosted content, no custom ports | 186210 |
| **E** | **Bundles / History** | Deployment entries with timestamps | 186213 |
| **F** | **Logs** | A full session: startup, query, AI call, no tokens or prompts | 186192, 186205, 186212, 186214, 186216, 186218 |

### The application

| # | Do this | Must show | Goes to |
|---|---|---|---|
| **G** | Ask *"How many mines are in Rufunsa?"* | ⚠️ low-confidence banner + AI stating no records exist | **186204** |
| **H** | Ask *"How many schools are in Lusaka?"* | Answer + source dataset citation + live/offline indicator | 186203, 186204 |
| **I** | Open any answer with downloads | Word/PDF export buttons visible to a signed-in user | 186196 |
| **J** | App landing page | Function set — chat, map, table, download. No admin screens | 186170, 186174 |

### Browser

| # | Do this | Must show | Goes to |
|---|---|---|---|
| **K** | DevTools → Network, run a query | No token in any request URL | 186211 |

**Screenshot G is the single highest-value capture** — 186204 is the one control that a single image closes, and the reviewer asked for it by name.

---
---

# PER-STORY CHECKLIST

| Story | Attach |
|---|---|
| 186168 | **B** |
| 186170 | **B** + **J** |
| 186174 | SA doc + **B** + **J** |
| 186178 | ✅ **CLOSED** |
| 186180 | `186180_secret_scan.txt` + **A** |
| 186182 | SA doc + `186182_..._no_arcgis_token.txt` + **A** |
| 186184 | **A** + **B** |
| 186188 | SA doc + `186188_dataset_inventory.txt` + `186188_sample_api_call.txt` + `186182_..._no_arcgis_token.txt` + **A** |
| 186189 | — decision required, see below |
| 186191 | `186203_data_minimisation.txt` |
| 186192 | `186203_data_minimisation.txt` + **F** |
| 186194 | `186203_data_minimisation.txt` |
| 186196 | **B** + **I** |
| 186198 | — remediation ready to implement, see below |
| 186199 | ✅ fixed — attach **F** |
| 186202 | Correction + `186202_..._approved_endpoints.txt` + **C** |
| 186203 | `186203_ai_request_payload.txt` + `186203_data_minimisation.txt` + **H** |
| 186204 | **G** + **H** |
| 186205 | **F** + ITSO retention terms |
| 186206 | `186202_..._approved_endpoints.txt` + **C** + ITSO onboarding records |
| 186208 | Correction + `186202_..._approved_endpoints.txt` |
| 186209 | Correction + SA doc + `186209_certificate_validation.txt` |
| 186210 | Correction + SA doc + `186202_..._approved_endpoints.txt` + **D** |
| 186211 | `186182_..._no_arcgis_token.txt` + **A** + **F** + **K** |
| 186212 | **F** + scope proposal, see below |
| 186213 | `186213_change_history.txt` + **E** |
| 186214 | **F** |
| 186216 | ✅ fixed — attach **F** |
| 186217 | — scope agreement needed, see below |
| 186218 | **F** + Posit admin confirmation |

---
---

# FIXED THIS ROUND — no longer blocking

**186199 + 186216 — error disclosure.** The application no longer shows technical error text to users; it returns a generic message. Logged errors record the exception type and message but never a service response body. Both OAuth failure paths that previously included response content have been corrected. Capture Screenshot **F** now — the logs are clean.

**186180 — secret scanning.** Scan run with detect-secrets 1.5.0 across all tracked files. 143 entropy flags, every one reviewed: 92 public ArcGIS dataset IDs, 51 MD5 checksums, **zero requiring action**. The scan also surfaced stale credential references — none were live secrets, all were templates or documentation — and all were corrected: `.env.example` rewritten and removed from the deployment, two token-management scripts deleted, an unused ArcGIS username/password code path removed from the bundle, and four documentation files fixed that had documented `OPENAI_API_KEY`, `ARCGIS_TOKEN`, and token-in-URL examples.

**186188 — dataset classification.** Inventory of all 62 catalogue datasets, all PUBLIC, plus a live API call proving unauthenticated retrieval works and a control test proving a restricted layer is refused.

**186203 — AI payload.** Real payload generated from the application's own prompt code.

---

# STILL OPEN — and who owns each

### 186189 — uploaded documents are not inspected — **your decision**
Users can attach a document whose text is sent to the AI. Nothing scans it, so a user could introduce personal data. Three options: remove the upload feature, add a user-facing warning prohibiting personal data, or ask OIS to accept it as a documented user-responsibility control. **Tell me which and I'll implement it.**

### 186198 — input validation — **ready to implement**
The fix is to validate the extracted place name against a fixed list of known Zambian districts and provinces, so only a name from a closed set can reach a query. The district list already exists in the application. **Say go and I'll do it**, then this becomes evidence rather than a plan.

### 186212 + 186217 — monitoring — **needs OIS scope first**
Nothing exists to screenshot. Rather than build something that misses the mark, ask OIS what minimum is acceptable for an application of this profile — Low time-criticality, stateless, public-data-only, nothing stored. Then build to that.

### 186205 + 186206 — **WBG ITSO / mAI team**
mAI Factory retention terms, and platform onboarding / model authorisation records. Not producible by this project.

### 186218 — **Posit Connect admin**
Does platform log forwarding to Splunk already cover this content item? One answer closes or scopes the story.

**The last two have the longest lead time — chase them today.**

---

*Reference: ACN-2026-31023*
