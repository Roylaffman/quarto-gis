# Users Guide and Implementation

**Quarto GIS Research Project**
Ryan Lafferty | Last updated: February 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture and Pipeline](#2-architecture-and-pipeline)
3. [Directory Structure](#3-directory-structure)
4. [Prerequisites and Installation](#4-prerequisites-and-installation)
5. [Database Setup (PostgreSQL/PostGIS)](#5-database-setup-postgresqlpostgis)
6. [Configuration Files](#6-configuration-files)
7. [Shared Python Modules](#7-shared-python-modules)
8. [Using the Analysis Template](#8-using-the-analysis-template)
9. [Using the Report Template](#9-using-the-report-template)
10. [Building Interactive Maps](#10-building-interactive-maps)
11. [Reusable Inserts](#11-reusable-inserts)
12. [Rendering and Output](#12-rendering-and-output)
13. [Documentation Site](#13-documentation-site)
14. [Loading New Data into PostGIS](#14-loading-new-data-into-postgis)
15. [Modifying and Extending the Setup](#15-modifying-and-extending-the-setup)
16. [Implementation Progress](#16-implementation-progress)
17. [Troubleshooting](#17-troubleshooting)

---

## 1. Project Overview

This project provides a complete workflow for producing standalone, interactive HTML documents from spatial data stored in PostgreSQL/PostGIS. The pipeline is:

```
PostgreSQL/PostGIS  →  psycopg2  →  Python/Pandas/GeoPandas  →  Folium/Matplotlib/Plotly  →  Quarto  →  Standalone HTML
```

Every output is a single self-contained `.html` file (no server required) that includes interactive Leaflet maps, Plotly charts, styled tables, and code blocks you can fold or expand.

The project is built around an Everglades historical GIS dataset containing:

- **1978 Florida coastline** (5,689 MULTILINESTRING features, NOAA)
- **Historical routes** (4 LINESTRING features — water and smuggling routes)
- **Historical sites** (20 POINT features — trading posts, settlements, preserves)

### Design principles

- **HTML-first** — every document renders to standalone HTML with `embed-resources: true`
- **Database-driven** — all spatial data lives in PostGIS, queried on demand
- **Modular** — shared Python modules (`db_connection.py`, `map_builder.py`) keep code DRY
- **Template-based** — start new work by copying a template, not from scratch
- **Branded** — consistent fonts (Inter/JetBrains Mono) and color palette across all output

---

## 2. Architecture and Pipeline

### Data flow

```
                    ┌──────────────────────┐
                    │  PostgreSQL 17       │
                    │  PostGIS 3.5.2       │
                    │                      │
                    │  everglades_gis DB   │
                    │  ┌────────────────┐  │
                    │  │ 1978_fl_coast  │  │
                    │  │ hist_routes    │  │
                    │  │ hist_sites     │  │
                    │  └────────────────┘  │
                    └──────────┬───────────┘
                               │ psycopg2 + SQL
                               │ (ST_Transform for CRS)
                               ▼
                    ┌──────────────────────┐
                    │  db_connection.py    │
                    │                      │
                    │  query_to_dataframe  │
                    │  query_to_geodf      │
                    └──────────┬───────────┘
                               │ DataFrame / GeoDataFrame
                               ▼
                    ┌──────────────────────┐
                    │  map_builder.py      │
                    │                      │
                    │  create_base_map     │
                    │  add_gdf_layer       │
                    │  add_point_markers   │
                    │  finalize_map        │
                    └──────────┬───────────┘
                               │ Folium Map object
                               ▼
                    ┌──────────────────────┐
                    │  Quarto .qmd file    │
                    │                      │
                    │  analysis or report  │
                    │  template            │
                    └──────────┬───────────┘
                               │ quarto render
                               ▼
                    ┌──────────────────────┐
                    │  Standalone HTML     │
                    │  (37 MB, embed-all)  │
                    └──────────────────────┘
```

### Technology stack

| Component | Technology | Version | Purpose |
|---|---|---|---|
| Database | PostgreSQL | 17 | Spatial data storage |
| Spatial extension | PostGIS | 3.5.2 | Geometry types, spatial SQL |
| DB connector | psycopg2-binary | 2.9+ | Python ↔ PostgreSQL |
| Credential management | python-dotenv | 1.0+ | .env file loading |
| Spatial data | GeoPandas | 1.1+ | GeoDataFrame operations |
| Tabular data | Pandas | 2.1+ | DataFrame operations |
| Interactive maps | Folium | 0.20+ | Leaflet.js wrapper |
| Static maps | Matplotlib | 3.8+ | Thematic maps |
| Interactive charts | Plotly | 6.5+ | Bar charts, scatter plots |
| Document engine | Quarto | 1.8.27 | .qmd → HTML rendering |
| Python runtime | Python | 3.11 | Microsoft Store edition |

---

## 3. Directory Structure

```
quarto-gis/
│
├── CLAUDE.md                     # Project context for Claude AI sessions
├── TASKS.md                      # Task tracker (completed / backlog)
├── Users Guide and Implementation.md  # This document
├── README.md                     # Quick-start readme
├── load_costline.py              # Data loader: 1978 FL coastline → PostGIS
│
├── research/                     # ── Main research project (HTML output) ──
│   ├── _quarto.yml               # Quarto project config (theme, code-fold, etc.)
│   ├── _brand.yml                # Brand tokens (colors, fonts)
│   ├── theme.scss                # Bootstrap 5 / SCSS overrides
│   ├── requirements.txt          # Python package dependencies
│   ├── .env                      # Database credentials (NEVER commit)
│   ├── .env.example              # Credential template
│   │
│   ├── db_connection.py          # Shared module: PostGIS → DataFrame/GeoDataFrame
│   ├── map_builder.py            # Shared module: Folium map construction
│   │
│   ├── analysis/                 # Exploratory analysis documents
│   │   ├── _metadata.yml         # Folder defaults (cache, code-fold)
│   │   ├── analysis-template.qmd # Starter template
│   │   └── everglades-historical.qmd  # First real analysis (all 3 layers)
│   │
│   ├── reports/                  # Client/leadership-ready reports
│   │   ├── _metadata.yml
│   │   ├── report-template.qmd   # Starter template
│   │   └── references.bib        # BibTeX citations
│   │
│   ├── inserts/                  # Reusable drop-in blocks
│   │   ├── map-block.qmd         # Folium world map callout
│   │   ├── figure-callout.qmd    # Plotly bar chart callout
│   │   └── methods-block.qmd     # Methods section template
│   │
│   ├── includes/
│   │   └── footer.html           # HTML footer for all documents
│   │
│   └── _output/                  # Rendered HTML output (auto-generated)
│       └── analysis/
│           └── everglades-historical.html  # 37 MB standalone
│
└── docs/                         # ── Documentation website ──
    ├── _quarto.yml               # Website config (navbar, footer)
    ├── _brand.yml
    ├── theme.scss
    ├── index.qmd                 # Homepage
    └── guides/
        ├── workflow.qmd          # Complete pipeline walkthrough
        ├── setup.qmd             # Installation guide
        ├── gis-visuals.qmd       # Map and visualization patterns
        └── publishing.qmd        # Deployment guide
```

---

## 4. Prerequisites and Installation

### Software required

1. **Python 3.11** — currently using Microsoft Store edition
2. **PostgreSQL 17** with **PostGIS 3.5.2** extension
3. **Quarto 1.8+** — install from https://quarto.org/docs/get-started/

### Python packages

All packages are currently installed globally (no venv). The required packages are listed in `research/requirements.txt`:

```
pandas>=2.1
matplotlib>=3.8
plotly>=5.18
geopandas>=0.14
folium>=0.15
shapely>=2.0
pyproj>=3.6
psycopg2-binary>=2.9
python-dotenv>=1.0
```

Additionally, Quarto needs these Jupyter infrastructure packages:

```
pyyaml
nbformat
nbclient
ipykernel
jupyter-cache
```

### Installation commands

```bash
# Install the data science and GIS packages
pip install -r research/requirements.txt

# Install the Jupyter packages Quarto needs
pip install pyyaml nbformat nbclient ipykernel jupyter-cache
```

### Optional: using a virtual environment

```bash
cd research
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
pip install pyyaml nbformat nbclient ipykernel jupyter-cache
```

If using a venv, make sure it is activated before running `quarto render`.

---

## 5. Database Setup (PostgreSQL/PostGIS)

### Current database

- **Name**: `everglades_gis`
- **Host**: `localhost`
- **Port**: `5432`
- **User**: `postgres`
- **Password**: stored in `research/.env`

### Tables

| Table | Geometry Column | Type | SRID | Rows | Source |
|---|---|---|---|---|---|
| `1978_fl_coastline` | `wkb_geometry` | MULTILINESTRING | 4269 (NAD83) | 5,689 | NOAA coastline data |
| `historical_routes` | `geom` | LINESTRING | 4326 (WGS84) | 4 | Manual entry |
| `historical_sites` | `geom` | POINT | 4326 (WGS84) | 20 | Manual entry |

### SRID handling

The coastline table uses **SRID 4269 (NAD83)** while the other tables use **SRID 4326 (WGS84)**. Web maps (Folium/Leaflet) require 4326. Always transform the coastline geometry in your SQL:

```sql
SELECT ogc_fid, inform, attribute, class,
       ST_Transform(wkb_geometry, 4326) AS geom
FROM "1978_fl_coastline"
```

The `query_to_geodataframe()` function expects the output geometry column name and CRS:

```python
gdf = query_to_geodataframe(sql, geom_col="geom", crs=4326)
```

### Credential management

Credentials are stored in `research/.env` and loaded by `python-dotenv`. The file format:

```
PG_HOST=localhost
PG_PORT=5432
PG_DBNAME=everglades_gis
PG_USER=postgres
PG_PASSWORD=password
```

A template is provided at `research/.env.example`. Copy it and fill in your values:

```bash
cp research/.env.example research/.env
```

**Never commit `.env` to version control.** Add it to `.gitignore`.

---

## 6. Configuration Files

### `research/_quarto.yml` — Research project config

Controls how all research documents render.

| Setting | Value | Purpose |
|---|---|---|
| `output-dir: _output` | All HTML goes to `research/_output/` | Keeps source clean |
| `cache: true` | Caches cell output | Avoids re-running slow queries |
| `freeze: auto` | Freezes output when source unchanged | Speeds up batch renders |
| `embed-resources: true` | Self-contained HTML | No external dependencies |
| `code-fold: true` | Code hidden by default | Reader-friendly output |
| `code-tools: true` | Show/hide all code button | Viewer choice |
| `df-print: paged` | Paginated DataFrames | Better table display |
| `page-layout: full` | Full-width layout | More room for maps |
| `theme: cosmo + theme.scss` | Bootstrap Cosmo + custom overrides | Consistent look |

### `research/_brand.yml` — Brand tokens

Defines colors and typography used across all documents:

- **Fonts**: Inter (body), JetBrains Mono (code) — loaded from Google Fonts
- **Colors**: ocean (`#0ea5e9`), moss (`#22c55e`), ember (`#f97316`), rose (`#f43f5e`), slate (`#64748b`)

### `research/theme.scss` — SCSS overrides

Custom Bootstrap overrides. Must include the layer markers:

```scss
/*-- scss:defaults --*/
$font-family-sans-serif: "Inter", system-ui, ...;

/*-- scss:rules --*/
.content { max-width: 1200px; }
```

Without `/*-- scss:defaults --*/` and `/*-- scss:rules --*/`, Quarto will fail to render.

---

## 7. Shared Python Modules

### `db_connection.py`

Location: `research/db_connection.py`

Handles all database communication. Reads credentials from `.env` automatically.

#### Functions

| Function | Returns | Parameters | Purpose |
|---|---|---|---|
| `get_connection()` | `psycopg2.connection` | none | Raw database connection |
| `query_to_dataframe(query, params)` | `pd.DataFrame` | SQL string, optional params | Non-spatial tabular data |
| `query_to_geodataframe(query, geom_col, crs, params)` | `gpd.GeoDataFrame` | SQL string, geometry column name, CRS, optional params | Spatial data with geometry |

#### Usage in .qmd files

Since analysis and report files run from subdirectories, they need `sys.path.append("..")`:

```python
import sys
sys.path.append("..")
from db_connection import query_to_geodataframe, query_to_dataframe
```

#### Examples

```python
# Spatial query (returns GeoDataFrame)
gdf = query_to_geodataframe("""
    SELECT id, name, ST_Transform(wkb_geometry, 4326) AS geom
    FROM "1978_fl_coastline"
""", geom_col="geom", crs=4326)

# Tabular query (returns DataFrame)
df = query_to_dataframe("""
    SELECT name, year_established, significance_level
    FROM historical_sites
    ORDER BY year_established
""")

# Parameterized query (prevents SQL injection)
gdf = query_to_geodataframe("""
    SELECT id, name, geom FROM historical_sites
    WHERE site_type = %s
""", params=("Trading Post",))
```

### `map_builder.py`

Location: `research/map_builder.py`

Provides reusable functions for building Folium maps. All functions return the map object for chaining.

#### Tile presets

| Key | Tiles | Best for |
|---|---|---|
| `"positron"` | CartoDB positron | Clean, light base (default) |
| `"dark"` | CartoDB dark_matter | Dark theme, presentations |
| `"osm"` | OpenStreetMap | Detailed street-level context |

Pass any Folium-compatible tile string for custom tiles.

#### Functions

| Function | Purpose | Key parameters |
|---|---|---|
| `create_base_map()` | Create the Folium Map | `center`, `zoom`, `tiles`, `gdf` (auto-center) |
| `add_geodataframe_layer()` | Add a GeoDataFrame as GeoJSON | `name`, `tooltip_fields`, `style`, `highlight` |
| `add_point_markers()` | Add circle markers from lat/lon columns | `lat_col`, `lon_col`, `popup_col`, `tooltip_col`, `color` |
| `finalize_map()` | Add LayerControl, return map | none |

#### Full example

```python
from db_connection import query_to_geodataframe
from map_builder import create_base_map, add_geodataframe_layer, finalize_map

gdf = query_to_geodataframe("SELECT id, name, geom FROM historical_routes")

m = create_base_map(gdf=gdf, zoom=11, tiles="positron")
m = add_geodataframe_layer(
    m, gdf,
    name="Routes",
    tooltip_fields=["name"],
    style={"color": "#f97316", "weight": 3, "dashArray": "8 4"},
    highlight={"weight": 5, "opacity": 1},
)
m = finalize_map(m)
m  # displays in Quarto
```

#### Style reference

The `style` and `highlight` dicts accept any Leaflet Path options:

| Property | Type | Example | Effect |
|---|---|---|---|
| `color` | string | `"#0ea5e9"` | Stroke color |
| `weight` | number | `2` | Stroke width in pixels |
| `opacity` | number | `0.7` | Stroke opacity (0-1) |
| `fillColor` | string | `"#22c55e"` | Fill color (polygons) |
| `fillOpacity` | number | `0.3` | Fill opacity (0-1) |
| `dashArray` | string | `"8 4"` | Dashed line pattern |

---

## 8. Using the Analysis Template

**File**: `research/analysis/analysis-template.qmd`

The analysis template is for exploratory work: prototyping queries, iterating on map styles, testing hypotheses.

### How to start a new analysis

1. Copy the template:
   ```bash
   cp research/analysis/analysis-template.qmd research/analysis/my-analysis.qmd
   ```

2. Update the YAML header (title, subtitle).

3. Replace the sample PostGIS queries with your own.

4. Remove the Natural Earth sample sections once you have real data working.

5. Render:
   ```bash
   cd research
   quarto render analysis/my-analysis.qmd
   ```

### Template sections

| Section | What it does | Modify? |
|---|---|---|
| Environment | Prints Python versions, imports modules | Keep as-is |
| Connect to PostGIS | `query_to_geodataframe` / `query_to_dataframe` examples | Replace queries |
| Sample data | Natural Earth fallback (template renders without DB) | Remove when using real data |
| Static map | Matplotlib thematic map | Adapt to your data |
| Interactive map (map_builder) | Folium via shared module | Adapt to your data |
| Interactive map (PostGIS) | Same but from database | Uncomment + adapt |
| Summary table | Grouped aggregation | Adapt to your data |
| Decision log | Freeform notes | Fill in as you work |

### Real-world example: `everglades-historical.qmd`

This is the first completed analysis. It demonstrates:

- Querying all three PostGIS tables
- `ST_Transform` in SQL for CRS conversion
- Splitting coastline by classification (SHORELINE vs ALONGSHORE)
- Multi-layer Folium map with styled lines and colored point markers
- Plotly timeline chart
- Summary tables with `groupby` aggregations
- Full render to 37 MB standalone HTML

---

## 9. Using the Report Template

**File**: `research/reports/report-template.qmd`

The report template is for polished deliverables. It has numbered sections, an executive summary, and a structured layout.

### How to start a new report

1. Copy the template:
   ```bash
   cp research/reports/report-template.qmd research/reports/my-report.qmd
   ```

2. Update the YAML header (title, subtitle, author).

3. The hidden setup cell already imports `db_connection` and `map_builder` — just use them.

4. Fill in the executive summary first (forces you to know your story).

5. Write PostGIS queries in the "Data acquisition" section.

6. Build your key map in the "Results" section using `map_builder` functions.

7. Render:
   ```bash
   cd research
   quarto render reports/my-report.qmd
   ```

### Template sections

| Section | Purpose |
|---|---|
| Setup cell (hidden) | `echo: false` — imports modules without showing code |
| Executive summary | 3-bullet structure: what changed, what matters, what's next |
| Context and objectives | Who uses this, what decisions it informs |
| Data and methods | Includes `methods-block.qmd` insert + data acquisition code |
| Results | Key map (Folium) + key figure (Plotly insert) |
| Interpretation | Drivers, confounders, sensitivity checks |
| Recommendations | Numbered actions with owners and impact |
| Appendix | Reproducibility info, references |

### Analysis vs report — when to use which

| | Analysis | Report |
|---|---|---|
| Audience | You / your team | Stakeholders / clients |
| Structure | Freeform | Numbered sections |
| Code | Folded but present | Hidden setup, selective display |
| Decision log | Active, updated as you go | Not included |
| Polish | Working draft | Final deliverable |

---

## 10. Building Interactive Maps

### Pattern: database to map in 4 steps

```python
# 1. Query PostGIS
gdf = query_to_geodataframe("""
    SELECT id, name, ST_Transform(wkb_geometry, 4326) AS geom
    FROM "1978_fl_coastline"
    WHERE class = 'SHORELINE'
""", geom_col="geom", crs=4326)

# 2. Create base map
m = create_base_map(center=[25.85, -81.35], zoom=10, tiles="positron")

# 3. Add layers
m = add_geodataframe_layer(m, gdf,
    name="Shoreline",
    tooltip_fields=["name"],
    style={"color": "#0ea5e9", "weight": 1.5},
)

# 4. Finalize and display
m = finalize_map(m)
m
```

### Multiple layers on one map

You can call `add_geodataframe_layer()` and `add_point_markers()` as many times as needed before `finalize_map()`. Each layer appears in the LayerControl toggle.

### Custom point markers

For more control than `add_point_markers()` provides, use Folium directly:

```python
import folium

for _, row in sites.iterrows():
    color = "#f43f5e" if row["significance_level"] == "High" else "#0ea5e9"
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=8,
        color=color,
        fill=True,
        fill_opacity=0.8,
        tooltip=f"<b>{row['name']}</b>",
        popup=folium.Popup(f"{row['description']}", max_width=300),
    ).add_to(m)
```

### Performance tips for large datasets

- **Simplify in SQL**: `ST_Simplify(geom, 0.001)` reduces vertex count
- **Filter spatially**: `WHERE ST_Intersects(geom, ST_MakeEnvelope(...))` limits to your area
- **Use `LIMIT`** during development
- **Quarto caching** (`cache: true` in `_quarto.yml`) avoids re-running queries on every render

---

## 11. Reusable Inserts

Location: `research/inserts/`

Inserts are `.qmd` snippets you drop into any document with:

```markdown
{{< include ../inserts/map-block.qmd >}}
```

### Available inserts

| File | Content | Wrapped in |
|---|---|---|
| `map-block.qmd` | Folium world map with country tooltips | `.callout-tip` |
| `figure-callout.qmd` | Plotly GDP bar chart with interpretation notes | `.callout-important` |
| `methods-block.qmd` | Structured methods section (inputs, processing, validation) | `.callout-note` |

### Creating a new insert

1. Create a `.qmd` file in `research/inserts/`:

   ```markdown
   ::: {.callout-tip}
   ## My Block Title

   Content here (code cells, markdown, images).
   :::
   ```

2. Include it in your document:

   ```markdown
   {{< include ../inserts/my-block.qmd >}}
   ```

### When to create inserts

- Same code/text appears in 2+ documents
- You want a standardized map style or figure format
- Boilerplate sections (disclaimers, data dictionaries, methods)

---

## 12. Rendering and Output

### Render commands

```bash
# Render a single document
cd research
quarto render analysis/everglades-historical.qmd

# Preview with live reload (opens browser)
quarto preview analysis/everglades-historical.qmd

# Render all documents in the research project
quarto render

# Render the docs website
cd ../docs
quarto render
```

### Output locations

| Project | Output directory | Format |
|---|---|---|
| Research | `research/_output/` | Standalone HTML |
| Docs website | `docs/_site/` | Multi-page website |

### Caching behavior

- `cache: true` in `_quarto.yml` — Quarto caches cell output between renders
- `freeze: auto` — frozen output is used when source hasn't changed
- The `everglades-historical.qmd` overrides this with `cache: false` in its YAML header to always re-query the database
- To force a fresh render: delete `research/_freeze/` and `research/_output/`

### Output size

The Everglades analysis renders to ~37 MB because `embed-resources: true` inlines all map tiles, JavaScript, and CSS. This is intentional — the file works offline, in email, or on any file share.

To reduce size:
- Simplify geometries (`ST_Simplify`)
- Limit the number of features loaded
- Filter to a geographic extent

---

## 13. Documentation Site

Location: `docs/`

A separate Quarto Website project for team documentation.

### Navbar pages

| Page | Content |
|---|---|
| Home (`index.qmd`) | Project overview |
| Workflow Guide (`guides/workflow.qmd`) | Complete pipeline walkthrough — DB, modules, templates, inserts |
| Setup (`guides/setup.qmd`) | Installation and environment setup |
| GIS Visuals (`guides/gis-visuals.qmd`) | Static vs interactive maps, CRS recommendations, patterns |
| Publishing (`guides/publishing.qmd`) | Deployment options |

### Rendering the docs site

```bash
cd docs
quarto preview     # live reload
quarto render      # build to docs/_site/
```

---

## 14. Loading New Data into PostGIS

### Using `load_costline.py` as a pattern

The existing loader script demonstrates the pattern for importing SQL dumps:

```python
import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'password',
    'database': 'everglades_gis'
}

conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()

with open(r'path\to\your_data.sql', 'r') as f:
    sql_content = f.read()

# Fix common export issues before executing
sql_content = sql_content.replace('NUMERIC(33,31)', 'NUMERIC')

cur.execute(sql_content)
conn.commit()

# Verify
cur.execute("SELECT COUNT(*) FROM your_table")
print(cur.fetchone()[0], "rows loaded")

cur.close()
conn.close()
```

### Loading shapefiles with ogr2ogr

```bash
ogr2ogr -f "PostgreSQL" PG:"host=localhost dbname=everglades_gis user=postgres password=password" \
    "path/to/your_shapefile.shp" \
    -nln your_table_name \
    -s_srs EPSG:4269 -t_srs EPSG:4326 \
    -lco GEOMETRY_NAME=geom
```

### Loading GeoJSON or GeoPackage with Python

```python
import geopandas as gpd
from sqlalchemy import create_engine

gdf = gpd.read_file("path/to/data.geojson")
gdf = gdf.to_crs(4326)

engine = create_engine("postgresql://postgres:password@localhost/everglades_gis")
gdf.to_postgis("new_table_name", engine, if_exists="replace", index=False)
```

### Common data issues and fixes

| Problem | Symptom | Fix |
|---|---|---|
| NUMERIC overflow | `numeric field overflow` error | Replace `NUMERIC(33,31)` with `NUMERIC` |
| Wrong SRID | Data appears in wrong location on map | Use `ST_Transform(geom, 4326)` in queries |
| Mixed geometry types | `GeometryType` returns multiple types | Filter or use `ST_Multi()` to normalize |
| NULL geometries | Empty features on map | Add `WHERE geom IS NOT NULL` to queries |

---

## 15. Modifying and Extending the Setup

### Adding a new database table

1. Load the data (see [section 14](#14-loading-new-data-into-postgis))
2. Update `CLAUDE.md` — add the table to the Tables section
3. Update `TASKS.md` — log it in the completed section
4. Query it using `query_to_geodataframe()` in your `.qmd` file

### Changing the brand colors

Edit `research/_brand.yml`:

```yaml
color:
  palette:
    ocean: "#0ea5e9"    # change these hex values
    moss: "#22c55e"
    ember: "#f97316"
  primary: ocean        # or reassign roles
```

Then update `map_builder.py` style dicts and any hardcoded colors in `.qmd` files to match.

### Adding a new tile provider

Edit `research/map_builder.py`:

```python
TILES = {
    "positron": "CartoDB positron",
    "dark": "CartoDB dark_matter",
    "osm": "OpenStreetMap",
    "satellite": "Esri.WorldImagery",    # add new entry
}
```

Or pass any tile string directly: `create_base_map(tiles="Stamen Terrain")`

### Adding a new map function to `map_builder.py`

Follow the existing pattern — accept the map object `m` as the first argument, modify it, and return it:

```python
def add_heatmap(m, df, lat_col="latitude", lon_col="longitude", radius=15):
    from folium.plugins import HeatMap
    heat_data = df[[lat_col, lon_col]].values.tolist()
    HeatMap(heat_data, radius=radius).add_to(m)
    return m
```

### Adding a new query helper to `db_connection.py`

```python
def query_to_dict(query, params=None):
    """Run a SQL query and return results as a list of dicts."""
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, params)
        results = [dict(row) for row in cur.fetchall()]
        cur.close()
    finally:
        conn.close()
    return results
```

### Changing the Quarto theme

Edit `research/_quarto.yml`:

```yaml
format:
  html:
    theme:
      - cosmo        # change to: flatly, litera, lux, journal, etc.
      - theme.scss   # your overrides still apply
```

Available themes: https://quarto.org/docs/output-formats/html-themes.html

### Adding a new insert

1. Create `research/inserts/your-insert.qmd`
2. Include it: `{{< include ../inserts/your-insert.qmd >}}`

### Switching from global packages to a venv

```bash
cd research
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pyyaml nbformat nbclient ipykernel jupyter-cache
```

Then always activate before rendering.

---

## 16. Implementation Progress

### What has been built

| Phase | What was done |
|---|---|
| **Scaffolding** | Full project structure, both Quarto sub-projects, templates, brand, theme, inserts, docs site |
| **Database layer** | `db_connection.py` module, `.env` credential management, PostGIS verified |
| **Map layer** | `map_builder.py` module with tile presets, GeoDataFrame layers, point markers, styling |
| **Template integration** | Both analysis and report templates wired to use shared modules |
| **Data loading** | `load_costline.py` fixed and executed — 5,689 coastline features loaded |
| **First analysis** | `everglades-historical.qmd` — all three layers, static + interactive maps, charts, tables |
| **Full pipeline test** | End-to-end render: PostGIS → Python → Folium → Quarto → 37 MB standalone HTML |
| **Documentation** | Workflow guide, setup guide, GIS visuals guide, this document |
| **Environment fixes** | Installed all missing packages, fixed SCSS layer markers, disabled missing lightbox filter |

### Issues encountered and resolved

| Issue | Cause | Resolution |
|---|---|---|
| `psycopg2` connection failure | Password was placeholder `'your_password'` | Updated to actual password |
| `NumericValueOutOfRange` on coastline load | SQL export used `NUMERIC(33,31)` — only 2 digits before decimal | String-replace to `NUMERIC` before execution |
| Wrong table/column in verify query | Script referenced `florida_coastline_1978.geom` instead of `1978_fl_coastline.wkb_geometry` | Fixed table and column names |
| Coastline not aligning on web map | SRID 4269 (NAD83) vs expected 4326 (WGS84) | Added `ST_Transform(wkb_geometry, 4326)` to all coastline queries |
| `No module named 'yaml'` | PyYAML not installed | `pip install pyyaml` |
| `No module named 'nbformat'` | Jupyter packages not installed | `pip install nbformat nbclient ipykernel` |
| `jupyter-cache package required` | jupyter-cache not installed | `pip install jupyter-cache` |
| `theme.scss doesn't contain layer boundary` | Missing SCSS markers | Added `/*-- scss:defaults --*/` and `/*-- scss:rules --*/` |
| `Could not find executable lightbox` | Lightbox filter referenced but not installed | Commented out in `_quarto.yml` |

### Current database state

| Table | Geometry | SRID | Rows | Description |
|---|---|---|---|---|
| `1978_fl_coastline` | wkb_geometry (MULTILINESTRING) | 4269 | 5,689 | 1978 NOAA Florida coastline |
| `historical_routes` | geom (LINESTRING) | 4326 | 4 | Barron River, Chatham River, Lopez River, Wilderness Waterway |
| `historical_sites` | geom (POINT) | 4326 | 20 | Trading posts, settlements, preserves, smuggling sites |

### Remaining backlog

- [ ] Set up git repo and `.gitignore`
- [ ] Optimize coastline rendering (simplify geometry, filter to Everglades extent)
- [ ] Add more data layers to Everglades analysis
- [ ] Publish docs site (GitHub Pages or other host)

---

## 17. Troubleshooting

### Quarto can't find Python

```bash
# Check which Python Quarto sees
quarto check jupyter

# Set explicitly if needed
set QUARTO_PYTHON=C:\path\to\python.exe
```

### Missing Python package errors during render

Install the missing package globally:

```bash
pip install <package-name>
```

Key packages Quarto needs beyond the data science stack: `pyyaml`, `nbformat`, `nbclient`, `ipykernel`, `jupyter-cache`.

### `theme.scss` layer boundary error

Your SCSS file must contain at least one layer marker. Minimum required:

```scss
/*-- scss:defaults --*/
/* variables here */

/*-- scss:rules --*/
/* CSS rules here */
```

### Database connection refused

1. Check PostgreSQL is running: `pg_isready -h localhost`
2. Verify credentials in `research/.env`
3. Make sure the `everglades_gis` database exists: `psql -U postgres -l`

### Lightbox filter error

The lightbox filter is commented out in `_quarto.yml`. To install it:

```bash
cd research
quarto add quarto-ext/lightbox
```

Then uncomment the filter in `_quarto.yml`:

```yaml
filters:
  - lightbox
```

### Map renders but appears blank

- Check that geometry is in SRID 4326 (WGS84)
- Verify the center coordinates match your data's extent
- Try a different tile provider (`tiles="osm"`)
- Check browser console for JavaScript errors

### Large file output (>50 MB)

- Simplify geometries: `ST_Simplify(geom, 0.001)` in SQL
- Limit feature count: `LIMIT 1000` during development
- Filter to area of interest: `WHERE ST_Intersects(geom, ST_MakeEnvelope(...))`
- Consider disabling `embed-resources` for development previews
