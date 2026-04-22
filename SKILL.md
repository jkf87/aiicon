---
name: aaicon
description: Fill a Korean-conference one-page abstract template (.docx) with title, authors, body text, and a figure. Use when the user asks to generate/build/fill/produce/edit an 학회 abstract, 초록, AAICon, AI Friends Conference, 에이아이프렌즈 abstract, or any one-page Korean academic abstract that needs a .docx output with an embedded figure. The skill bundles the AAICon 2026 template and a builder script; it supports custom templates that follow the same 4-row title table + figure table structure. Output is a filled .docx plus an optional PDF preview checked for the 1-page constraint.
---

# Conference Abstract (DOCX) Builder

Fills a template .docx for 1-page Korean-conference abstracts (default:
AAICon 2026). Inputs come from a YAML config; output is a .docx plus an
optional PDF preview. Preserves the template's banner image, fonts, and
layout — only content cells are rewritten.

## Concrete workflow

1. **Gather inputs.** From the user, confirm:
   - tag: `구두` (oral) or `포스터` (poster)
   - Korean + English titles
   - Korean + English author lines (name, affiliation, email)
   - Abstract body text (Korean-mixed OK)
   - Figure image path (PNG/JPEG) + caption

2. **Build a config file.** Copy `references/example_config.yaml` to the
   project folder and edit. Inline markup inside body/caption: use
   `[b]…[/b]` for bold, `[url=https://…]anchor[/url]` for hyperlinks.

3. **Run the builder.** From a Python env with `python-docx` and
   `pyyaml` installed (project venv, not a system Python that may lack
   those packages):
   ```bash
   python scripts/build_abstract.py --config CONFIG.yaml --out OUT.docx
   # Custom template:
   python scripts/build_abstract.py --config CONFIG.yaml --out OUT.docx --template /path/to/other_template.docx
   ```

4. **Render preview + page check.**
   ```bash
   python scripts/render_preview.py OUT.docx --png
   ```
   Exits with code 2 and prints a warning if the PDF exceeds one page.

5. **Fit to one page if needed.** See `references/one_page_fit.md` for
   the in-order levers (body length → figure width → line spacing →
   caption length). Re-render and re-check after each change.

## Inputs and structure

- **Config schema** and the complete field reference: `references/config_schema.md`
- **Example config** (AAICon Paper Loop abstract): `references/example_config.yaml`
- **How the AAICon template is laid out** (table indices, cell roles, what to avoid touching): `references/template_structure.md`
- **Adapting to non-AAICon templates**: `references/custom_templates.md` — covers the required structural invariants (4-row title table + 2-row figure table + "요 약" heading) and how to verify a candidate template.
- **One-page fit strategy**: `references/one_page_fit.md`.
- **Auto-generating the figure via Codex CLI**: `references/figure_generation.md` — ports the flow from [openclaw-codex-image-gen](https://github.com/jkf87/openclaw-codex-image-gen). Add a `figure.generate` block to the YAML to produce the PNG in-line; no pre-made image required.

## Bundled assets

- `assets/aaicon_template.docx` — AAICon 2026 official template, used by
  default when `--template` is not passed.
- `assets/example_figure.jpeg` — Paper Loop unified figure, useful as a
  smoke-test image.

## Requirements

- Python 3.10+ with `python-docx` and `pyyaml` importable
  (`pip install python-docx pyyaml`).
- LibreOffice (`soffice`) for the PDF preview step. Optional:
  `pdftoppm` for PNG rendering and `pdfinfo` for page-count verification.
- Korean fonts (맑은 고딕 / Malgun Gothic) installed on the rendering
  machine. Without them LibreOffice will substitute; the .docx itself
  still embeds the correct font *names*.

## Typical pitfalls

- **Output lands on 2 pages.** Cut body word count first (it dominates);
  drop figure width in 5–10 mm steps; only then reduce body line spacing
  below 1.0. Do not touch the banner or top margin.
- **Bold markup leaks.** Only `[b]…[/b]` and `[url=…]…[/url]` are parsed.
  Do not nest tags.
- **Banner disappears.** The banner is part of the first body paragraph
  (P0) of the template. The script never touches P0/P1 — keep the
  original template file untouched in `assets/`.
- **Wrong table picked.** If a custom template orders its figure /
  guidelines tables differently, set `figure_table_index` and
  `guidelines_table_index` in the config (see config_schema.md).
