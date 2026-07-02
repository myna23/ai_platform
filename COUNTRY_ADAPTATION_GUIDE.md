# GeoHub AI Assistant — Country Adaptation Guide

**What this guide is:** A step-by-step playbook covering two scenarios:

- **Part A — Single country swap:** Replace Zambia with a different country (e.g. deploy a Kenya-only version)
- **Part B — Multi-country:** Add a second (or third) country alongside Zambia so users can switch between them in one app

Read Part A first even if you want Part B — Part B builds on top of it.

**Time needed:** 1–2 days for a developer familiar with Python. Half a day if the country already has a GeoHub.

**What you need before you start:**
- Access to the country's GeoHub (ArcGIS Online Hub site)
- An ArcGIS token or API key from the country's GeoHub admin
- Python 3.9+ installed locally
- The same codebase (just copy the whole Zambia folder)

---

## Step 1 — Find the Country's GeoHub

Every World Bank country GeoHub follows the same pattern:

```
https://[country-code]-geowb.hub.arcgis.com
```

Examples:
- Zambia → `zmb-geowb.hub.arcgis.com`
- Kenya → `ken-geowb.hub.arcgis.com`
- Ghana → `gha-geowb.hub.arcgis.com`
- Tanzania → `tza-geowb.hub.arcgis.com`

Open the Hub in your browser and confirm it loads and has datasets. If the country does not have a Hub yet, contact the World Bank GOST (Geospatial Operations Support Team) team.

**Write down:**
- The full Hub URL: `https://___-geowb.hub.arcgis.com`
- The 3-letter country code (ISO code): e.g. `ken`, `gha`, `tza`

---

## Step 2 — Get the Dataset List from the New Hub

Go to the Hub URL and click **Data** or **Explore**. Write down the names of the key datasets available. Most WB country Hubs have:

- Health facilities
- Schools / education
- Roads / transport
- Administrative boundaries (districts, provinces)
- Settlements / populated places
- Flood risk / environment
- Population data

You need this list for Step 4.

**Also ask the Hub admin for:**
1. The ArcGIS token or API key (to access private datasets)
2. The content group ID (lists all datasets in the org)
3. The country tag used for public datasets (usually the 3-letter ISO code, like `ken`)

---

## Step 3 — Set Up the Environment File

Open the `.env` file in the project root. Change these two values:

```
# Old (Zambia)
ARCGIS_TOKEN=eyJ...your_zambia_token...
HUB_BASE_URL=https://zmb-geowb.hub.arcgis.com

# New (example: Kenya)
ARCGIS_TOKEN=eyJ...your_kenya_token...
HUB_BASE_URL=https://ken-geowb.hub.arcgis.com
```

That's the only change to `.env`.

---

## Step 4 — Update the Hub Client (`hub/client.py`)

This file is the connection to the GeoHub. It has 4 things to change.

### 4a. Change the Hub URL and country tag

Find these two lines near the top of `hub/client.py` (around line 292):

```python
# OLD
"Referer": "https://zmb-geowb.hub.arcgis.com",
"Origin":  "https://zmb-geowb.hub.arcgis.com",
```

Change to the new country Hub URL.

Also find where the search query uses the tag `zmb` (around line 278 in the `search_arcgis_online` function) and change `zmb` to the new country code.

### 4b. Replace the Offline Dataset Map (`_STATIC_MAP`)

This dictionary maps dataset names to offline backup files. Around line 100, find the block that starts with `_STATIC_MAP = {` and replace the dataset names on the LEFT side with the new country's dataset names. Keep the filenames on the right (you will replace those files in Step 6).

Example — Zambia to Kenya:
```python
# Zambia (old)
"Zambia_Health_Facilities": "health_facilities.json",
"Zambia_Education_Facilities": "schools.json",

# Kenya (new)
"Kenya_Health_Facilities_MFL": "health_facilities.json",
"Kenya_Primary_Schools": "schools.json",
```

> **How to find the correct dataset names:** Browse the country Hub, open a dataset, and copy the exact title from the URL or page header.

### 4c. Replace the Keyword-to-Dataset Map (`_SUBJECT_BOOST`)

