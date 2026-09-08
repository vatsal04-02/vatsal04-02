"""
Hero graphic, redesigned to match the reference layout:

    900                                              104
    contributions in the last year              active days
                                                          125
                                                     best week
    [ ---- sparkline ---- ]
    updated <date>, live from the GitHub API

Columns, not a line -- daily/weekly contribution counts are sparse and
discrete; a line chart between two real points implies values that were
never actually there.
"""
import datetime as dt
from svg_common import wrap_svg, esc, INK, DIM, ACCENT


def render_hero_svg(total: int, active_days: int, best_week: int, weekly_counts: list[int]) -> str:
    W, H = 640, 206
    pad = 4
    chart_top = 120
    chart_h = 50
    chart_w = W - 2 * pad

    body = []

    # left: big total
    body.append(f'<text x="{pad}" y="56" font-size="46" font-weight="700" fill="{INK}">'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" fill="freeze"/>{total:,}</text>')
    body.append(f'<text x="{pad}" y="80" font-size="13" fill="{DIM}">contributions in the last year</text>')

    # right: active days / best week, stacked, right-aligned
    body.append(f'<text x="{W-pad}" y="34" font-size="24" font-weight="700" fill="{INK}" text-anchor="end">{active_days}</text>')
    body.append(f'<text x="{W-pad}" y="50" font-size="12" fill="{DIM}" text-anchor="end">active days</text>')
    body.append(f'<text x="{W-pad}" y="76" font-size="24" font-weight="700" fill="{INK}" text-anchor="end">{best_week}</text>')
    body.append(f'<text x="{W-pad}" y="92" font-size="12" fill="{DIM}" text-anchor="end">best week</text>')

    # sparkline, weekly totals, filled area + line for the smoother "trend" read
    if weekly_counts:
        n = len(weekly_counts)
        max_v = max(weekly_counts) or 1
        step = chart_w / max(n - 1, 1)
        pts = []
        for i, v in enumerate(weekly_counts):
            x = pad + i * step
            y = chart_top + chart_h - (v / max_v) * chart_h
            pts.append((x, y))

        line_path = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        area_path = line_path + f" L {pts[-1][0]:.1f},{chart_top+chart_h} L {pts[0][0]:.1f},{chart_top+chart_h} Z"

        body.append(f'<path d="{area_path}" fill="{DIM}" opacity="0.12"/>')
        body.append(
            f'<path d="{line_path}" fill="none" stroke="{ACCENT}" stroke-width="1.6" '
            f'stroke-linejoin="round" stroke-linecap="round" pathLength="100">'
            f'<animate attributeName="stroke-dasharray" from="0,100" to="100,0" dur="0.9s" fill="freeze"/>'
            f'</path>'
        )
        lx, ly = pts[-1]
        body.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="3" fill="{ACCENT}">'
                     f'<animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="0.9s" fill="freeze"/>'
                     f'</circle>')

    updated = dt.datetime.now(dt.timezone.utc).strftime("%b %-d, %Y")
    body.append(f'<text x="{pad}" y="{chart_top + chart_h + 18}" font-size="10" fill="{DIM}">'
                f'updated {esc(updated)} · live from the GitHub API</text>')

    return wrap_svg(W, H, "\n  ".join(body))


if __name__ == "__main__":
    demo = render_hero_svg(900, 104, 125,
                            [10, 8, 12, 9, 30, 40, 15, 20, 18, 12, 60, 25])
    with open("hero.svg", "w") as f:
        f.write(demo)
    print("wrote hero.svg (demo data)")
