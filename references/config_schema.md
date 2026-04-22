# Config schema

YAML fields consumed by `scripts/build_abstract.py`.

## Required

| Field | Type | Notes |
|---|---|---|
| `title_ko` | string | Korean title. Use `\n` for a manual line break. |
| `title_en` | string | English title. `\n` allowed. |
| `authors_ko` | list[str] | One entry per line in the KO author cell. Typically 3 lines: names+symbols, affiliation, emails. |
| `authors_en` | list[str] | English counterpart. Usually 2 lines (names, affiliation). |
| `body` | list[str] OR string | Each list entry becomes one paragraph. A string is treated as a single paragraph. |

## Optional

| Field | Default | Notes |
|---|---|---|
| `tag` | `"구두"` | `"구두"` (oral) or `"포스터"` (poster). Goes inside `[ ]` on the first line. |
| `abstract_heading` | `"요   약"` | Substring used to find the heading paragraph whose following body is replaced. |
| `body_size_pt` | `9` | Body font size. |
| `body_line_spacing` | `1.0` | Line spacing multiplier. Lower to fit one page. |
| `first_line_indent_mm` | `4` | First-line indent for each body paragraph. Set to `0` for no indent. |
| `justify` | `true` | Justify body paragraphs. |
| `figure` | — | Optional sub-object (see below). |
| `figure_table_index` | `1` | Zero-based index of the figure table. `1` for AAICon. |
| `remove_guidelines` | `true` | Drop the guidelines table from the template. |
| `guidelines_table_index` | `2` | Zero-based index of the guidelines table. `2` for AAICon. |

## `figure` sub-object

| Field | Default | Notes |
|---|---|---|
| `image` | required* | Path to a PNG/JPEG. `~` expansion is supported. *Optional if `generate` is set.* |
| `caption` | required | Caption text. Inline `[b]` markup allowed. |
| `width_mm` | `140` | Image width. Typical range 120–160 mm for AAICon. |
| `caption_size_pt` | `8` | Caption font size. |
| `caption_label` | `"그림 1."` | Bold label prefixed to caption. Set to `""` to omit. |
| `generate` | — | Optional sub-object (below). Auto-generates the image via Codex if `image` is missing. |

### `figure.generate` sub-object (optional)

Triggers `scripts/generate_figure.py` and caches the resulting PNG. See
`figure_generation.md` for details.

| Field | Default | Notes |
|---|---|---|
| `prompt` | required | Image prompt. Spell out labels, style, language explicitly. |
| `aspect` | `"landscape"` | `square` / `landscape` / `portrait`. |
| `background` | `"auto"` | `auto` / `opaque` / `transparent`. |
| `file_name` | `<out-stem>_figure.png` | Cache filename. |
| `output_dir` | `<config_dir>/generated` | Cache dir. Relative paths resolve against the config file. |
| `force` | `false` | Regenerate even if the cached file exists. |
| `timeout_seconds` | `180` | Subprocess timeout for `codex responses`. |
| `codex` | auto-detect | Explicit path to the `codex` binary. |

## Inline markup

Usable in `body`, author lines, captions, and title strings:

- `[b]text[/b]` — bold span.
- `[url=https://example.com]anchor[/url]` — clickable hyperlink (blue, underlined).

Markup tokens are not nested. Do not put `[b]` or `[url=...]` sequences
inside each other.

## Minimal example

```yaml
tag: 구두
title_ko: 예시 제목
title_en: An Example Title
authors_ko:
  - "홍길동*†1"
  - "1소속기관"
  - "hong@example.com"
authors_en:
  - "Gildong Hong*†1"
  - "1Affiliation"
body:
  - |
    개인 연구자의 병목은 [b]역할 전환 비용[/b]이다.
    (이하 생략)
figure:
  image: ./fig.png
  caption: "실험 결과 요약."
  width_mm: 130
```

Run with:

```bash
python scripts/build_abstract.py --config config.yaml --out abstract.docx
```
