# Zambia GeoHub AI Assistant
## Solution Concept — Architecture Change Notification (ACN) Submission
### Version 1.0 | June 2026

---

## Table of Contents
1. Introduction
2. Intended Audience & Acronyms
3. Project Overview
4. Solution Concept — Architecture
5. Authorization Model & Matrices
6. Security Risk Considerations
7. Reference

---

## 1.0 Introduction

### 1.1 Purpose of this Document

The purpose of this accreditation request is to obtain OIS review and approval for the **Zambia GeoHub AI Assistant** — a Python-based geospatial intelligence web application that combines Zambia's national open data platform (Zambia GeoHub, hosted on ArcGIS Online) with WBG-approved AI models to support development planning, infrastructure analysis, and policy decision-making. The application is intended for deployment on the **WBG Posit Connect** platform, using the WBG mAI Factory for AI inference.

---

## 2.0 Intended Audience

This document is intended for the following audience:
- OIS (World Bank Office of Information Security)
- Enterprise & Solution Architects
- Project Team (Zambia GSURR / Development Data Group)

### 2.1 Acronyms

| Acronym | Definition |
|---|---|
| WB | World Bank |
| WBG | World Bank Group |
| OIS | World Bank Office of Information Security |
| ACN | Architecture Change Notification |
| GeoHub | Zambia National Geospatial Data Hub (zmb-geowb.hub.arcgis.com) |
| mAI Factory | WBG AI platform (azapimdev.worldbank.org) |
| GRID3 | Geo-Referenced Infrastructure and Demographic Data for Development |
| RLS | Row-Level Security |
| SPA | Single-Page Application |

---

## 3.0 Project Overview

The **Zambia GeoHub AI Assistant** is a conversational geospatial intelligence tool that allows World Bank staff, government officials, and development practitioners to explore Zambia's national geospatial datasets using natural language queries. The system retrieves live data from the Zambia GeoHub (a publicly accessible ArcGIS Online platform), processes it, and returns AI-analyzed answers with interactive maps and data tables.

**In-scope:**
- Streamlit-based Python web application hosted on WBG Posit Connect
- Integration with Zambia GeoHub (zmb-geowb.hub.arcgis.com) via ArcGIS REST API — public datasets only
- Integration with WBG mAI Factory (via Posit Connect OAuth token exchange) for AI inference (GPT-5 / Claude Sonnet)
- Offline static fallback datasets (pre-saved public GeoJSON files bundled with the application)

**Out of scope:**
- The Zambia GeoHub platform itself (separately operated by World Bank; not modified by this project)
- WBG mAI Factory infrastructure (operated by ITSO/mAI team; accessed via approved API)
- ArcGIS Online infrastructure (operated by Esri)
- Any user authentication / login system (the app is currently open to all users with the Posit Connect URL; no user accounts or PII are stored)

**Data Classification:** The application processes only **Public** (open zmb-tagged GeoHub datasets). No Confidential, Restricted, or Internal Use Only data is processed. No Personally Identifiable Information (PII) is collected, stored, or transmitted.

---

## 4.0 Solution Concept

### 4.1 Solution Architecture

The overall solution is a **stateless Python web application** deployed on WBG Posit Connect. It queries external APIs at runtime and returns results directly to the user's browser — no data is persisted on the server.

**Figure 1: High-Level Deployment Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                        User's Browser                           │
│              (HTTPS — WBG-managed Posit Connect URL)            │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTPS
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              WBG Posit Connect (Hosted on WBG Cloud)            │
│                                                                 │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │       Zambia GeoHub AI App (app.py — Python/Streamlit)   │  │
│   │                                                          │  │
│   │  ┌─────────────┐  ┌──────────────┐                       │  │
│   │  │ hub/client  │  │ ai/model_    │                       │  │
│   │  │ .py         │  │ client.py    │                       │  │
│   │  │ (ArcGIS     │  │ (mAI Factory │                       │  │
│   │  │  REST API)  │  │  OAuth)      │                       │  │
│   │  └──────┬──────┘  └──────┬───────┘                       │  │
│   └─────────┼────────────────┼─────────────────────────────── ┘  │
└─────────────┼────────────────┼───────────────────────────────────┘
              │ HTTPS           │ HTTPS
              ▼                 ▼
