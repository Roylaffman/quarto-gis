# fix-writing — Remove Em Dashes from a Single File

Edit one file to remove all em dashes from narrative prose, replacing each with better sentence structure.

**Usage:** `/fix-writing <absolute file path>`

Example: `/fix-writing G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\SubstackRanaBoylii.md`

---

## Instructions

You are editing the file at: **$ARGUMENTS**

### Step 1 — Read the file

Read the complete file. Count every em dash character "—" (U+2014).

### Step 2 — Apply skip rules

Do NOT change any line that is:
- Inside a fenced code block (` ```python ` through closing ` ``` `)
- A Python `print()` statement
- Inside a Python f-string literal
- Inside an HTML comment block `<!-- ... -->`
- Inside YAML frontmatter (between the opening `---` and closing `---`)
- A BibTeX entry

DO change:
- All narrative markdown prose paragraphs
- Markdown table cells containing prose
- Notes to Self citation list annotations (convert ` — ` to `: `)

### Step 3 — Rewrite each em dash

For each em dash found in editable text, choose the best replacement:

| Pattern | Replace with |
|---|---|
| `X — the Y — does Z` (parenthetical) | `X, the Y, does Z` |
| `X — and Y follows` (trailing thought) | Period. New sentence starting with Y. |
| `Name — description` (list annotation) | `Name: description` |
| `not X — it's Y` (contrast) | `It is not X. It is Y.` |
| `X — Y — Z` (two parentheticals) | Restructure into two sentences or use commas |

Additional rules:
- No sentence should start with "I"
- Keep sentences under 20 words where possible
- Use precise nouns, not vague language
- No new em dashes introduced anywhere

### Step 4 — Write the file back

Write the edited content to the same file path.

### Step 5 — Report

Print:
- Em dashes found in narrative: N
- Em dashes replaced: N
- Em dashes skipped (in code/YAML): N
- Any lines where restructuring changed meaning (flag for review)
