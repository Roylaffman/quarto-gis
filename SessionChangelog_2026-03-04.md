# Session Changelog
**Author:** Ryan Lafferty
**Date:** 2026-03-04
**Session:** Stone Towers + Rana boylii + Geoglypha updates

## Summary

This session built the Stone Towers of the Sino-Tibetan Borderlands story map from scratch, resolved a serious OSM network hang in the Quarto render pipeline, fixed a CSS and layout conflict, created the Substack article draft, uploaded Rana boylii content to Geoglypha, and corrected author attribution across the project.

## 1. New Files Created

### Stone Towers Story Map

| File | Description |
|---|---|
| `research/analysis/stone-towers.qmd` | 10-section story map with Folium regional map, Danba detail view, architecture narrative, chronology, and conservation section |
| `research/analysis/stone-towers.scss` | Earth-tone CSS overlay (burnt sienna, warm cream) layered on top of Cosmo + project theme.scss |
| `research/analysis/StoneTowerSites.json` | 7 curated tower cluster sites with coordinates, ethnic attribution, plan types, and conservation status |
| `research/analysis/generate_danba_map.py` | Standalone script to fetch OSM data via osmnx and render a Danba County map. Must be run separately before rendering the QMD |
| `research/analysis/export_stone_towers_images.py` | Exports Plotly plan-type chart + copies Danba PNG to Google Drive Substack images folder |
| `research/analysis/_export_images/danba-osmnx.png` | Pre-generated Danba County OSM map (64 KB) |
| `research/analysis/_export_images/stone-towers-plan-chart.png` | Tower plan type distribution bar chart (83 KB) |

### Substack Article

| File | Description |
|---|---|
| `G:/My Drive/02. Obsidian/Lafferty Cloud/Substack/SubstackStoneTowers.md` | Full Substack draft (~1,400 words, no em dashes, mystery/puzzle framing) |

### BibTeX Entries Added

12 new entries appended to `research/reports/references.bib`:

- darragon2003, li2009danba, wang2007qiang, theobald2013, tsomu2015, yin2006, kirby2003, freeman2015, yang2004, sun2009wenchuan, aldenderfer2004, wmf2006

## 2. Stone Towers Layout Fixes

The first render of stone-towers.qmd had a layout problem: the Table of Contents overlapped the main content column because three competing layout columns were active at once.

**Root cause:** `toc-location: left` combined with `citation-location: margin` and `page-layout: full` created three competing columns.

**Fix applied in stone-towers.qmd:**
- Changed `toc-location:` from `left` to `right`
- Removed `citation-location: margin` and `reference-location: margin`
- Changed `theme:` from `[cosmo, stone-towers.scss]` to `[cosmo, ../theme.scss, stone-towers.scss]` to correctly layer all three theme files

**Fix applied in stone-towers.scss:**
- Added explicit content padding: `#quarto-content #quarto-document-content { padding-right: 1.5rem; }`
- Added TOC link styling for right-column position
- Added `iframe.folium-map { height: 650px !important; }` to ensure the Folium map renders at full height

The interactive Folium map was also resized using `folium.Figure(width="100%", height="650px")`.

## 3. OSM / prettymaps Render Hang (Root Cause + Fix)

The original plan called for prettymaps to render an artistic local view of Danba County inside the QMD. This hung indefinitely during Quarto rendering.

**Root cause 1:** prettymaps 1.4.2 installed PySide6 (Qt) as a dependency. Even with `show=False`, the Qt display subsystem attempted to initialize in the Jupyter kernel, causing an indefinite hang.

**Root cause 2:** After switching to osmnx directly, the render still hung. The cause was `ox.settings.overpass_rate_limit = True` (the default). This makes osmnx query the Overpass API status endpoint between every request to avoid rate limits, but in Quarto's Jupyter kernel context the inter-request pause never resolves.