┌──────────────────┐   ┌────────────────────────────────────────┐
│  Zambia GeoHub   │   │  WBG mAI Factory                       │
│  (ArcGIS Online) │   │  azapimdev.worldbank.org               │
│  FeatureServer   │   │  GPT-5 / Claude Sonnet via Bedrock     │
│  REST API        │   │  Auth: Posit Connect OAuth             │
└──────────────────┘   └────────────────────────────────────────┘
```

**Figure 2: Data Flow — Question-to-Answer Process**

```
User types: "How many schools are in Chongwe District?"
                         │
                         ▼
          ┌──────────────────────────────────────┐
          │  1. Intent Detection                  │
          │     detect_intent(question)           │
          │     → "chat" / "report" / "summary"  │
          └──────────────┬───────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────────────┐
          │  2. Location & Topic Extraction       │
          │     → location = "Chongwe"           │
          │     → topic = "schools"              │
          └──────────────┬───────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────────────┐
          │  3. Dataset Search (Catalog Ranking) │
          │     hub.search_datasets(q)           │
          │     → GRID3 Schools dataset selected │
          └──────────────┬───────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────────────┐
          │  4. Live Data Fetch                  │
          │     ArcGIS FeatureServer REST API    │
          │     WHERE District='Chongwe'         │
          │     → GeoJSON response (≤200 records)│
          │     (Falls back to static JSON if    │
          │      server unavailable)             │
          └──────────────┬───────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────────────┐
          │  5. AI Prompt Construction           │
          │     Question + dataset info +        │
          │     sampled records (≤15) +          │
          │     pre-aggregated counts +          │
          │     system rules (no hallucination)  │
          └──────────────┬───────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────────────┐
          │  6. WBG mAI Factory API Call         │
          │     POST azapimdev.worldbank.org/... │
          │     Auth: Bearer (OAuth token)       │
          │     → streaming text response        │
          └──────────────┬───────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────────────┐
          │  7. Display to User                  │
          │     → Markdown answer text           │
          │     → Interactive pydeck map         │
          │     → Data table (st.dataframe)      │
          └──────────────────────────────────────┘
