# Zambia GeoHub AI Assistant — OIS Accreditation Intake Form
## Answers / Draft Reference

Use this as a copy-paste source for the OIS accreditation intake form before redeploying to Posit Connect. Fields marked `>>> FILL IN <<<` need your input — either a name/number only you know, or a WBG-internal picklist value I don't have visibility into.

---

**OIS Accreditation Number (ACN)**
_(leave blank — "Pending accreditation is acceptable")_

**Application Name**
Zambia Geospatial Intelligence Assistant (ZGIA)

_(renamed from "Zambia GeoHub AI Assistant" — the original doubled as the project name and named the app after "GeoHub," the underlying Esri/ArcGIS product it queries, both of which LEAP's naming guidelines advise against. This name is function/capability-driven instead.)_

**Description of the Application**
Supports the following functions:
- Natural-language querying of Zambia's public geospatial datasets (schools, health facilities, roads, settlements, etc.)
- AI-generated analysis and narrative answers to geographic/development questions, using WBG-approved models (GPT-5 / Claude Sonnet)
- Interactive map and data table visualization of query results
- Generation of downloadable analytical reports (Word .docx and PDF)

_(rewritten from a project-overview style paragraph to a functions list, per LEAP naming/description guidance: "the application description should list the functions supported" and "should not be the project description")_

**Status of the Application**
`>>> FILL IN <<<` — New / Pilot / Production?

**Business Solution Center / Line of Business**
`>>> FILL IN <<<` — likely "Zambia GSURR / Development Data Group"; confirm exact picklist match

**IT Sub-Unit**
_(optional — skip unless you know your specific sub-unit code)_

**Supported Organizations**
`>>> FILL IN <<<` — single org (World Bank / IBRD-IDA); do NOT select "WBG" (that's for multi-org apps per the form's own guidance)

**Business Owner/Sponsor**
`>>> FILL IN <<<`

**IT Owner**
`>>> FILL IN <<<`

**Portfolio Manager**
`>>> FILL IN <<<`

**Data Security Classification**
Public

**Data Privacy Risk Tier**
`>>> FILL IN <<<` — lowest available tier (no PII collected, stored, or transmitted)

**Access Method**
Web Browser (HTTPS)

**Primary URL**
`>>> FILL IN <<<` — your Posit Connect published URL

**Time Criticality**
Low

**ICFR Scope**
Out of scope / No

**Critical Info Asset**
No

**Application Development Category**
`>>> FILL IN <<<` — likely "Custom Developed" / "In-house"

**Application Network Zone**
`>>> FILL IN <<<` — check with Posit admin/IT owner how Posit Connect is zoned

**Nature of Hosting**
WBG-managed Cloud / SaaS (WBG Posit Connect)

**Number of Users**
`>>> FILL IN <<<`

**User Base**
`>>> FILL IN <<<` — likely "Internal + External" (WBG staff + government/development practitioners)

**Mobile Support**
No Mobile Support

**AI Enabled**
Yes

**AI Use Case**
The application uses WBG-approved large language models (GPT-5 via Azure OpenAI, Claude Sonnet via Amazon Bedrock — both accessed through the WBG mAI Factory gateway) for three functions:
1. **Query understanding** — classifies each user's natural-language question to determine intent (chatbot Q&A, report generation, or dataset summary) and extracts the geographic area and topic being asked about.
2. **Data analysis and narrative generation** — takes the retrieved Zambia GeoHub dataset records (public data only) plus the user's question and generates a plain-language analytical answer, grounded strictly in the retrieved records (system prompt enforces no hallucination, source citation, and Zambia-only scope).
3. **Report drafting** — assembles the AI-generated analysis into structured Word/PDF reports for download.
No model training or fine-tuning occurs; the application only calls pre-trained WBG-approved models via API for inference. No user data or query history is used to train or fine-tune any model.

**Business Capability Mapping**
`>>> FILL IN <<<` — see WBG Business Capability Model

**Business Domain**
`>>> FILL IN <<<`

**Business Sub-Domain**
`>>> FILL IN <<<`

**Business Capability the Application Supports**
Geospatial data discovery, analysis, and AI-assisted reporting for development planning

**Business Product Mapping**
`>>> FILL IN <<<` — see AIP Domains and Product Lines

**AIP Domain**
`>>> FILL IN <<<`

**Business Product Line**
`>>> FILL IN <<<`

**Business Product / Service**
`>>> FILL IN <<<`

**Technologies Supporting the Application**
Python, Streamlit, WBG Posit Connect, ArcGIS REST API (Esri), WBG mAI Factory (Azure OpenAI GPT-5 / Amazon Bedrock Claude Sonnet)

**Authentication Platform**
`>>> FILL IN <<<` — app currently has no user login (open to anyone with the Posit Connect URL); flag to IT owner, OIS may require this to change

**Two Factor Authentication**
No

**Supporting Enterprise Platforms**
WBG Posit Connect, WBG mAI Factory (azapimdev.worldbank.org)

**Does this application have interfaces with other applications?**
Yes — both integrations below are WBG-operated systems (not third-party public APIs), so they count as interfaces with other WBG applications rather than external services.

**Inbound Interfaces**
Zambia GeoHub (zmb-geowb.hub.arcgis.com) — the application queries the GeoHub ArcGIS FeatureServer REST API and Hub Search API, and receives public geospatial dataset records (GeoJSON) and dataset metadata in response.

**Outbound Interfaces**
WBG mAI Factory (azapimdev.worldbank.org) — the application sends the user's question plus a sampled excerpt of retrieved dataset records (no PII) to the mAI Factory API for AI inference, and receives the generated analysis text back over the same channel.

**Additional Comments**
Application scope was recently narrowed to public-only GeoHub datasets (no private/token-gated data) and no third-party public APIs (Open-Elevation, OSRM removed), in response to OIS security review feedback. See attached architecture diagrams and solution concept document.

---

## Follow-up: Application Functionality Description (OIS request, 2026-08-05)

The **Zambia Geospatial Intelligence Assistant** is a conversational AI tool that lets World Bank staff, government officials, and development practitioners explore Zambia's national geospatial data using plain-English questions instead of GIS software or manual dataset searches.

**How it works, end to end:**
1. A user types a question in the chat interface (e.g. "How many health facilities are in Eastern Province?" or "Compare Lusaka and Kitwe in terms of schools").
2. The app classifies what the user wants — a direct answer, a two-area comparison, a dataset summary, or a downloadable report — and extracts the location and topic from the question.
3. It queries the relevant dataset(s) live from the Zambia GeoHub (a public World Bank-operated ArcGIS Online platform covering ~80 datasets: schools, health facilities, roads, settlements, flood risk, and more), filtered to the requested area.
4. The retrieved records are sent, along with the user's question, to a WBG-approved AI model (GPT-5 or Claude Sonnet, via the WBG mAI Factory → COM Gateway) to generate a grounded, plain-language answer — the AI is instructed not to state anything not supported by the retrieved data.
5. Results are displayed as text, an interactive map, and a data table, with an option to export the answer as a Word or PDF report.

**Core capabilities:**
- Natural-language Q&A over Zambia's public geospatial datasets
- Side-by-side comparison of two areas (e.g. two districts) on a given topic
- Dataset summarization in plain language
- Interactive map visualization of query results
- Downloadable Word/PDF reports of AI-generated analysis

**Scope and data handling:** Only public, non-PII geospatial data is used (no private/token-gated datasets, per the narrowed scope agreed with OIS). The application is fully stateless — no user data, queries, or AI responses are stored server-side.

---

## Follow-up: Detailed Technology Stack (OIS request, received after initial submission)

**Frontend technologies**
Streamlit (Python) — a server-rendered Python web framework, not a JS SPA framework. No Angular or React. Maps rendered via Folium/streamlit-folium (Leaflet.js under the hood) and Plotly for charts.

**Backend technologies**
Python 3.11, running entirely as a Streamlit application. No .NET or Java. Backend logic is organized into Python modules: `app.py` (main app + UI), `hub/client.py` (Zambia GeoHub integration), `ai/model_client.py` (AI provider routing/auth), `reports/builder.py` (Word/PDF generation), `utils/geo_utils.py` (geospatial helpers).

**Databases**
None. The application is fully stateless — no SQL Server, PostgreSQL, or any other database. Geospatial data is retrieved live from the Zambia GeoHub ArcGIS FeatureServer REST API at query time, with pre-bundled static GeoJSON files as an offline fallback if the live API is unavailable. No data is persisted server-side.

**Cloud services**
- WBG Posit Connect — WBG-managed application hosting (confirmed Kubernetes-based from deployment logs; Ubuntu 24.04 LTS runtime)
- Azure OpenAI (GPT-5) — AI inference, accessed via WBG mAI Factory → COM Gateway
- Amazon Bedrock (Claude Sonnet) — AI inference, accessed via WBG mAI Factory → COM Gateway
- Azure AD — OAuth 2.0 token exchange (RFC 8693) for mAI Factory/COM Gateway authentication, via the `azure-identity` Python library and Posit Connect's built-in OAuth integration

### Hosting and Infrastructure

**Cloud provider**
WBG-managed — hosted entirely on WBG's Posit Connect platform (Kubernetes-based). `>>> FILL IN <<<` — the underlying IaaS provider beneath Posit Connect (Azure vs. AWS) is managed by WBG's ITS infrastructure team, not chosen by this application; confirm with your Posit Connect/ITS admin if OIS wants that named explicitly.

**Specific services used**
- Azure OpenAI (AI inference — GPT-5)
- Amazon Bedrock (AI inference — Claude Sonnet)
- Azure AD (OAuth authentication for AI Factory/COM Gateway access)
- GitHub (source control and git-backed deployment to Posit Connect — not Azure DevOps)
- **Not used:** Azure Blob Storage (reports are generated in-memory and streamed directly to the browser, never written to disk or blob storage), Azure Key Vault (secrets are handled via Posit Connect environment variables and OAuth session tokens, not Key Vault), Azure DevOps (deployment is git-backed via GitHub, not an Azure DevOps pipeline) — confirmed by full codebase search, no references to any of these exist in the application.

---

## Still needed before submission
- [ ] Status of the Application
- [ ] Business Solution Center / Line of Business (confirm picklist match)
- [ ] Supported Organizations (confirm picklist match)
- [ ] Business Owner/Sponsor
- [ ] IT Owner
- [ ] Portfolio Manager
- [ ] Data Privacy Risk Tier (confirm picklist match)
- [ ] Primary URL
- [ ] Application Development Category (confirm picklist match)
- [ ] Application Network Zone
- [ ] Number of Users
- [ ] User Base (confirm picklist match)
- [ ] Business Capability Mapping / Domain / Sub-Domain
- [ ] Business Product Mapping / AIP Domain / Product Line / Product / Service
- [ ] Authentication Platform
