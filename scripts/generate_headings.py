"""
Section headings as images -- the only way to put your own typeface on a
heading, since GitHub strips <style>/class/font from markdown text.

These don't depend on live data, so they're generated once, locally, not
by the nightly workflow. Run:

    python3 scripts/generate_headings.py

whenever you add/rename a section.
"""
from svg_common import wrap_svg, esc, INK, DIM

CONTENT_WIDTH = 640  # matches the width= on the <img> tags in README.md


def render_heading_svg(label: str, width: int = CONTENT_WIDTH, height: int = 30) -> str:
    label = label.lower()
    pad_left = 2
    font_size = 15
    text_w = len(label) * font_size * 0.62  # rough monospace advance estimate
    rule_x1 = pad_left + text_w + 12
    y = height // 2 + 5

    body = f"""
  <text x="{pad_left}" y="{y}" class="head" font-size="{font_size}" font-weight="700" fill="{INK}">{esc(label)}</text>
  <line x1="{rule_x1:.1f}" y1="{height//2}" x2="{width-2}" y2="{height//2}" stroke="{DIM}" stroke-width="1" opacity="0.5"/>
"""
    return wrap_svg(width, height, body)


HEADINGS = ["about", "stack", "projects", "stats", "the year"]

if __name__ == "__main__":
    import os
    out_dir = os.path.join(os.path.dirname(__file__), "..", "headings")
    os.makedirs(out_dir, exist_ok=True)
    for label in HEADINGS:
        fname = label.replace(" ", "-") + ".svg"
        path = os.path.join(out_dir, fname)
        with open(path, "w") as f:
            f.write(render_heading_svg(label))
        print(f"wrote {path}")
