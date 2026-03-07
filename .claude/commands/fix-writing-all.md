# fix-writing-all — Full Em Dash Removal + Publish Pipeline

Remove all em dashes from narrative prose across all Substack templates and QMD story maps, re-render the QMDs, and upload to GCS.

**Usage:** `/fix-writing-all`

No arguments needed. Runs all five phases in order.

---

## Skip Rules (apply to every file, every phase)

NEVER edit lines that are:
- Inside a fenced code block (` ```python ` through closing ` ``` `)
- Python `print()` statements
- Python f-string literals
- HTML comment blocks `<!-- ... -->`
- YAML frontmatter (between opening `---` and closing `---`)
- BibTeX / citation entries

DO edit:
- All narrative markdown prose paragraphs
- Markdown section headings containing em dashes
- Markdown table cells containing prose
- Notes to Self citation list annotations (convert ` — ` to `: `)

## Rewriting Patterns

| Pattern | Replacement |
|---|---|
| `X — the Y — does Z` | `X, the Y, does Z` |
| `X — and Y follows` | Period + new sentence |
| `Name — description` | `Name: description` |
| `not X — it's Y` | Two sentences: "It is not X. It is Y." |
| Long clause with interior em dash | Restructure or split at the dash |

Additional rules: no new em dashes, sentences under 20 words where possible, no sentence starting with "I", precise nouns.

---

## Phase 1: Substack Templates

Process these five files in order. For each: read → rewrite narrative em dashes → write → print count.

1. `G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\SubstackLithiumAnalysis.md`
2. `G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\SubstackRanaBoylii.md`
3. `G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\SubstackEvergladesOutlawCoast.md`
4. `G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\SubstackRomanRoads.md`
5. `G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\SubstackStoneTowers.md`

---

## Phase 2: QMD Narrative Sections

Process these five files in order. Apply skip rules strictly — code blocks are large in QMD files.

1. `research/analysis/rana-boylii.qmd`
2. `research/analysis/stone-towers.qmd`
3. `research/analysis/critical-minerals.qmd`
4. `research/analysis/everglades-historical.qmd`
5. `research/analysis/roman-roads.qmd`

---

## Phase 3: Render QMDs

Run sequentially. Report pass/fail for each.

```bash
cd research && quarto render analysis/rana-boylii.qmd
cd research && quarto render analysis/stone-towers.qmd
cd research && quarto render analysis/roman-roads.qmd
cd research && quarto render analysis/everglades-historical.qmd
cd research && quarto render analysis/critical-minerals.qmd
```

---

## Phase 4: Upload to GCS

```bash
gsutil cp research/_output/analysis/rana-boylii.html gs://www.geoglypha1.org/rana-boylii.html
gsutil cp research/_output/analysis/stone-towers.html gs://www.geoglypha1.org/stone-towers.html
gsutil cp research/_output/analysis/roman-roads.html gs://www.geoglypha1.org/roman-roads.html
gsutil cp research/_output/analysis/everglades-historical.html gs://www.geoglypha1.org/everglades-historical.html
gsutil cp research/_output/analysis/critical-minerals.html gs://www.geoglypha1.org/critical-minerals.html
```

---

## Phase 5: Final Report

Print a summary table:

| File | Dashes removed | Dashes skipped (code) | Render | Upload |
|---|---|---|---|---|
| SubstackLithiumAnalysis.md | N | 0 | n/a | n/a |
| SubstackRanaBoylii.md | N | 0 | n/a | n/a |
| SubstackEvergladesOutlawCoast.md | N | 0 | n/a | n/a |
| SubstackRomanRoads.md | N | 0 | n/a | n/a |
| SubstackStoneTowers.md | N | 0 | n/a | n/a |
| rana-boylii.qmd | N | N | pass/fail | pass/fail |
| stone-towers.qmd | N | N | pass/fail | pass/fail |
| critical-minerals.qmd | N | N | pass/fail | pass/fail |
| everglades-historical.qmd | N | N | pass/fail | pass/fail |
| roman-roads.qmd | N | N | pass/fail | pass/fail |
