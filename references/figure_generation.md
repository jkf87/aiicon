# Figure generation via Codex CLI

The skill can auto-generate the abstract's figure by calling the OpenAI
Codex CLI's `image_generation` tool — no pre-made image required. This
ports the working flow from
[`openclaw-codex-image-gen`](https://github.com/jkf87/openclaw-codex-image-gen)
into a standalone Python script so you do not need OpenClaw installed.

## Prerequisites

- `codex` CLI installed and logged in:
  ```bash
  codex login status   # expect: "Logged in using ChatGPT"
  ```
- A Codex version that supports `codex responses`. If `codex responses`
  prints "unknown command", you have an older binary — prefer the
  user-installed one (`~/.npm-global/bin/codex`) over `/usr/local/bin/codex`.

The skill's `scripts/generate_figure.py` tries these binaries in order:

1. `~/.npm-global/bin/codex`
2. `/usr/local/bin/codex`
3. `/opt/homebrew/bin/codex`
4. `which codex`
5. `--codex /explicit/path` (overrides all of the above)

## How it works

```
prompt → JSON payload → `codex -c mcp_servers={} responses` (stdin)
       → JSONL stream on stdout
       → pluck `response.output_item.done` + `image_generation_call`
       → base64-decode `result`
       → PNG on disk
```

Model is hardcoded to `gpt-5.4`, quality to `high`. Aspect ratios:
`square` → 1024×1024, `landscape` → 1536×1024, `portrait` → 1024×1536.
MCP servers are disabled for the subprocess (`-c mcp_servers={}`) to
avoid inherited config incompatibilities.

Streamed Codex events and stderr land in a sibling
`<figure-stem>.codex_logs/` directory — inspect
`codex.responses.jsonl` when extraction fails.

## Option A — standalone invocation

Use directly, independent of the abstract builder:

```bash
python scripts/generate_figure.py \
  --prompt "Paper Loop pipeline, 5-stage self-referential loop, academic figure, clean vector style, English labels" \
  --out figure.png \
  --aspect landscape \
  --background auto
```

## Option B — auto-generate from the YAML config

Add a `figure.generate` block. If `figure.image` is missing (or doesn't
exist on disk), the builder invokes the generator, caches the PNG next
to the config, and embeds it.

```yaml
figure:
  caption: "..."
  width_mm: 125
  generate:
    prompt: |
      Academic figure illustrating a 5-stage paper-production harness
      (executor → runner → analyzer → writer → peer review) with a
      feedback loop indicated by a red dashed arrow from review back
      to the first stage. Clean vector style, English labels, light
      neutral background, high contrast, suitable for a Korean
      conference abstract.
    aspect: landscape            # square | landscape | portrait
    background: auto             # auto | opaque | transparent
    file_name: paperloop_fig.png # optional; defaults to <out>_figure.png
    output_dir: ./generated      # optional; defaults to <config_dir>/generated
    force: false                 # true to regenerate even if cached file exists
    timeout_seconds: 180
    codex: ~/.npm-global/bin/codex   # optional explicit codex binary
```

Cache behavior: the resolved filename is `output_dir/file_name`. If that
file already exists and `force` is `false`, the cached image is reused —
cheap re-runs while you iterate on body text or layout.

## Practical prompt tips

- Name the exact glyphs you want: "5 rounded rectangles labeled
  Executor, Runner, Analyzer, Writer, Peer Review, connected
  left-to-right by arrows."
- Specify language of labels: "English labels only" avoids mixed
  Korean/English text in the rendered figure.
- Ask for vector/flat style explicitly: "clean vector illustration,
  flat design, no photorealism" — generative image output tends to add
  texture otherwise.
- Keep aspect = `landscape` for wide figures, `square` for balanced
  panels, `portrait` only when vertical composition matters.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `codex responses` exits with "unknown command" | Older Codex binary. Install via `npm i -g @openai/codex` and prefer `~/.npm-global/bin/codex`, or pass `--codex /explicit/path`. |
| `Codex produced no image_generation_call result` | Inspect `codex.responses.jsonl` in the logs dir. Usually an auth/quota issue — run `codex login status`. |
| 429 / `usage_limit_reached` | This standalone script does not round-robin OAuth accounts. Either retry later, switch `CODEX_HOME`, or install the full `openclaw-codex-image-gen` plugin which supports the ohmyclaw OAuth pool. |
| MCP-related failures | Already mitigated — the subprocess launches with `-c mcp_servers={}`. |
