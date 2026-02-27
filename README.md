# Quarto GIS Research Starter (HTML-first)

This starter kit gives you **Quarto templates** for:
- **Analysis** (exploratory notebooks, GIS EDA)
- **Reports** (client/leadership-ready)
- **Article Inserts** (drop-in modules you can include in other docs)
- **Documentation Site** (Quarto Website)

Everything is tuned for **HTML output** and GIS visualization workflows (GeoPandas → plots, Folium/Leaflet → interactive maps).

---

## 1) Install Quarto

### Option A — Quarto CLI (recommended)
1. Install Quarto: https://quarto.org/docs/get-started/
2. Verify:
   ```bash
   quarto --version
   ```

### Option B — VS Code / Positron
- Install the **Quarto** extension (VS Code) or use **Positron**.
- You can still render from the terminal.

---

## 2) Python environment (recommended baseline)

From the `research/` folder:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

If GeoPandas wheels are problematic on your machine, use **conda** instead:
```bash
conda create -n quarto-gis python=3.11 -y
conda activate quarto-gis
conda install -c conda-forge geopandas folium matplotlib pandas pyproj shapely fiona -y
pip install plotly
```

---

## 3) How to use the templates

### Render a single document
From `research/`:
```bash
quarto render analysis/analysis-template.qmd
quarto render reports/report-template.qmd
```

### Preview while editing
```bash
quarto preview analysis/analysis-template.qmd
```

### Export *standalone HTML* (no external assets)
Most templates set `embed-resources: true`.  
That produces a single self-contained HTML file you can email or archive.

---

## 4) Article inserts (partials)

Use the include shortcode:
```markdown
{{< include inserts/figure-callout.qmd >}}
```

This lets you keep reusable snippets (methods blocks, callouts, standardized figures)
and insert them into many reports.

---

## 5) Documentation site (Quarto Website)

From `docs/`:
```bash
quarto preview
# or build
quarto render
```

Output goes to `docs/_site/` by default.

---

## 6) Project layout

```
quarto-gis-starter/
  research/                 # analysis + reports (HTML-first)
    _quarto.yml
    _brand.yml              # reusable brand tokens (colors, fonts)
    theme.scss              # bootstrap theme overrides
    requirements.txt
    analysis/
      _metadata.yml         # defaults for this folder
      analysis-template.qmd
    reports/
      _metadata.yml
      report-template.qmd
      references.bib
    inserts/
      figure-callout.qmd
      methods-block.qmd
      map-block.qmd
  docs/                     # documentation website
    _quarto.yml
    _brand.yml
    theme.scss
    index.qmd
    guides/
      setup.qmd
      gis-visuals.qmd
      publishing.qmd
```

---

## 7) Recommended workflow

- Use **analysis** templates for exploration and prototyping.
- Promote stable outputs into the **report** template.
- Convert repeated text/figures into **inserts**.
- Document your conventions in the **docs** site so the workflow is repeatable.

---

## 8) Troubleshooting quick hits

- **Quarto can’t find Python**: set `QUARTO_PYTHON` environment variable or ensure your venv is active.
- **GeoPandas install issues**: prefer conda-forge install (see above).
- **Interactive maps blank**: ensure your HTML viewer allows external tiles, or use `embed-resources: true` and/or a different tile source.

