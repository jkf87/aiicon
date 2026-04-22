# AAICon template structure

File: `assets/aaicon_template.docx` (`abstract_template_ver.260315`).

## Body order (top-to-bottom)

| Index | Kind | Role |
|---|---|---|
| P0 | paragraph | **Banner image** (AAICon logo). Do not touch. |
| P1 | paragraph | Empty spacer. Do not touch. |
| TABLE 0 | 4×1 table | **Title + author block** (edited by this skill). |
| P2 | paragraph | Empty spacer. |
| P3 | paragraph | `"요   약"` heading. The builder treats its next-following paragraphs (up to TABLE 1) as the replaceable body. |
| P4… | paragraphs | Placeholder abstract body — replaced. |
| TABLE 1 | 2×1 table | **Figure + caption**. Row 0 = image cell, Row 1 = caption. |
| P… | paragraphs | Trailing empties. |
| TABLE 2 | 2×5 table | **Guidelines** — removed by default (`remove_guidelines: true`). |
| P_last | paragraph | Final empty. |

## Title table (TABLE 0) cell mapping

| Row | Content written by the builder |
|---|---|
| 0 | `[{tag}]` on line 1, then Korean title lines (16 pt bold). |
| 1 | Korean author info. Typical list: `["홍길동†*1", "1Affiliation", "email1, email2"]`. |
| 2 | English title lines (14 pt). |
| 3 | English author info. |

## Figure table (TABLE 1)

- Row 0, cell 0 — cleared, then `add_picture(image_path, width=Mm(width_mm))`.
- Row 1, cell 0 — cleared, then `"{caption_label} "` (bold) + caption text.

## Fonts

The builder sets run-level `rFonts` on every inserted run so that text
renders as Malgun Gothic (ASCII) + 맑은 고딕 (East Asian). The Normal
style in the template already targets these — the explicit per-run
setting is defensive for tables where style inheritance is weaker.

## Page setup (present in the template, not re-applied)

- A4 portrait.
- Margins: top 40 mm, bottom 20 mm, left 10 mm, right 10 mm.
- 1 page constraint is a submission rule, not a Word setting —
  `render_preview.py` enforces it via `pdfinfo`.