Around line 190, find the `_SUBJECT_BOOST` dictionary. This maps keywords like "school", "hospital", "flood" to the correct dataset name. Update the dataset names on the RIGHT side to match what the new Hub calls those datasets.

Example:
```python
# Old (Zambia)
"school": "GRID3_ZMB_School",
"health": "GRID3_ZMB_HealthFac",

# New (Kenya)
"school": "Kenya_Primary_Schools",
"health": "Kenya_Health_Facilities_MFL",
```

### 4d. Clear the Blocklist

Around line 250, find `_BLOCKLIST = {` — a set of broken or protected ArcGIS URLs specific to Zambia. Delete all the URLs inside it and leave it as an empty set:

```python
_BLOCKLIST: set = set()
```

You can add new broken URLs later if you discover them while testing.

---

## Step 5 — Update the App (`app.py`)

This file has 5 things to change.

### 5a. Branding (page title and header)

Find these lines near the top of the app section (around line 990):

```python
# OLD
st.set_page_config(
    page_title="Zambia GeoHub AI",
    ...
)
```

Change `"Zambia GeoHub AI"` to the new country name, e.g. `"Kenya GeoHub AI"`.

Then find the hero header HTML (search for `zmb-hero` — around line 2281):

```html
<h1>Zambia GeoHub AI Assistant</h1>
<p>Explore Zambia's national geospatial data...</p>
```

Change "Zambia" to the new country name.

Also update the Hub link in the sidebar (search for `zmb-geowb.hub.arcgis.com` — around line 1869) to the new Hub URL.

### 5b. Language options

Around line 248, find `_LANG_INSTRUCTIONS`:

```python
_LANG_INSTRUCTIONS = {
    "English":  "",
    "Nyanja":   " Please respond in Chichewa/Nyanja language.",
    "Bemba":    " Please respond in Bemba language.",
    "Tonga":    " Please respond in Tonga language.",
}
```

Replace with the languages spoken in the new country. Keep English. Examples:

- Kenya: Swahili, Kikuyu
- Ghana: Twi, Ga, Ewe
- Tanzania: Swahili, Arabic
- Nigeria: Hausa, Yoruba, Igbo

If you don't know the correct language names for the AI, keep only English for now. You can add more later.

### 5c. Coordinate boundaries

Around line 2121, find the comment `Zambia bounds:` and the two lines below it:

```python
if -18 <= lat <= -8 and 21 <= lon <= 34:
```

Replace the numbers with the new country's bounding box. You can look these up at [bboxfinder.com](http://bboxfinder.com) or search "[country name] bounding box latitude longitude".

| Country | Approx. lat range | Approx. lon range |
|---|---|---|
| Kenya | -5 to 5 | 34 to 42 |
| Ghana | 5 to 11 | -3 to 1 |
| Tanzania | -12 to -1 | 29 to 41 |
| Nigeria | 4 to 14 | 3 to 15 |
| Ethiopia | 3 to 15 | 33 to 48 |

Update all three occurrences (the same check appears three times in that section).

### 5d. Province/district names

Around line 2071, find `_ZAMBIA_PROVINCES = {` — a dictionary of province names and their bounding boxes. Replace this entire dictionary with the new country's administrative divisions.

For each province/state/region, you need the name and rough lat/lon bounds. You can get these from the Hub's administrative boundary dataset.

```python
# Example for Kenya
_KENYA_COUNTIES = {
    "Nairobi":   {"min_lat": -1.44, "max_lat": -1.16, "min_lon": 36.65, "max_lon": 37.10},
    "Mombasa":   {"min_lat": -4.12, "max_lat": -3.94, "min_lon": 39.57, "max_lon": 39.73},
    # ... add all counties
}
```

Also rename the variable from `_ZAMBIA_PROVINCES` to `_[COUNTRY]_PROVINCES` and update the one reference to it below (around line 2086).

### 5e. City coordinates and road network

Around line 2188, find `_ZAMBIA_TOWN_COORDS = {` — a dictionary of city names and their lat/lon.

Around line 53, find `_ZMB_ROAD_SEGMENTS = {` — the offline road routing network.

Replace both with the new country's cities and major roads. These are only used for the offline road routing feature. If you want to keep things simple for now:
- Replace `_ZAMBIA_TOWN_COORDS` with the new country's major cities and their coordinates (easy to look up)
- For `_ZMB_ROAD_SEGMENTS`, you can leave it empty (`{}`) for now — the app will fall back to OSRM (live routing) which works for any country

