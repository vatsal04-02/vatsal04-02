#!/usr/bin/env python3
"""
Photo -> ASCII portrait -> self-typing SVG.

Run this ONCE locally, by hand, whenever you replace your source photo.
It is deliberately NOT part of the nightly workflow -- your face doesn't
change every night, and rembg's model is too heavy to want to install
inside CI on a schedule.

Usage:
    python3 generate_portrait.py path/to/photo.jpg -o ../portrait.svg

Requires: pillow numpy opencv-python-headless rembg onnxruntime
"""
from __future__ import annotations
import argparse
import io
import sys

import numpy as np
import cv2
from PIL import Image

from svg_common import wrap_svg, esc, INK, RAMP

CHAR_W = 7.74          # em-advance-locked grid width, matches JetBrains Mono
                        # (600/1000 units) at font-size 12.9 -> 0.600em advance
FONT_SIZE = 12.9
LINE_H = CHAR_W / 0.6  # keep the same 0.6 advance-ratio vertically as width


def remove_background(img: Image.Image) -> Image.Image:
    """Cuts the subject out, forces everything else to white so it maps to
    the blank end of the ramp. Skipping this step fills the background with
    '@' characters and the portrait drowns."""
    from rembg import remove
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    cut = remove(buf.getvalue())
    fg = Image.open(io.BytesIO(cut)).convert("RGBA")
    white_bg = Image.new("RGBA", fg.size, (255, 255, 255, 255))
    white_bg.alpha_composite(fg)
    return white_bg.convert("RGB")


def enhance(gray: np.ndarray) -> np.ndarray:
    """Bilateral filter (smooth skin, keep edges) + CLAHE (local contrast)
    + a darkening curve. The curve is the fix on top of the base guide --
    without it the face renders washed out and featureless."""
    smoothed = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    contrasted = clahe.apply(smoothed)

    normalized = contrasted.astype(np.float64) / 255.0
    darkened = np.power(normalized, 1.7)
    return (darkened * 255).astype(np.uint8)


def to_ascii_grid(gray: np.ndarray, cols: int = 90) -> list[str]:
    h, w = gray.shape
    rows = max(1, round(cols * (h / w) * 0.48))
    resized = cv2.resize(gray, (cols, rows), interpolation=cv2.INTER_AREA)

    ramp = RAMP
    n = len(ramp) - 1
    grid = []
    for r in range(rows):
        line = []
        for c in range(cols):
            v = resized[r, c] / 255.0
            # v=1 (white/background) -> index 0 (blank); v=0 (black) -> last char
            idx = round((1 - v) * n)
            line.append(ramp[idx])
        grid.append("".join(line))
    return grid


def grid_to_svg(grid: list[str]) -> str:
    rows = len(grid)
    cols = max(len(r) for r in grid) if grid else 0
    W = round(cols * CHAR_W) + 20
    H = round(rows * LINE_H) + 20

    body = []
    for i, line in enumerate(grid):
        y = 10 + (i + 1) * LINE_H
        row_w = round(len(line) * CHAR_W)
        clip_id = f"clip{i}"
        # clipPath rect animates width 0 -> full; a thin cursor rides the edge
        body.append(f"""
  <clipPath id="{clip_id}">
    <rect x="10" y="{y - LINE_H:.1f}" width="0" height="{LINE_H:.1f}">
      <animate attributeName="width" from="0" to="{row_w}" dur="0.4s"
               begin="{i * 0.09:.2f}s" fill="freeze"/>
    </rect>
  </clipPath>
  <g clip-path="url(#{clip_id})">
    <text x="10" y="{y:.1f}" class="ramp" font-size="{FONT_SIZE}" fill="{INK}"
          xml:space="preserve">{esc(line)}</text>
    <rect x="10" y="{y - LINE_H:.1f}" width="2.4" height="{LINE_H:.1f}" fill="{INK}" opacity="0.85">
      <animate attributeName="x" from="10" to="{10 + row_w}" dur="0.4s"
               begin="{i * 0.09:.2f}s" fill="freeze"/>
      <set attributeName="opacity" to="0" begin="{i * 0.09 + 0.4:.2f}s" fill="freeze"/>
    </rect>
  </g>""")

    return wrap_svg(W, H, "\n".join(body), extra_style=f".ramp {{ white-space: pre; letter-spacing: 0; }}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("-o", "--out", default="../portrait.svg")
    ap.add_argument("--cols", type=int, default=90)
    ap.add_argument("--skip-bg-removal", action="store_true",
                     help="use if your photo already has a plain white background")
    args = ap.parse_args()

    img = Image.open(args.photo).convert("RGB")
    if img.width < 1200:
        print(f"warning: source is {img.width}px wide; 1200px+ recommended "
              f"or thin features (glasses, brows) will average away", file=sys.stderr)

    if not args.skip_bg_removal:
        print("removing background (first run downloads the rembg model, ~176MB)...")
        img = remove_background(img)

    arr = np.array(img)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

    print("enhancing contrast...")
    processed = enhance(gray)

    print(f"building {args.cols}-column ASCII grid...")
    grid = to_ascii_grid(processed, cols=args.cols)

    print("rendering typing-animation SVG...")
    svg = grid_to_svg(grid)
    with open(args.out, "w") as f:
        f.write(svg)

    rows = len(grid)
    est_seconds = rows * 0.09 + 0.4
    print(f"wrote {args.out} ({args.cols} cols x {rows} rows, "
          f"~{est_seconds:.1f}s to finish typing)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
