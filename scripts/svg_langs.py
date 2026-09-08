from svg_common import wrap_svg, esc, INK, DIM


def render_langs_svg(langs: list[tuple[str, str, int]]) -> str:
    """langs: [(name, hex_color, bytes), ...] already sorted desc, top N."""
    W = 480
    pad = 24
    row_h = 28
    H = 44 + row_h * max(len(langs), 1)

    total = sum(b for _, _, b in langs) or 1
    bar_max_w = W - 2 * pad - 90

    body = [f'<text x="{pad}" y="30" class="head" font-size="13" fill="{DIM}">top languages · by bytes</text>']

    y = 54
    for i, (name, color, size) in enumerate(langs):
        pct = size / total
        bw = pct * bar_max_w
        body.append(f'<text x="{pad}" y="{y-6}" font-size="12" fill="{INK}">{esc(name)}</text>')
        body.append(f'<text x="{W-pad}" y="{y-6}" font-size="11" fill="{DIM}" text-anchor="end">{pct*100:.1f}%</text>')
        body.append(
            f'<rect x="{pad}" y="{y}" width="{bar_max_w:.1f}" height="8" rx="4" fill="{DIM}" opacity="0.18"/>'
        )
        body.append(
            f'<rect x="{pad}" y="{y}" width="{bw:.1f}" height="8" rx="4" fill="{color}">'
            f'<animate attributeName="width" from="0" to="{bw:.1f}" dur="0.6s" '
            f'begin="{i*0.08:.2f}s" fill="freeze"/>'
            f'</rect>'
        )
        y += row_h

    return wrap_svg(W, H, "\n  ".join(body))


if __name__ == "__main__":
    demo = render_langs_svg([
        ("Python", "#3572A5", 120000),
        ("JavaScript", "#f1e05a", 80000),
        ("TypeScript", "#2b7489", 45000),
        ("HTML", "#e34c26", 20000),
        ("Shell", "#89e051", 8000),
    ])
    with open("langs.svg", "w") as f:
        f.write(demo)
    print("wrote langs.svg (demo data)")