---

## Step 6 — Replace the Offline Fallback Data (`data/` folder)

The `data/` folder contains pre-saved GeoJSON files used when the live Hub is unavailable. All of them are Zambia-specific and must be replaced.

**What to do:**
1. Open each dataset on the new country Hub
2. Download it as GeoJSON (most Hubs have a download button)
3. Save it with the same filename in the `data/` folder (replacing the Zambia file)

**Priority files to replace first:**

| File | What it contains | Priority |
|---|---|---|
| `districts.json` | Administrative boundary polygons | **Critical** — used for every map |
| `health_facilities.json` | Health facility points | High |
| `schools.json` | School locations | High |
| `settlements.json` | Village/town points | High |
| `roads.json` | Major road lines | Medium |
| `poi_all.json` | Points of interest | Medium |
| `flood_prone.json` | Flood risk zones | Medium |
| `population_districts.json` | Population by district | Low |

> If a dataset doesn't exist for the new country, delete the corresponding entry from `_STATIC_MAP` in `hub/client.py` (Step 4b). The app will simply not use that offline file.

---

## Step 7 — Update the AI Prompts (`ai/prompts.py`)

Open `ai/prompts.py`. Search for every occurrence of:
- `"Zambia"`
- `"zmb-geowb.hub.arcgis.com"`

Replace them with the new country name and Hub URL.

The key places are:
1. `chatbot_system_prompt()` — the first line says `"You are an AI assistant for the Zambia GeoHub"`
2. `tool_use_system_prompt()` — same first line
3. Any mention of Zambia-specific dataset types (e.g., the POI "Type" field categories — check if the new country uses the same categories or different ones)

Example change:
```python
# OLD
"You are an AI assistant for the Zambia GeoHub (zmb-geowb.hub.arcgis.com). "
"Your job is to help users understand and explore Zambia's geospatial data.\n\n"

# NEW (Kenya)
"You are an AI assistant for the Kenya GeoHub (ken-geowb.hub.arcgis.com). "
"Your job is to help users understand and explore Kenya's geospatial data.\n\n"
```

---

## Step 8 — Test Locally

Run the app locally:

```bash
streamlit run app.py
```

Test these things in order:

1. **Does the app load?** — check for errors in the terminal
2. **Does the chat respond?** — ask "what data is available?"
3. **Does the map work?** — ask about a district/province in the new country
4. **Does the AI find the right datasets?** — ask "how many health facilities are in [capital city]?"
5. **Does the fallback work?** — temporarily disconnect from the internet and ask a question

If any step fails, check the terminal for error messages. The most common issues are:
- Wrong dataset name in `_SEED_CATALOG` (Step 4b)
- Coordinate bounds not covering the country (Step 5c)
- Offline file not replaced (Step 6)

---

## Step 9 — Deploy

Once the local test works, deploy to Posit Connect (same as Zambia):

1. Push changes to GitHub
2. In Posit Connect, update the environment variables:
   - `ARCGIS_TOKEN` — new country token
   - `HUB_BASE_URL` — new country Hub URL
3. Redeploy the app

No other changes are needed for deployment.

---

## Summary: What Changes vs. What Stays the Same

| What CHANGES per country | What STAYS THE SAME |
|---|---|
| Hub URL (`zmb-geowb` → `ken-geowb`) | All the Python code logic |
| Country dataset names in `hub/client.py` | AI model (mAI Factory) |
| Coordinate bounding box in `app.py` | Authentication system (Posit OAuth) |
| Province/city names and coordinates | Report generation (.docx / .pdf) |
| Language options in `app.py` | Map rendering (pydeck) |
| All `data/*.json` offline files | Deployment platform (Posit Connect) |
| Country name in page title and prompts | `.env` structure (just different values) |
| ArcGIS token in `.env` | All other dependencies |

---

## Common Problems and Fixes

