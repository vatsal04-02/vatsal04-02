"""
Shared building blocks for every generated SVG:
  - the ASCII ramp (same one the portrait uses, for the year grid)
  - font embedding (base64 woff2 -> @font-face, so files stand alone)
  - a thin XML-escape + wrapper so every graphic shares one visual language

Colour: one fill colour per graphic. No per-character rainbow colouring --
that's what makes most ASCII/graph art look noisy instead of deliberate.
"""
from __future__ import annotations
import base64
import os
import xml.sax.saxutils as saxutils

# same 13-step ramp used by the portrait (Part 1). Index 0 = blank/background.
RAMP = " .`:-=+*cs#%@"

INK = "#c9d1d9"      # primary text colour (GitHub dark-mode friendly light grey)
DIM = "#6e7681"      # secondary / muted
ACCENT = "#58a6ff"   # single accent colour, used sparingly
BG = "transparent"

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")


def esc(s: str) -> str:
    return saxutils.escape(str(s))


def _font_face(family: str, filename: str, weight: int = 400) -> str:
    """Builds an @font-face block with the font inlined as base64.
    Silently returns '' if the subset hasn't been built yet (Part 4 step),
    so scripts still run and fall back to system monospace/sans."""
    path = os.path.join(FONT_DIR, filename)
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"""
    @font-face {{
      font-family: '{family}';
      src: url(data:font/woff2;base64,{b64}) format('woff2');
      font-weight: {weight};
      font-style: normal;
    }}"""


def font_styles() -> str:
    """All font-face blocks this project knows how to embed. Missing subset
    files degrade gracefully to 'monospace' / 'sans-serif'."""
    return (
        _font_face("JBM-Ramp", "ramp.woff2")
        + _font_face("JBM-Head", "headings.woff2")
        + _font_face("JBM-Body", "basic-latin.woff2")
    )


def wrap_svg(width: int, height: int, body: str, extra_style: str = "") -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <style>
    {font_styles()}
    text {{ font-family: 'JBM-Body', 'JBM-Head', ui-monospace, monospace; }}
    .head {{ font-family: 'JBM-Head', ui-monospace, monospace; }}
    .ramp {{ font-family: 'JBM-Ramp', ui-monospace, monospace; }}
    {extra_style}
  </style>
  {body}
</svg>"""
