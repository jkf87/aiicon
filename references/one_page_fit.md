# One-page fit strategy

AAICon submissions must be exactly one A4 page. Apply levers in this
order — each subsequent lever costs more readability than the last.

1. **Trim body length.** Body dominates vertical space.
   - Collapse redundant clauses; merge adjacent sentences.
   - Consolidate multiple short blocks into a single paragraph.

2. **Reduce figure width.** Drop `figure.width_mm` in 5–10 mm
   increments (140 → 130 → 120 …). Below 90 mm, legibility drops.

3. **Shorten the caption.** Remove sub-label descriptions that are
   already explained in the body. Prefer one sentence.

4. **Tighten line spacing.** `body_line_spacing: 1.0` → `0.95`.
   Values below 0.9 cause visible crowding for Korean glyphs.

5. **Reduce first-line indent.** `first_line_indent_mm: 4` → `0`
   reclaims ~1 line at a small cost in visual rhythm.

6. **Last resort — body font size.** AAICon requires ≥9 pt. Only drop
   below if a submission portal explicitly allows it (most do not).

## Do not

- Touch the page margins — they are a submission rule.
- Remove or shrink the banner image (P0).
- Add extra blank paragraphs between title and body.
- Stretch the figure beyond 160 mm (exceeds text block width).

## Verification loop

```bash
python scripts/build_abstract.py --config config.yaml --out out.docx
python scripts/render_preview.py out.docx --png
# If exit code 2 (>1 page), apply next lever and repeat.
```