| Problem | Likely cause | Fix |
|---|---|---|
| "No datasets found" | Wrong Hub URL or country tag | Check `hub/client.py` Step 4a |
| Map shows Zambia outline | Old `districts.json` not replaced | Replace file — Step 6 |
| Coordinate input not working | Bounding box not updated | Fix bounds — Step 5c |
| AI says "Zambia" for the wrong country | Prompts not updated | Step 7 |
| Language dropdown shows wrong languages | `_LANG_INSTRUCTIONS` not updated | Step 5b |
| App crashes on startup | Python error from renamed variable | Check Step 5d — variable rename |
| Live data works but offline fallback fails | `_STATIC_MAP` has wrong dataset name | Step 4b |

---

## If the Country Has No GeoHub Yet

If the target country does not have a World Bank GeoHub, you have two options:

**Option A — Use a national open data portal**
Many countries have their own geospatial portals on ArcGIS Online. The Hub client works with any ArcGIS Online FeatureServer URL — you just need to update `_SEED_CATALOG` with the correct dataset URLs from that portal.

**Option B — Upload datasets to a new Hub**
The World Bank GOST team can help set up a new country Hub. Once it exists, follow this guide from Step 1.

---

## Files Changed Summary (Quick Reference)

```
.env                      ← ARCGIS_TOKEN, HUB_BASE_URL
hub/client.py             ← Hub URL, country tag, dataset names, keyword map, blocklist
app.py                    ← Branding, languages, coordinate bounds, provinces, cities, roads
ai/prompts.py             ← Country name, Hub URL in all prompt strings
data/districts.json       ← REPLACE with new country boundaries
data/health_facilities.json  ← REPLACE
data/schools.json         ← REPLACE
data/settlements.json     ← REPLACE
data/roads.json           ← REPLACE
data/poi_all.json         ← REPLACE if available
data/flood_prone.json     ← REPLACE if available
```

Everything else in the codebase stays untouched.

---

---

# Part B — Adding a Second Country to the Same App

This section is for when you want **one app that serves multiple countries** — for example, Zambia and Kenya both available in the same deployment, with the user choosing which country to explore.

## What changes in this mode

When the app is multi-country:

1. **The title and AI identity become neutral** — instead of "You are an AI assistant for the Zambia GeoHub", the AI says "You are a geospatial data assistant" and references whichever country the user has selected.
2. **A country selector appears in the sidebar** — users pick their country and the Hub, datasets, languages, and map all switch automatically.
3. **Each country's data lives in its own subfolder** — `data/zmb/`, `data/ken/`, etc. instead of one shared `data/` folder.
4. **One central config file defines all countries** — adding a new country means adding one block to that file, nothing else.

---

## B1 — Create a Country Config File

Create a new file: `countries/config.py`

```python
# countries/config.py
# Add one entry per country. The key is what appears in the dropdown.

COUNTRIES = {

    "Zambia": {
        "hub_url":    "https://zmb-geowb.hub.arcgis.com",
        "code":       "zmb",
        "data_dir":   "data/zmb",
        "bounds":     {"lat_min": -18, "lat_max": -8,  "lon_min": 21, "lon_max": 34},
        "languages":  {
            "English": "",
            "Nyanja":  " Please respond in Chichewa/Nyanja language.",
            "Bemba":   " Please respond in Bemba language.",
            "Tonga":   " Please respond in Tonga language.",
        },
        "admin_level": "District",      # field name in datasets for admin unit
        "provinces": {
            "Lusaka Province":    {"min_lat": -16.0, "max_lat": -14.5, "min_lon": 27.5, "max_lon": 29.5},
            "Copperbelt Province":{"min_lat": -13.5, "max_lat": -11.5, "min_lon": 27.0, "max_lon": 29.5},
            # ... add others
        },
        "cities": {
            "lusaka":   (-15.4167, 28.2833),
            "ndola":    (-12.9587, 28.6366),
            "kitwe":    (-12.8024, 28.2132),
            # ... add others
        },
    },

    "Kenya": {
        "hub_url":    "https://ken-geowb.hub.arcgis.com",
        "code":       "ken",
        "data_dir":   "data/ken",
        "bounds":     {"lat_min": -5, "lat_max": 5, "lon_min": 34, "lon_max": 42},
        "languages":  {
            "English": "",
            "Swahili": " Please respond in Swahili language.",
        },
        "admin_level": "County",
        "provinces": {
            "Nairobi":  {"min_lat": -1.44, "max_lat": -1.16, "min_lon": 36.65, "max_lon": 37.10},
            "Mombasa":  {"min_lat": -4.12, "max_lat": -3.94, "min_lon": 39.57, "max_lon": 39.73},
            # ... add others
        },
        "cities": {
            "nairobi":  (-1.2921,  36.8219),
            "mombasa":  (-4.0435,  39.6682),
            "kisumu":   (-0.1022,  34.7617),
            # ... add others
        },
    },

    # To add a third country, copy the block above and fill in the values.
    # "Ghana": { ... },
    # "Tanzania": { ... },

}
```

