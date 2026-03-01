# Quarto GIS Research Project

## Owner
Ryan Lafferty

## Pipeline
PostgreSQL/PostGIS → psycopg2 → Python/Pandas → Folium → Quarto Document (HTML-first)

## Project Layout
```
quarto-gis/
  CLAUDE.md              ← this file (project context for Claude sessions)
  TASKS.md               ← task tracker
  Users Guide and Implementation.md ← comprehensive documentation
  load_costline.py       ← loads 1978 FL coastline SQL into PostGIS
  roman_roads_harvester.py ← fetches Itiner-e data, loads into PostGIS
  data/roman_roads/      ← downloaded NDJSON + GeoJSON (not committed)
  research/              ← analysis + reports (HTML-first output)
    db_connection.py     ← shared PostGIS connection module (uses .env)
    map_builder.py       ← shared Folium map builder (create_base_map, add layers, finalize)
    .env.example         ← credential template
    .env                 ← actual credentials (never committed)
    _quarto.yml          ← Cosmo theme, code-fold, embed-resources
    _brand.yml           ← brand tokens (Inter font, ocean/moss/ember palette)
    theme.scss           ← Bootstrap overrides
    requirements.txt     ← Python dependencies
    analysis/
      _metadata.yml      ← folder-level defaults (cache, code-fold, full layout)
      analysis-template.qmd  ← EDA / exploration notebook
      everglades-historical.qmd ← Everglades story map (coastline + routes + sites)
      roman-roads.qmd        ← Roman roads story map (Itiner-e data)
      roman-roads-poi.json   ← user-curated POIs with photo URLs
      critical-minerals.qmd  ← Critical minerals story map (lithium, REE, strategic metals)
      CriticalMineralsSites.json ← 17 curated mining sites across the Americas
    reports/
      _metadata.yml
      report-template.qmd   ← client/leadership-ready report
      references.bib
    inserts/              ← reusable drop-in blocks (include shortcode)
      map-block.qmd       ← Folium world map
      figure-callout.qmd  ← figure callout pattern
      methods-block.qmd   ← methods section
    includes/
      footer.html
  docs/                   ← documentation website (Quarto Website project)
    _quarto.yml           ← website config, navbar
    _brand.yml
    theme.scss
    index.qmd
    guides/
      workflow.qmd        ← comprehensive workflow guide (DB → maps → templates)
      setup.qmd
      gis-visuals.qmd
      publishing.qmd
```

## Tech Stack
- **Quarto** — rendering engine (HTML-first, embed-resources: true for standalone files)
- **Python 3** — Jupyter kernel in .qmd files
- **GeoPandas** — spatial data handling
- **Folium/Leaflet** — interactive web maps
- **Matplotlib** — static thematic maps
- **Plotly** — interactive charts
- **psycopg2** — PostgreSQL/PostGIS database connection
- **python-dotenv** — .env-based credential management
- **Pandas** — tabular data
- **SQLAlchemy + geoalchemy2** — PostGIS table creation (used by roman_roads_harvester)
- **requests** — HTTP data fetching (Itiner-e API)

## Shared Python Modules
- **`db_connection.py`** — `get_connection()`, `query_to_dataframe(sql)`, `query_to_geodataframe(sql)`
  - Reads credentials from `research/.env` via python-dotenv
  - Templates import via `sys.path.append("..")` since they run from subdirectories
- **`map_builder.py`** — `create_base_map()`, `add_geodataframe_layer()`, `add_point_markers()`, `build_photo_popup()`, `finalize_map()`
  - Tile presets: "positron" (default), "dark", "osm", "satellite" (Esri.WorldImagery)
  - Auto-centers on GeoDataFrame bounds when `gdf=` is passed
  - `build_photo_popup()` generates HTML with optional `<img>` tag, graceful `onerror` handling
  - Style/highlight dicts for consistent look across documents

## Key Patterns
- Templates live in `research/analysis/` (EDA) and `research/reports/` (polished)
- Both templates import `db_connection` and `map_builder` via `sys.path.append("..")`
- Reusable blocks go in `research/inserts/` — include via `{{< include inserts/map-block.qmd >}}`
- Promote stable analysis outputs into report templates
- `docs/` is a separate Quarto Website for team documentation
- CRS: EPSG:4326 (WGS84) for web maps; local projected CRS for distance/area calcs
- Python venv lives at `research/.venv` — activate before rendering

