"""
Hero graphic: big total-contributions number + a weekly sparkline.

Columns, not a line -- daily/weekly contribution counts are sparse and
discrete, and a line chart implies values that were never actually there
between two real data points.
"""
from svg_common import wrap_svg, esc, INK, DIM, ACCENT


def render_stats_svg(total: int, weekly_counts: list[int], login: str) -> str:
    W, H = 480, 160
    pad = 24
    chart_w = W - 2 * pad
    chart_h = 64
    chart_top = 84

    body = []
    body.append(f'<text x="{pad}" y="34" class="head" font-size="13" fill="{DIM}">{esc(login)} · contributions, last 12 months</text>')
    body.append(f'<text x="{pad}" y="70" font-size="40" font-weight="700" fill="{INK}">{total:,}</text>')

    if weekly_counts:
        max_v = max(weekly_counts) or 1
        n = len(weekly_counts)
        bar_w = chart_w / n * 0.62
        gap = chart_w / n
        for i, v in enumerate(weekly_counts):
            bh = 0 if max_v == 0 else (v / max_v) * chart_h
            x = pad + i * gap
            y = chart_top + (chart_h - bh)
            fill = ACCENT if v > 0 else DIM
            opacity = 0.9 if v > 0 else 0.25
            body.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{max(bh,1):.1f}" '
                f'rx="1.5" fill="{fill}" opacity="{opacity}">'
                f'<animate attributeName="height" from="0" to="{max(bh,1):.1f}" dur="0.5s" '
                f'begin="{i * 0.02:.2f}s" fill="freeze"/>'
                f'<animate attributeName="y" from="{chart_top + chart_h:.1f}" to="{y:.1f}" dur="0.5s" '
                f'begin="{i * 0.02:.2f}s" fill="freeze"/>'
                f'</rect>'
            )
        body.append(f'<line x1="{pad}" y1="{chart_top + chart_h}" x2="{pad + chart_w}" y2="{chart_top + chart_h}" stroke="{DIM}" stroke-width="1" opacity="0.4"/>')

    return wrap_svg(W, H, "\n  ".join(body))


if __name__ == "__main__":
    # smoke test with fake data
    demo = render_stats_svg(1423, [3, 0, 12, 5, 0, 0, 8, 20, 4, 1, 0, 6], "vatsal04-02")
    with open("stats.svg", "w") as f:
        f.write(demo)
    print("wrote stats.svg (demo data)")