Also create an empty `countries/__init__.py` file (just leave it blank) so Python treats it as a module.

---

## B2 — Reorganise the Data Folder

Move the Zambia offline files into a subfolder, and create a matching folder for Kenya:

```
data/
  zmb/
    districts.json
    health_facilities.json
    schools.json
    settlements.json
    roads.json
    poi_all.json
    flood_prone.json
    ...
  ken/
    districts.json          ← download from Kenya Hub
    health_facilities.json  ← download from Kenya Hub
    schools.json            ← download from Kenya Hub
    settlements.json        ← download from Kenya Hub
    ...
```

Shell commands to do the move:

```bash
mkdir -p data/zmb data/ken
mv data/*.json data/zmb/
```

Then download Kenya files into `data/ken/`. You can leave `data/ken/` files missing for now — the app will fall back gracefully to live API data.

---

## B3 — Update `hub/client.py` to Accept a Dynamic Hub URL

Find the `HubClient` class `__init__` method. Change it so the Hub URL is passed in as a parameter instead of being hardcoded:

```python
# OLD — hardcoded Zambia URL
class HubClient:
    def __init__(self):
        self.base_url = "https://zmb-geowb.hub.arcgis.com"
        ...

# NEW — accepts any country's URL
class HubClient:
    def __init__(self, hub_url: str, country_code: str, data_dir: str):
        self.base_url    = hub_url
        self.country_code = country_code
        self.data_dir    = data_dir
        ...
```

Anywhere in the file that previously had `"https://zmb-geowb.hub.arcgis.com"` hardcoded, replace it with `self.base_url`.

Anywhere that loaded offline files from `data/` should now load from `self.data_dir/`.

Example — finding the offline file path:
```python
# OLD
path = os.path.join("data", filename)

# NEW
path = os.path.join(self.data_dir, filename)
```

---

## B4 — Add the Country Selector to the Sidebar (`app.py`)

At the top of the sidebar section in `app.py`, add a country dropdown:

```python
from countries.config import COUNTRIES

# In the sidebar
selected_country = st.sidebar.selectbox(
    "Select Country",
    options=list(COUNTRIES.keys()),
    index=0,
)

country_cfg = COUNTRIES[selected_country]

# Build the Hub client for the selected country
hub = HubClient(
    hub_url      = country_cfg["hub_url"],
    country_code = country_cfg["code"],
    data_dir     = country_cfg["data_dir"],
)
```

Store `selected_country` and `country_cfg` in `st.session_state` so they persist across reruns:

```python
if "selected_country" not in st.session_state:
    st.session_state.selected_country = "Zambia"

if selected_country != st.session_state.selected_country:
    st.session_state.selected_country = selected_country
    st.session_state.messages = []   # clear chat when switching countries
    st.rerun()
```

---

## B5 — Make Language Options Dynamic

Instead of a hardcoded `_LANG_INSTRUCTIONS` dictionary, pull it from the country config:

```python
# OLD — fixed Zambia languages
_LANG_INSTRUCTIONS = {
    "English": "",
    "Nyanja": " Please respond in Chichewa/Nyanja language.",
    ...
}

# NEW — comes from the selected country's config
_LANG_INSTRUCTIONS = country_cfg["languages"]
```

The language dropdown automatically shows the right languages for whichever country is selected.

---

## B6 — Make the AI Prompt Neutral (No Country Hard-Coded)

In `ai/prompts.py`, change the system prompt so it takes the country as a parameter:

