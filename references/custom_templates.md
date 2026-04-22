# Adapting to a non-AAICon template

The builder assumes a template shaped like this:

- **TABLE 0** — 4 rows × 1 col, each row is a cell rewritten in order:
  `[KO title, KO authors, EN title, EN authors]`.
- **A heading paragraph** containing the abstract label (default
  `"요   약"`), followed by placeholder body paragraphs that run until
  the next table.
- **A figure table** with at least 2 rows × 1 col (image row above
  caption row).
- **(Optional) a guidelines table** that gets removed when
  `remove_guidelines: true`.

## Verifying a candidate template

Run this one-liner (inside the project venv) and check the structure
matches the expected shape:

```bash
python3 -c "
from docx import Document
d = Document('path/to/template.docx')
for i,t in enumerate(d.tables):
    print(f'TABLE {i}: {len(t.rows)}x{len(t.columns)}')
    for ri,row in enumerate(t.rows):
        for ci,c in enumerate(row.cells):
            print(f'  [{ri},{ci}]', (c.text.strip()[:80]))
print('---')
for i,p in enumerate(d.paragraphs):
    if p.text.strip(): print(f'P{i}:', p.text.strip()[:80])
"
```

If the table indices differ, set these in the config:

```yaml
figure_table_index: 0        # whichever TABLE holds the image cell
guidelines_table_index: 3    # whichever TABLE (if any) is the guidelines grid
remove_guidelines: false     # if the template has no guidelines table
abstract_heading: "Abstract" # change to the exact heading text used
```

## When the shape does not match

If the template diverges significantly (e.g. title + authors live in
separate tables, or the figure is a floating shape rather than a table
cell), the builder will not produce correct output. Options:

1. **Adjust the template** to match the expected shape — usually the
   easiest path.
2. **Extend the builder** — add a new helper alongside
   `fill_figure_table()` that targets the different structure, and
   choose between code paths with a config flag.