## Brand
- Fonts: Inter (base), JetBrains Mono (code) — Google Fonts
- Colors: ocean (#0ea5e9) primary, slate (#64748b) secondary, moss (#22c55e) success, ember (#f97316) warning, rose (#f43f5e) danger
- Base font size: 16px, line-height: 1.55

## Database (PostGIS)
- **Database**: `everglades_gis` on localhost (PostgreSQL 17, PostGIS 3.5.2)
- **User**: `postgres`
- **Credentials**: stored in `research/.env` (never committed), template at `.env.example`
- **Connection module**: `research/db_connection.py` uses python-dotenv

### Tables
| Table | Geometry | SRID | Rows | Description |
|---|---|---|---|---|
| `1978_fl_coastline` | wkb_geometry (MULTILINESTRING) | 4269 | 5,689 | 1978 FL coastline features |
| `historical_routes` | geom (LINESTRING) | 4326 | 4 | Historical travel routes |
| `historical_sites` | geom (POINT) | 4326 | 20 | Historical site locations |
| `roman_road_segments` | geometry (LINESTRING) | 4326 | 16,554 | Itiner-e route segments |
| `roman_road_places` | geometry (POINT) | 4326 | 11,847 | Pleiades places linked to road segments |

### Data loader scripts
- `load_costline.py` — loads `FL GIS Data/1978_FL_coastline.sql` into `1978_fl_coastline`
  - Note: SQL export had bad NUMERIC(33,31) precision; script replaces with NUMERIC before executing
- `roman_roads_harvester.py` — fetches from Itiner-e API, saves GeoJSON/NDJSON, loads via SQLAlchemy
  - Usage: `python roman_roads_harvester.py --mode bulk --output ./data/roman_roads`
  - Load: `python roman_roads_harvester.py --mode load --input ./data/roman_roads --db-url "postgresql://postgres:password@localhost:5432/everglades_gis"`

## Environment Setup
```bash
cd research
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env            # then edit .env with your credentials
```

## Conventions
- All HTML output uses `embed-resources: true` for self-contained files
- Code blocks default to folded (`code-fold: true`)
- Execution caching enabled (`cache: true`, `freeze: auto`)
- Output directory: `research/_output/` for research, `docs/_site/` for docs
- PostGIS cells use `#| eval: false` until credentials are configured
- 1978_fl_coastline uses SRID 4269 (NAD83) — always use `ST_Transform(wkb_geometry, 4326)` in queries for web maps
- theme.scss files require `/*-- scss:defaults --*/` and `/*-- scss:rules --*/` layer markers (Quarto requirement)
- lightbox filter not installed — commented out in `_quarto.yml` (install with `quarto add quarto-ext/lightbox` if needed)
- Packages installed globally (not venv): geopandas, psycopg2, folium, plotly, python-dotenv, matplotlib, jupyter-cache
- GIS data source files at `c:\Users\royla\Documents\FL GIS Data\`

## Everglades Historical Document Structure
The `everglades-historical.qmd` is a narrative story map with 10 sections:

1. **The Outlaw Coast** — intro narrative (rum-runners → saltwater cowboys → Square Grouper)
2. **Points of Interest** — sites table (Name, Type, Year, Description)
3. **The Smuggler's Highway** — routes narrative (Barron, Chatham, Lopez, Wilderness Waterway)
4. **Route Details** — routes table
5. **Smuggling Routes & Historical Sites** — combined Folium map (satellite tile, wider popups)
6. **Coastline Overview** — static matplotlib map (CARTOGRAPHIC LIMIT filtered)
7. **Sites Timeline** — Plotly scatter
8. **Documentation & Source Data** — route citations + video reference
9. **Technical Details** — appendix (Environment, Feature Breakdown, Notes)

Map styling: satellite-optimized palette (shoreline #38bdf8, routes #fbbf24 amber, markers 9/6px radius, popups max_width=450 with min-width:280px div)

## Roman Roads Document Structure
The `roman-roads.qmd` is a narrative story map with 9 sections:

1. **All Roads Lead to Rome** — intro narrative (250,000 miles, Itiner-e project)
2. **The Road Network** — summary stats by road_type + construction_period
3. **Stationes and Mansiones** — places table (Name, Type, Period)
4. **The Empire's Road Map** — combined Folium map (positron tile, roads by type, places, user POIs with photo popups)
5. **Points of Interest** — user-curated POI table from `roman-roads-poi.json`
6. **Construction Timeline** — Plotly scatter (aggregated by type + date)
7. **Static Overview** — matplotlib map colored by road type
8. **Data Source & Bibliography** — Itiner-e citation, CC BY 4.0, Pleiades
9. **Technical Details** — appendix (Environment, Data Summary, Feature Breakdown, Notes)

Bounding box: W 5.74, S 36.71, E 29.04, N 48.47 (core Roman Empire)
Road colors: Main #f97316, Secondary #d97706, Sea Lane #64748b dashed, River #0ea5e9
Photo popups: `build_photo_popup()` from map_builder.py, POI data in `roman-roads-poi.json`
Performance: `ST_Simplify(geometry, 0.005)` for road segments, GeoJSON layer for places

## Critical Minerals Document Structure
The `critical-minerals.qmd` is a narrative story map with 10 sections:

1. **The White Gold Rush** — intro narrative (EV demand, IRA, Lithium Triangle, China dominance)
2. **Mining Sites** — data table from CriticalMineralsSites.json (Name, Category, Status, Operator)
3. **The Lithium Triangle** — narrative (Chile/Argentina/Bolivia geology, extraction, geopolitics)
4. **Sites by Category** — breakdowns by category, status, country
5. **The Americas' Critical Minerals Map** — Folium map (positron tile, category colors, status icons)
6. **Global Production: Americas vs. the World** — Plotly horizontal bar (lithium production by country)
7. **Rare Earth Dominance** — Plotly donut chart (China's 60% REE share)
8. **Static Overview** — matplotlib scatter map with contextily basemap
9. **Data Sources & Bibliography** — USGS, IEA, IRA, operator references
10. **Technical Details** — Environment, Data Summary, Decision Log

Map styling: positron tile, Lithium=#22c55e green, Rare Earth=#f97316 orange, Strategic Metals=#0ea5e9 blue. Icons by status (industry/wrench/check-circle/flask/question-circle). No PostGIS dependency — JSON-only data approach.

## Rana boylii Document Structure
The `rana-boylii.qmd` is a narrative story map with 10 sections:

1. **The Sentinel of the Streams** — intro narrative (ecological indicator species, range loss 45-55%, ESA listings 2023-2024)
2. **Data & Setup** — imports + load all 5 layers (CA, range, clades, ecoregions, GBIF CSV)
3. **The Habitat** — narrative (lotic ecosystems, cobble substrate, flow regime, riparian vegetation)
4. **Range & Management Units** — ESA status table by clade (6 CDFW clades → 4 DPS) + ecoregion summary table
5. **The Frog's Territory** — Folium interactive map (4 toggleable layers: EPA ecoregions, CDFW range, clade boundaries, GBIF heatmap)
6. **A Shrinking Map** — Plotly bar (GBIF observations by decade) + narrative on spatial decline patterns
7. **Why the Frogs Are Disappearing** — narrative (4 threats: dams, invasives, climate, conservation paradox)
8. **The Four DPS and Their Status** — Plotly horizontal bar (range loss %) + DPS status table
9. **Static Overview** — matplotlib map in EPSG:3310 (CA Albers) with ecoregions, range, clade outlines, thinned GBIF points
10. **Data Sources & Bibliography** — CDFW ds589/ds2865, EPA ecoregions, GBIF, USFWS ESA listings, Welsh/McCartney-Melstad/Hayes literature

Data files (downloaded once by `download_rana_boylii_data.py`):
- `data/rana_boylii/california.geojson` (85 KB, Natural Earth fallback)
- `data/rana_boylii/rana_boylii_range.geojson` (9,967 KB, 1 feature, CDFW CWHR ds589)
- `data/rana_boylii/rana_boylii_clades.geojson` (8,803 KB, 6 clades, CDFW ds2865)
- `data/rana_boylii/ca_ecoregions.geojson` (10,388 KB, 11 ecoregions, EPA ArcGIS REST)
- `data/rana_boylii/rana_boylii_occurrences.csv` (518 KB, 6,253 GBIF points)

Map styling: positron tile, range=#22c55e fill (0.25 opacity), clade dashed outlines by ESA status (Endangered=rose/orange, Threatened=amber/ocean, Not Listed=moss/purple). GBIF as HeatMap (avoids point_to_layer serialization error). `simplify(0.005)` on range/clades/ecoregions. Static map in EPSG:3310 (CA Albers).

ESA DPS mapping: South Coast=Endangered, South Sierra=Endangered, North Feather=Threatened, Central CA Coast=Threatened, Northwest/Northeast=Not Listed.

Key bug fix: `point_to_layer` lambda in `folium.GeoJson` causes `TypeError: Object of type function is not JSON serializable` — replaced with `HeatMap` from `folium.plugins`.

## Next Session Plan
- Add site photos to CriticalMineralsSites.json
- Add POI photos and expand narrative sections in roman-roads.qmd
- Further map styling refinements as needed
- Optimize Everglades coastline rendering (simplify geometry, filter to extent)
- Set up git repo and .gitignore
- Create Substack article for Rana boylii (SubstackRanaBoylii.md)
- Consider adding watershed layer (HUC-8) to rana-boylii.qmd