```python
# OLD
def chatbot_system_prompt() -> str:
    return (
        "You are an AI assistant for the Zambia GeoHub (zmb-geowb.hub.arcgis.com). "
        "Your job is to help users understand and explore Zambia's geospatial data.\n\n"
        ...
    )

# NEW — country passed in
def chatbot_system_prompt(country: str = "Zambia", hub_url: str = "") -> str:
    hub_ref = f" ({hub_url})" if hub_url else ""
    return (
        f"You are a geospatial data assistant for the {country} national GeoHub{hub_ref}. "
        f"Your job is to help users understand and explore {country}'s geospatial data.\n\n"
        ...
    )
```

Then in `app.py`, call it with the selected country:

```python
system = chatbot_system_prompt(
    country = selected_country,
    hub_url = country_cfg["hub_url"],
)
```

---

## B7 — Make Coordinate Bounds Dynamic

Find the coordinate validation block in `app.py` (the lines that check `if -18 <= lat <= -8 and 21 <= lon <= 34`). Replace the hardcoded numbers with values from the config:

```python
# OLD
if -18 <= lat <= -8 and 21 <= lon <= 34:

# NEW
b = country_cfg["bounds"]
if b["lat_min"] <= lat <= b["lat_max"] and b["lon_min"] <= lon <= b["lon_max"]:
```

Do the same for the province bounding-box lookup — replace `_ZAMBIA_PROVINCES` with `country_cfg["provinces"]` and the city lookup with `country_cfg["cities"]`.

---

## B8 — Update the Page Title and Hero

Change the page title to be neutral:

```python
# OLD
st.set_page_config(page_title="Zambia GeoHub AI", ...)

# NEW
st.set_page_config(page_title="GeoHub AI Assistant", ...)
```

For the hero header, show the selected country dynamically:

```html
<!-- OLD -->
<h1>Zambia GeoHub AI Assistant</h1>
<p>Explore Zambia's national geospatial data...</p>

<!-- NEW -->
<h1>GeoHub AI Assistant</h1>
<p>Explore {selected_country}'s national geospatial data...</p>
```

In practice, since this is Python f-string HTML:
```python
st.markdown(f"""
<div class="zmb-hero">
  <h1>GeoHub AI Assistant</h1>
  <p>Explore <strong>{selected_country}'s</strong> national geospatial data —
     health, education, infrastructure, environment and more.</p>
</div>
""", unsafe_allow_html=True)
```

---

## B9 — Test the Multi-Country Setup

Run the app locally and test:

1. **Country switcher works** — select Kenya in the dropdown, app reloads with Kenya datasets
2. **Chat clears on switch** — conversation from Zambia does not appear when switching to Kenya
3. **Languages update** — Kenya shows English + Swahili; Zambia shows English + Nyanja + Bemba + Tonga
4. **AI knows the right country** — ask "what country are you helping me with?" — it should say Kenya when Kenya is selected
5. **Map shows right area** — Kenya questions should produce a map centered on Kenya, not Zambia
6. **Offline fallback uses the right folder** — check that Kenya questions load from `data/ken/` not `data/zmb/`

---

## Adding a Third (or Fourth) Country Later

Once the multi-country structure is in place, adding a new country takes about **2–4 hours**:

1. Add one new block to `countries/config.py` with the Hub URL, bounds, languages, provinces, cities
2. Create `data/[code]/` folder and download the key GeoJSON files into it
3. Add the dataset names to a country-specific section in `hub/client.py` `_SEED_CATALOG`
4. Restart the app — the new country appears automatically in the dropdown

No other code changes needed.

---

## Summary: Single-Country vs. Multi-Country

| | Single Country (Part A) | Multi-Country (Part B) |
|---|---|---|
| App title | "Kenya GeoHub AI" | "GeoHub AI Assistant" |
| AI identity | "I am the Kenya GeoHub AI" | "I am a geospatial assistant" (country from selection) |
| Country config | Hardcoded per file | Central `countries/config.py` |
| Data folder | `data/` (one set) | `data/zmb/`, `data/ken/`, etc. |
| HubClient | Fixed Hub URL | URL passed in from config |
| Adding a country | Edit 5 files | Add one block to `config.py` + data folder |
| Coordinate bounds | Hardcoded numbers | From config dict |
| Language options | Hardcoded list | From config dict |
| When to use | One team, one country | Regional deployment, multiple countries |