**Fix:** Pre-generate the Danba map via a standalone script (`generate_danba_map.py`) that runs outside the Quarto kernel:
- Set `ox.settings.overpass_rate_limit = False` and `ox.settings.requests_timeout = 60`
- Use `matplotlib.use("Agg")` before any matplotlib import (non-interactive backend)
- Filter highway types with vectorized `.astype(str).str.contains(hw_type)` instead of a lambda (which fails on list-valued osmnx highway columns)
- Save PNG to `_export_images/danba-osmnx.png`

The QMD cell for Section 6 now only loads the saved PNG with `mpimg.imread()` — zero network calls at render time.

## 4. Folium MiniMap Fix

The MiniMap plugin raised `ValueError: Custom tiles must have an attribution` when passed a raw tile URL string.

**Fix:** Pre-build a `folium.TileLayer` object and pass the object (not the URL string) to `MiniMap(tile_layer=...)`.

## 5. Rana Boylii — Geoglypha Upload

Three actions taken for the rana-boylii story map:

1. **Coordinates extracted** from `research/analysis/farm.geojson`: Lat **39.4384°N**, Lon **-121.3108°W** (Sierra Nevada foothills, Yuba/Nevada County border area)

2. **File uploads to GCS bucket** (`gs://www.geoglypha1.org/`):
   - `research/_output/analysis/rana-boylii.html` uploaded as `rana-boylii.html`
   - `C:/Users/royla/OneDrive/Documents/2.9Dev/Geoglypha/images/Rana Clade.jpg` uploaded as `Rana%20Clade.jpg`

3. **geography.html updated** with a new Rana boylii card:
   - Card image: `Rana Clade.jpg` from the GCS bucket
   - Badge: `Conservation GIS`
   - Link: `rana-boylii.html`
   - geography.html re-uploaded to GCS after edit

## 6. Author Attribution Fixes

"Nathan Askins" appeared incorrectly as the author in several project files. All instances replaced with "Ryan Lafferty":

| File | Location |
|---|---|
| `research/analysis/rana-boylii.qmd` | YAML frontmatter `author:` field |
| `research/analysis/rana-boylii.scss` | CSS header comment `* Author:` line |
| `ClaudeCode_TeamGuidance.md` | Document header `**Author:**` field (line 3) and authorship rule table (line 212) |
| `CodeConventions.json` | `authorship.rule` field |

**Note:** The rendered HTML cache files (`research/_output/analysis/rana-boylii.html` and `research/_freeze/analysis/rana-boylii/execute-results/html.json`) still contain the old name. These are overwritten automatically the next time `quarto render analysis/rana-boylii.qmd` is run.

## 7. Author Verification Across All Reports

All QMD story maps confirmed with correct author attribution after fixes:

| File | Author |
|---|---|
| `research/analysis/stone-towers.qmd` | Ryan Lafferty |
| `research/analysis/rana-boylii.qmd` | Ryan Lafferty (fixed this session) |
| `research/analysis/critical-minerals.qmd` | Ryan Lafferty |
| `research/analysis/everglades-historical.qmd` | Ryan Lafferty |
| `research/analysis/roman-roads.qmd` | Ryan Lafferty |
| `research/analysis/analysis-template.qmd` | Ryan Lafferty |
| `research/reports/report-template.qmd` | Ryan Lafferty |

## 8. Pending Items (Not Completed This Session)

| Item | Notes |
|---|---|
| Interactive map screenshot for SubstackStoneTowers.md | Manual screenshot of `stone-towers.html` Folium map needed. Save to `G:/My Drive/02. Obsidian/Lafferty Cloud/Substack/images/stone-towers/interactive-map.png` |
| Interactive map screenshot for SubstackRanaBoylii.md | Manual screenshot of `rana-boylii.html` Folium map needed |
| Re-render rana-boylii.qmd | Updates cached HTML with correct author name. Run: `cd research && quarto render analysis/rana-boylii.qmd` |
