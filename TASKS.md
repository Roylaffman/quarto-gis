# Task Tracker

## Completed
- [x] Scaffold project structure (research + docs)
- [x] Create `_quarto.yml` for research (Cosmo theme, code-fold, embed-resources)
- [x] Create `_quarto.yml` for docs website (navbar, footer)
- [x] Create `_brand.yml` with color palette and typography
- [x] Create `theme.scss` for both research and docs
- [x] Create `requirements.txt` with core Python GIS deps
- [x] Create analysis template (`analysis-template.qmd`)
- [x] Create report template (`report-template.qmd`)
- [x] Create reusable inserts: map-block, figure-callout, methods-block
- [x] Create docs site pages: index, setup guide, gis-visuals guide, publishing guide
- [x] Create `_metadata.yml` for analysis and reports folders
- [x] Create `CLAUDE.md` + `TASKS.md` for persistent context
- [x] Add `psycopg2-binary` and `python-dotenv` to requirements.txt
- [x] Create `.env.example` and `.env` with real credentials
- [x] Create `db_connection.py` — shared PostGIS connection module
- [x] Create `map_builder.py` — shared Folium map builder
- [x] Update both templates to use shared modules
- [x] Create comprehensive workflow guide (`docs/guides/workflow.qmd`)
- [x] Fix `load_costline.py` — password, table/column names, NUMERIC overflow
- [x] Load 1978 FL coastline data (5,689 features, SRID 4269)
- [x] Verify PostGIS 3.5.2 on PostgreSQL 17
- [x] Install missing Python packages globally (folium, plotly, python-dotenv, jupyter-cache, ipykernel)
- [x] Fix `theme.scss` — add SCSS layer markers (`/*-- scss:defaults --*/`, `/*-- scss:rules --*/`)
- [x] Comment out missing lightbox filter in `_quarto.yml`
- [x] Create `everglades-historical.qmd` — first real analysis with all three PostGIS layers
- [x] Successfully render full pipeline: PostGIS → psycopg2 → GeoDataFrame → Folium → Quarto HTML (37 MB standalone)
- [x] Write `Users Guide and Implementation.md` — comprehensive documentation (17 sections)
- [x] Add satellite imagery tile (`Esri.WorldImagery`) to `map_builder.py` TILES dict
- [x] Restructure `everglades-historical.qmd` — narrative story map with 10 sections
- [x] Add "The Outlaw Coast" intro narrative (rum-runners → saltwater cowboys → Square Grouper)
- [x] Add "The Smuggler's Highway" routes narrative (Barron, Chatham, Lopez, Wilderness Waterway)
- [x] Rename Sites section to "Points of Interest" — drop significance_level, widen description column
- [x] Switch interactive map to satellite imagery base tile with contrast-optimized colors
- [x] Widen popup boxes (max_width=450, min-width:280px div wrapper)
- [x] Filter CARTOGRAPHIC LIMIT from coastline static map legend
- [x] Add "Documentation & Source Data" section with all 4 route citations + video reference
- [x] Move technical details (Environment, Feature Breakdown, Notes) to bottom appendix
- [x] Render restructured Everglades document — all 9 cells pass, HTML output verified
- [x] Install `requests`, `sqlalchemy`, `geoalchemy2` — add to requirements.txt
- [x] Download Itiner-e bulk data — 16,554 segments + 11,847 places (39 MB NDJSON)
- [x] Load Roman road data into PostGIS (`roman_road_segments`, `roman_road_places`)
- [x] Add `build_photo_popup()` to `map_builder.py` — HTML popups with optional `<img>` + `onerror` handler
- [x] Create `roman-roads-poi.json` — seed file with 3 starter POIs (Via Appia, Pont du Gard, Porta Nigra)
- [x] Create `roman-roads.qmd` — 9-section story map with bounding box filter, road type styling, photo popups
- [x] Optimize Roman roads render — `ST_Simplify`, GeoJSON layers for places, aggregated timeline chart
- [x] Render `roman-roads.qmd` — all 12 cells pass, HTML output verified
- [x] Create `CriticalMineralsSites.json` — 17 curated mining sites (lithium, REE, strategic metals) across 7 countries
- [x] Create `critical-minerals.qmd` — 10-section story map (JSON-only, no PostGIS dependency)
- [x] Render `critical-minerals.qmd` — all 10 cells pass, 22 MB standalone HTML output verified
- [x] Create `SubstackCriticalMinerals.md` — Substack article draft with image placeholders
- [x] Create `CriticalMineralsSourceGuide.md` — source quality guide with 7 tiers + full bibliography
- [x] Create `export_critical_minerals_images.py` — exports 3 static PNGs (static-overview, lithium-production, ree-dominance)
- [x] Create `download_rana_boylii_data.py` — harvester for 5 GIS layers (CA boundary, CDFW range/clades, EPA ecoregions, GBIF)
- [x] Download all Rana boylii data (california.geojson 85KB, range 9.9MB, clades 8.8MB, ecoregions 10.4MB, occurrences 518KB / 6,253 pts)
- [x] Create `rana-boylii.qmd` — 10-section story map (Foothill Yellow-legged Frog, California)
- [x] Render `rana-boylii.qmd` — all 10 cells pass, standalone HTML output verified

## Database State (everglades_gis)
| Table | Type | SRID | Rows |
|---|---|---|---|
| `1978_fl_coastline` | MULTILINESTRING | 4269 | 5,689 |
| `historical_routes` | LINESTRING | 4326 | 4 |
| `historical_sites` | POINT | 4326 | 20 |
| `roman_road_segments` | LINESTRING | 4326 | 16,554 |
| `roman_road_places` | POINT | 4326 | 11,847 |

## In Progress
- [ ] Add POI photos and descriptions to `roman-roads-poi.json` (Ryan gathering data)
- [ ] Expand narrative sections in `roman-roads.qmd` (commented-out TODO sections ready for content)

## Backlog
- [ ] Add site photos to `CriticalMineralsSites.json` (photo_url, photo_caption)
- [ ] Set up git repo and `.gitignore` (exclude .venv, .env, _output, _site, data/)
- [ ] Optimize Everglades coastline rendering (simplify geometry, filter to extent)
- [ ] Publish docs site (GitHub Pages or other host)
- [ ] Regional detail maps for Roman roads (Italy, Gaul, Iberia)
- [ ] Add certainty breakdown section to Roman roads (currently commented out)