```

### Process Flow Detail

**1. User Interface (Streamlit Web App)**
The application is a Python Streamlit app served via WBG Posit Connect. Users access it through a standard HTTPS browser connection. The interface provides a conversational chat, interactive maps (pydeck/folium), data tables, and file download buttons. No plugins, browser extensions, or local installations are required.

**2. AI Intent Detection & Dataset Search**
User questions are analyzed server-side to detect intent (chatbot Q&A or dataset summarization) and to extract geographic and thematic keywords. These keywords are scored against a curated catalog of ~80 Zambia GeoHub datasets to select the most relevant source.

**3. Live Geospatial Data Retrieval (ArcGIS REST API)**
The app queries the Zambia GeoHub's ArcGIS FeatureServer API over HTTPS to fetch feature records (e.g., school locations with district and name fields). Only public datasets are accessed — no authentication token is used. Requests include:
- District or province filter (SQL WHERE clause passed as a URL parameter)
- Maximum of 200 records per request
- GeoJSON response format

Fallback: If the live API is unavailable, the app reads pre-bundled static GeoJSON files (stored locally within the deployed application).

**4. AI Inference (WBG mAI Factory)**
The user question and dataset records (≤15 sampled features + pre-aggregated counts) are sent to the WBG mAI Factory. On Posit Connect, authentication uses the **Posit Connect OAuth 2.0 token exchange** flow (RFC 8693):
- Posit Connect auto-injects `CONNECT_CONTENT_SESSION_TOKEN` per viewer session
- The app exchanges this for an Azure AD Bearer token via `POST CONNECT_SERVER/__api__/v1/oauth/integrations/credentials`
- The Bearer token is passed to `azapimdev.worldbank.org` for AI inference
- No AI API keys are stored in the application; all auth is handled via Posit Connect OAuth

### Technology Stack Summary

| No. | Component | Description | Security Control / Authentication |
|---|---|---|---|
| 1 | Streamlit Web App (app.py) | Python web application — UI, intent detection, map rendering | Served via Posit Connect (WBG-managed); HTTPS enforced by Posit |
| 2 | WBG Posit Connect | Application hosting platform | WBG-managed; user access controlled via Posit Connect URL sharing or SSO |
| 3 | WBG mAI Factory (GPT-5 / Claude) | AI inference for natural language analysis | Posit Connect OAuth 2.0 token exchange (RFC 8693); DesktopToken on WB machines |
| 4 | Zambia GeoHub (ArcGIS Online) | Source of Zambia geospatial datasets (public only) | Public datasets: no authentication |
| 5 | Offline Static Datasets | Pre-bundled GeoJSON fallback files (health, schools, settlements, etc.) | Bundled within Posit Connect deployment; read-only static files |

---

## 5.0 Authorization Model — Roles & Permissions Matrix

### Application Roles / Groups

| Role | Security Group | Description | Permissions |
|---|---|---|---|
| System Administrator | Admin (Posit Connect owner) | Manages app deployment and environment variables | Write (deploy, configure) |
| Application User | All users with Posit Connect URL | Queries GeoHub datasets, views AI answers, downloads reports | Read-only (query, view, download) |

> **Note:** The application currently has no user login system. Access is controlled by possession of the Posit Connect URL. If restricted access is required, Posit Connect's built-in access control (SSO / user list) can be applied at the platform level without any application code changes.

### API Authorization Matrix

| API Endpoint | Action | Permission | Description |
|---|---|---|---|
| ArcGIS FeatureServer `/query` | GET | Read | Fetches GeoJSON feature records from Zambia GeoHub datasets |
| ArcGIS Hub `/api/v3/search` | GET | Read | Searches the GeoHub catalog for datasets matching a keyword query |
| `azapimdev.worldbank.org/conversationalai/v2/` (GPT) | POST | Read (consume) | Sends prompt + data to WBG mAI Factory for AI inference |
| `azapimdev.worldbank.org/conversationalai/bedrock/model/` (Claude) | POST | Read (consume) | Sends prompt + data to WBG Bedrock Claude endpoint |
| `CONNECT_SERVER/__api__/v1/oauth/integrations/credentials` | POST | Read | Posit Connect token exchange — gets Azure AD Bearer token for mAI Factory |

### Cloud Authorization Matrix (Posit Connect Deployment)

| Identity Type | Resource Accessed | Permission | Description |
|---|---|---|---|
| Posit Connect Content Service (CONNECT_API_KEY) | Posit Connect OAuth endpoint | Read | Used by the app to initiate OAuth token exchange for mAI Factory access |
| Posit Connect Session Token (CONNECT_CONTENT_SESSION_TOKEN) | Posit Connect OAuth endpoint | Read | Per-viewer session token auto-injected by Posit Connect; identifies the calling user |
| Azure AD Bearer Token (obtained via OAuth exchange) | WBG mAI Factory API (azapimdev.worldbank.org) | Write (invoke AI) | Short-lived token used to call GPT-5 / Claude models; scoped to the mAI Factory integration |

### Integration Table

| Source System | Target System | Integration Purpose | Authentication / Authorization Method | Scopes / Permissions |
|---|---|---|---|---|
| Streamlit App (Posit Connect) | WBG mAI Factory (azapimdev.worldbank.org) | AI natural language inference — send question + dataset excerpt, receive analysis | Posit Connect OAuth 2.0 token exchange (RFC 8693); DesktopToken on WB machines | mAI Factory integration GUID: `20c434c5-78f1-431f-a286-76980748bc93`; Read (invoke AI completions) |
| Streamlit App (Posit Connect) | Zambia GeoHub ArcGIS FeatureServer | Retrieve live geospatial feature records (schools, health, roads, etc.) | Public datasets only: no authentication | Read-only: `outFields=*&resultRecordCount=200&f=geojson` |
| Streamlit App (Posit Connect) | ArcGIS Hub Search API (`/api/v3/search`) | Discover available datasets in the GeoHub catalog | No authentication (public search endpoint) | Read-only: dataset metadata only (title, URL, description) |

### MS Graph Authorization

This application does **not** use Microsoft Graph APIs or Azure AD user profile lookups. The Posit Connect OAuth integration is scoped only to the mAI Factory integration GUID and does not request any Microsoft Graph permissions.

### WBG SaaS Authorization (Posit Connect)

| Role | Platform Component | Permission | Description |
|---|---|---|---|
| System Administrator | Posit Connect — App Deployment & Env Vars | Write | Deploys app, sets environment variables (WB_POSIT), manages OAuth integration config |
| Application User | Posit Connect — Published App | Read-only | Accesses the published Streamlit app via browser; cannot modify app code or environment |

---

## 6.0 Security Risk Considerations

### 6.1 Data Sensitivity
- All geospatial data retrieved is from the **Zambia GeoHub**, a publicly accessible government open data platform. All datasets accessed (health facilities, schools, settlements, roads) are tagged `zmb` and are publicly accessible with no authentication.
- **No PII is processed.** The app does not collect user identities, does not store chat history server-side, and does not transmit any personal data to external APIs. The AI prompts contain only the user's geographic question and anonymized dataset records (place names, counts, coordinates).

### 6.2 API Key / Secret Management
- **mAI Factory Access**: Handled entirely via Posit Connect OAuth — no API keys stored in the app. The `CONNECT_CONTENT_SESSION_TOKEN` is auto-injected per session by Posit Connect and never persisted.
- **No direct OpenAI/Anthropic keys in production**: The WB Posit provider routes all AI calls through the WBG mAI Factory gateway, not directly to external AI providers.

### 6.3 Statelessness / No Persistent Storage
The application is fully stateless. No user queries, AI responses, or geospatial data are written to disk on the server.

### 6.4 Transport Security
All API calls (ArcGIS, mAI Factory, Posit OAuth) are made over HTTPS. The `truststore` library is used to inject system certificate trust on WBG corporate machines where custom certificate authorities are used.

---

## 7.0 Reference

### 7.1 Previous Accreditations
No previous ACN for this project. This is the initial accreditation request.

### 7.2 Supporting Documentation
- Zambia GeoHub AI System Architecture Document (`Zambia_GeoHub_AI_System_Explained.md`)
- WBG mAI Factory API Documentation: https://ai.worldbank.org/platform/documentation
- Posit Connect OAuth Integration Guide (WBG internal)
- ArcGIS REST API Reference: https://developers.arcgis.com/rest/
- Zambia GeoHub: https://zmb-geowb.hub.arcgis.com

---

*Prepared by: [Your Name], [Your Role]*
*Date: June 2026*
*Version: 1.0*
