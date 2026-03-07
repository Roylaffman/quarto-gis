# Quarto GIS Workflow Transfer Guide
**Author:** Ryan Lafferty
**Source project:** quarto-gis
**Purpose:** Transferable patterns, pipeline steps, and lessons for new Claude Code sessions

## What This Project Proved

A single Claude Code project can own the full publishing pipeline: raw data in PostGIS or JSON, Python analysis, interactive maps in Folium, Quarto HTML output, Substack article drafts, and GCS static hosting. Each stage is automated or reduced to a single slash command. The patterns below transfer directly to any data-driven publishing workflow.

## Core Pipeline (QuartotoSS)

```
Data source (PostGIS / JSON / CSV / GIS files)
  → Python/GeoPandas analysis
  → Folium interactive map + Plotly/matplotlib charts
  → Quarto .qmd document (HTML-first, embed-resources: true)
  → export_*.py script → static PNGs to Google Drive images folder
  → Substack{Title}.md article draft
  → GCS bucket (gsutil cp)
```

Each story map follows the same 10-section structure: intro narrative, data table, thematic narrative, analysis/charts, interactive map, static overview map, secondary chart, data sources, bibliography, technical appendix.

## Slash Commands (`.claude/commands/`)

These live in `.claude/commands/` and are invoked as `/command-name [args]`. Create these for any workflow you repeat more than twice.

| Command | What it does |
|---|---|
| `/quarto-to-ss <slug>` | Reads QMD, runs export script, checks Drive images, writes Substack draft, updates index |
| `/fix-writing <file>` | Removes em dashes from narrative prose in one file with intelligent rewrites |
| `/fix-writing-all` | Batch: edits all Substack templates + QMDs, re-renders, uploads to GCS |

**Command file structure (`.claude/commands/command-name.md`):**
```markdown
# Command Name — Short description

**Usage:** `/command-name $ARGUMENTS`

## Step 1 — [action]
[instructions referencing $ARGUMENTS]

## Step 2 — [action]
...

## Final report
Print a completion summary with counts/status.
```

The command file is a prompt. Claude executes it literally when the slash command is invoked. `$ARGUMENTS` receives whatever the user typed after the command name.

## Pre-Generate Pattern (Critical for Quarto)

Never put live network calls or heavy compute inside a QMD cell that runs at render time. Instead:

1. Create a standalone `generate_*.py` script that runs once, saves output to `_export_images/`
2. QMD cell just loads the saved PNG: `img = mpimg.imread("_export_images/output.png")`
3. Zero network calls at render time, deterministic output, fast renders

**Applies to:** OSM/Overpass fetches (osmnx), API calls, anything taking more than 5 seconds.

**osmnx-specific:** Always set `ox.settings.overpass_rate_limit = False` in standalone scripts. Default `True` hangs indefinitely in Jupyter/Quarto kernels. Also use `matplotlib.use("Agg")` at the top of any standalone matplotlib script.

## Export Script Pattern

Every story map gets an `export_{slug}_images.py` in `research/analysis/`:

```python
OUT = "_export_images"
DRIVE = r"G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\images\{slug}"

def save(local_path):
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(local_path, dpi=150, bbox_inches="tight")        # matplotlib
    pio.write_image(fig, local_path, scale=2)                    # plotly
    if os.path.exists(r"G:\My Drive"):
        shutil.copy2(local_path, os.path.join(DRIVE, os.path.basename(local_path)))
```

Folium interactive maps can never be exported by script. Always flag them as `SCREENSHOT NEEDED` in the Substack template image table. Manual step: open HTML in browser, screenshot, save as `interactive-map.png`.

## Agent Delegation Rules

Use `Agent(subagent_type="general-purpose")` for:
- Writing tasks on individual files (em dash removal, prose rewriting, article drafts)
- File audits across many paths (count em dashes, check authorship, verify structure)
- Any task where you want to protect the main context window from large file reads

Use parallel agents when: tasks touch different files with no dependencies (e.g., editing 5 Substack templates simultaneously).

Never run parallel agents that write to the same file or the same output directory (Quarto _freeze conflicts).

**Agent prompt template for writing tasks:**
```
You are editing [file path] to [goal].

SKIP RULES (never modify these):
- [list exact skip conditions]

EDIT THESE:
- [list what to change]

REWRITING RULES:
- [specific patterns with before/after examples]

Read the file, make all edits, write it back, report counts.
```

## Substack Article Structure

Every article lives at `G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\Substack{PascalCaseTitle}.md`

```
YAML frontmatter (tags, date, status, source)
## Hook          — 2-3 sentences, concrete image or fact
## Body
### [Section 1]  — narrative + image embed ![[images/{slug}/name.png]]
### [Section 2]
### [Section 3]
## Takeaway      — precise conclusion
## Call to Action — subscribe + topic-specific hook
## Notes to Self — private: tone, audience, length, image table, sources
```

**Image table in Notes to Self:**
```markdown
| Description | File | Status |
|---|---|---|
| Static map | images/{slug}/map.png | EXPORTED |
| Chart | images/{slug}/chart.png | EXPORTED |
| Interactive | images/{slug}/interactive-map.png | SCREENSHOT NEEDED |
```

## Writing Rules (Enforce in All Content)

These apply to every QMD narrative section and every Substack article. Enforce them with `/fix-writing`.

