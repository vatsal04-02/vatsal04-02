Run `scripts/build_font_subsets.sh` to populate this folder with:

- `ramp.woff2` — 13 characters, used by the portrait and year grid
- `headings.woff2` — only the letters used in your section headings
- `basic-latin.woff2` — numbers + labels used in the data graphics

Also copy the font's OFL `LICENSE.txt` in here — it ships in a public
repo, so the license needs to travel with it.

Until these files exist, every generated SVG falls back gracefully to
the visitor's system monospace/sans font (see `svg_common.py::_font_face`).
