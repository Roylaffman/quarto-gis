# QuartotoSS — Quarto Story Map to Substack Pipeline

Convert a completed Quarto story map (.qmd) into a Substack article draft with accompanying images folder.

**Usage:** `/quarto-to-ss <slug>`

Example: `/quarto-to-ss stone-towers` or `/quarto-to-ss rana-boylii`

---

## Workflow

You are executing the QuartotoSS pipeline for the story map: **$ARGUMENTS**

Work through each step in order. Mark each complete before moving on.

### Step 1 — Locate and Read the QMD

1. Find `research/analysis/$ARGUMENTS.qmd` in the project
2. Read the full file to extract:
   - `title:` and `subtitle:` from YAML
   - All section headings and narrative text
   - Which charts/maps are generated (Plotly, matplotlib, Folium)
   - Any existing `bibliography:` entries to draw from
   - The overall argument/story arc

### Step 2 — Check Export Script Status

Check for `research/analysis/export_$ARGUMENTS_images.py`:

**If it exists:** Run it from `research/analysis/`:
```bash
cd research/analysis && python export_$ARGUMENTS_images.py
```
Confirm all PNGs landed in `research/analysis/_export_images/` and were copied to `G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\images\$ARGUMENTS\`

**If it does not exist:** Create it following the pattern from `export_stone_towers_images.py` or `export_rana_boylii_images.py`. The script must:
- Export all Plotly charts via `pio.write_image()` at scale=2
- Export all matplotlib maps via `fig.savefig()` at dpi=150
- Copy every PNG to `G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\images\$ARGUMENTS\`
- Print a summary of what was exported and what still needs a manual screenshot
- Note: never export the Folium interactive map — that always requires a manual screenshot

### Step 3 — Check Images Folder

Verify `G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\images\$ARGUMENTS\` exists and list the PNGs. Note which ones are present and which are still needed (especially `interactive-map.png` which is always manual).

### Step 4 — Check for Existing Substack Draft

Check `G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\Substack$ARGUMENTS_title.md` (PascalCase title, e.g., `SubstackStoneTowers.md`).

**If it exists:** Read it and report its current state. Note which image placeholders still say EXPORT NEEDED or SCREENSHOT NEEDED.

**If it does not exist:** Create it (see Step 5).

### Step 5 — Write the Substack Article Draft

Create `G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\Substack{PascalCaseTitle}.md` using this structure derived from the Substack Article template:

```markdown
---
tags:
  - substack
  - writing
  - gis
  - [topic tags from QMD]
date: YYYY-MM-DD
status: "[[Seed 3]]"
source: "[[{slug}.qmd]]"
---

## Hook
[2-3 sentences. Vivid, specific, no em dashes. Opens on a concrete image or surprising fact from the QMD.]

## Body

### [Section title drawn from QMD narrative]
[Prose adapted from QMD narrative sections. Target: ~200-250 words per section.]
[Image embed: ![[images/{slug}/image-name.png]]]
*Caption text.*

### [Next section]
...

## Takeaway
[What the reader walks away with. Specific conclusion, not generic.]

## Call to Action
[Subscribe prompt + specific engagement hook tied to this topic.]

## Notes to Self

**Tone**: [match to QMD subject matter]
**Audience**: [from QMD audience notes if available]
**Target length**: ~1,400 words, [N] images
**Publish date**: TBD
**Cross-post to**: geoglypha1.org

**Source Material**:
[List primary data sources from QMD bibliography section]

**Images / Media**:

| Description | File | Status |
|---|---|---|
[One row per image — mark EXPORTED or SCREENSHOT NEEDED]

**To export static images**: Run `python export_{slug}_images.py` from `research/analysis/`
**Interactive HTML location**: `research/_output/analysis/{slug}.html`
```

**Critical writing rules:**
- No em dashes (use commas, colons, or restructure the sentence)
- Short sentences (under 20 words preferred)
- Precise nouns — no vague language like "interesting" or "significant"
- First paragraph must not start with "I"
- Image embeds use Obsidian `![[]]` syntax

### Step 6 — Update Substack.md Index

Read `G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\Substack.md` and add the new article link under `## Drafts — YYYY` if not already present:

```markdown
[[Substack{PascalCaseTitle}]]
```

### Step 7 — Final Status Report

Print a completion summary:

```
QuartotoSS complete: {slug}

Images:
  [x] chart-name.png          — exported to Drive
  [x] map-name.png            — exported to Drive
  [ ] interactive-map.png     — MANUAL SCREENSHOT NEEDED

Substack draft:
  [x] Substack{Title}.md created/updated
  [x] Added to Substack.md index

Next step:
  Open research/_output/analysis/{slug}.html in browser
  Screenshot the Folium map
  Save to: G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\images\{slug}\interactive-map.png
```