- No em dashes (—). Use commas, colons, semicolons, or split into two sentences.
- Sentences under 20 words where possible.
- No sentence starting with "I".
- Precise nouns. "The Dadu River" not "the nearby river".
- No vague language: not "interesting", "significant", "important".
- First paragraph: vivid concrete image or surprising fact, not context-setting.

**Em dash skip rules (what NOT to edit):**
- YAML frontmatter (title, subtitle, author)
- Fenced code blocks (```python ... ```)
- Python print() strings and f-string literals
- HTML comment blocks
- BibTeX entries and citation labels

## GCS Publish Pattern

```bash
# Single file
gsutil cp research/_output/analysis/{slug}.html gs://www.geoglypha1.org/{slug}.html

# Batch (all story maps)
for slug in rana-boylii stone-towers roman-roads everglades-historical critical-minerals; do
  gsutil cp research/_output/analysis/$slug.html gs://www.geoglypha1.org/$slug.html
done
```

All 5 story maps live at `gs://www.geoglypha1.org/{slug}.html`. Cache is public-read. No CDN needed for this scale. Uploads take 30-90 seconds per file (file sizes range 17-38 MB due to `embed-resources: true`).

## Cross-Session Memory System

Two files keep Claude oriented across sessions:

- **`CLAUDE.md`** (project root, committed): full project context. Pipeline, file layout, DB tables, key patterns, document structures for each story map. Update it when a new story map is built or a key pattern changes.
- **`MEMORY.md`** (`~/.claude/projects/{hash}/memory/MEMORY.md`): Claude's auto-memory. Lessons, bugs fixed, session history. Auto-loaded into every session.

At the start of any new session, read both files before doing anything else.

## Quarto-Specific Lessons

| Problem | Root cause | Fix |
|---|---|---|
| Quarto render hangs forever | Live network call inside a kernel cell | Pre-generate via standalone script |
| "Maximum call stack exceeded" in browser | 10K+ individual Folium markers | Use `folium.GeoJson()` layer instead |
| `TypeError: function is not JSON serializable` | `point_to_layer` lambda in `folium.GeoJson` | Use `folium.plugins.HeatMap` for point density |
| TOC covers content | `toc-location: left` + `citation-location: margin` + `page-layout: full` together | Use `toc-location: right`, drop margin citations |
| Theme not applied | `theme: [cosmo, custom.scss]` drops project theme.scss | `theme: [cosmo, ../theme.scss, custom.scss]` |
| SCSS fails to compile | Missing layer markers | File must start with `/*-- scss:defaults --*/` |
| CDFW data is FileGDB in ZIP | Not a shapefile | Download bytes → save ZIP → extract → `gpd.read_file(gdb_path)` |
| osmnx highway column filter fails | Highway values can be lists | Use `.astype(str).str.contains(hw_type)` not lambda |

## Folium Map Conventions

```python
# Standard tile options
"positron"     # CARTO light (default, clean)
"dark"         # CARTO dark matter
"osm"          # OpenStreetMap
"satellite"    # Esri.WorldImagery
"relief"       # Esri.WorldShadedRelief (mountain context)

# Always set explicit iframe size
fig = folium.Figure(width="100%", height="650px")
m = folium.Map()
fig.add_child(m)

# MiniMap: pass TileLayer object, not URL string
_mini = folium.TileLayer(tiles=url, attr="Esri", name="mini")
MiniMap(tile_layer=_mini).add_to(m)

# Geometry simplification for performance
gdf["geometry"] = gdf["geometry"].simplify(0.005)   # GeoPandas (no PostGIS)
ST_Simplify(geometry, 0.005)                         # PostGIS
```

## .env Structure

Every project using this pipeline should have `research/.env` with these sections:

```
# PostGIS
PG_HOST=localhost
PG_PORT=5432
PG_DBNAME=your_database
PG_USER=your_username
PG_PASSWORD=your_password

# GCS
GCS_BUCKET=gs://your-bucket-name

# Project paths
PROJECT_DIR=
ANALYSIS_DIR=
OUTPUT_DIR=

# Obsidian / Substack paths
OBSIDIAN_DIR=
SUBSTACK_DIR=
SUBSTACK_IMAGES_DIR=
```

Load in Python scripts with `python-dotenv`: `from dotenv import load_dotenv; load_dotenv()`.

## What to Do First in a New Session

1. Read `CLAUDE.md` (project context)
2. Read `MEMORY.md` (lessons from previous sessions)
3. Check `TASKS.md` if it exists (task tracker)
4. Ask: does the project have a `.claude/commands/` folder? If yes, list what commands are available.
5. Ask: does the project have `research/.env`? If yes, check what path variables are set.

## Transferable to Any Data Publishing Project

The core loop works for any subject:

```
Authoritative data source
  → Python cleaning + analysis
  → Folium/Plotly/matplotlib visualization
  → Quarto HTML document (narrative structure)
  → export_*.py → static images → Drive folder
  → Article draft (Substack, Medium, newsletter)
  → GCS / S3 / Netlify static host
```

Replace PostGIS with SQLite, DuckDB, or flat files. Replace Folium with Leaflet.js or deck.gl. Replace Substack with Ghost or Beehiiv. The slash commands and agent patterns work the same way regardless of stack.
