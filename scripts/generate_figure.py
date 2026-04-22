#!/usr/bin/env python3
"""Generate a PNG figure via the Codex CLI `responses` + `image_generation` tool.

Ports the core flow of the `openclaw-codex-image-gen` plugin
(https://github.com/jkf87/openclaw-codex-image-gen) into a standalone script.

Usage:
    generate_figure.py --prompt "..." --out figure.png \
        [--aspect square|landscape|portrait] [--background auto|opaque|transparent]
        [--codex /path/to/codex] [--timeout 120]

Requires: `codex` CLI logged in with a Codex-capable account (`codex login status`).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


SIZE_BY_ASPECT = {
    "square": "1024x1024",
    "landscape": "1536x1024",
    "portrait": "1024x1536",
}

BACKGROUNDS = ("auto", "opaque", "transparent")

# Candidates tried in order, same priority as the OpenClaw plugin.
CODEX_CANDIDATES = [
    os.path.expanduser("~/.npm-global/bin/codex"),
    "/usr/local/bin/codex",
    "/opt/homebrew/bin/codex",
]


def find_codex(explicit: str | None) -> str:
    if explicit:
        if not Path(explicit).exists():
            sys.exit(f"ERROR: --codex path does not exist: {explicit}")
        return explicit
    for p in CODEX_CANDIDATES:
        if Path(p).exists():
            return p
    found = shutil.which("codex")
    if found:
        return found
    sys.exit(
        "ERROR: could not locate the `codex` binary. "
        "Install OpenAI Codex CLI and ensure `codex login status` is valid, "
        "or pass --codex /explicit/path."
    )


def build_payload(prompt: str, aspect: str, background: str) -> str:
    size = SIZE_BY_ASPECT[aspect]
    return json.dumps(
        {
            "model": "gpt-5.4",
            "instructions": (
                "Use the image_generation tool to create the requested image. "
                "Return the image generation result."
            ),
            "input": [
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt.strip()}],
                }
            ],
            "tools": [
                {
                    "type": "image_generation",
                    "size": size,
                    "quality": "high",
                    "background": background,
                    "action": "generate",
                }
            ],
            "tool_choice": {"type": "image_generation"},
            "store": False,
            "stream": True,
        }
    )


def extract_image_b64(stdout: str) -> str | None:
    """Find the base64 image payload in Codex's JSONL stream."""
    image_b64: str | None = None
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item") or {}
        if event.get("type") == "response.output_item.done" and item.get("type") == "image_generation_call":
            image_b64 = item.get("result") or image_b64
    return image_b64


def run_codex(codex: str, payload: str, timeout: int, log_dir: Path) -> tuple[str, str]:
    log_dir.mkdir(parents=True, exist_ok=True)
    args = [codex, "-c", "mcp_servers={}", "responses"]
    proc = subprocess.run(
        args,
        input=payload,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    (log_dir / "codex.responses.jsonl").write_text(proc.stdout)
    (log_dir / "codex.stderr.log").write_text(proc.stderr)
    if proc.returncode != 0:
        sys.exit(
            f"ERROR: codex exited with {proc.returncode}. "
            f"stderr tail:\n{proc.stderr.strip().splitlines()[-10:]}"
        )
    return proc.stdout, proc.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True, help="Image generation prompt")
    ap.add_argument("--out", required=True, type=Path, help="Output PNG path")
    ap.add_argument("--aspect", choices=list(SIZE_BY_ASPECT), default="landscape")
    ap.add_argument("--background", choices=BACKGROUNDS, default="auto")
    ap.add_argument("--codex", default=None, help="Explicit codex binary path")
    ap.add_argument("--timeout", type=int, default=180, help="Subprocess timeout (seconds)")
    args = ap.parse_args()

    codex = find_codex(args.codex)
    payload = build_payload(args.prompt, args.aspect, args.background)

    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    log_dir = out.parent / (out.stem + ".codex_logs")

    stdout, _ = run_codex(codex, payload, args.timeout, log_dir)
    b64 = extract_image_b64(stdout)
    if not b64:
        sys.exit(
            "ERROR: Codex produced no image_generation_call result. "
            f"Inspect {log_dir / 'codex.responses.jsonl'} for the streamed events."
        )
    out.write_bytes(base64.b64decode(b64))
    print(f"Saved: {out}  ({out.stat().st_size:,} bytes)  via {codex}")


if __name__ == "__main__":
    main()
