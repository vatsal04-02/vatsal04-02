import datetime as dt
from svg_common import wrap_svg, esc, INK, DIM, ACCENT


def _fmt_range(rng) -> str:
    if not rng or not rng[0]:
        return "—"
    start, end = rng
    if start == end:
        return start.strftime("%b %-d")
    same_year = start.year == end.year
    s = start.strftime("%b %-d")
    e = end.strftime("%b %-d, %Y") if same_year else end.strftime("%b %-d, %Y")
    return f"{s} – {e}"


def render_streak_svg(current: int, current_range, longest: int, longest_range) -> str:
    W, H = 480, 140
    pad = 24

    body = []
    body.append(f'<text x="{pad}" y="34" class="head" font-size="13" fill="{DIM}">streak</text>')

    # current streak, left column
    cx = pad
    body.append(f'<text x="{cx}" y="76" font-size="34" font-weight="700" fill="{ACCENT}">'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" fill="freeze"/>{current}</text>')
    body.append(f'<text x="{cx}" y="96" font-size="12" fill="{DIM}">day current streak</text>')
    body.append(f'<text x="{cx}" y="114" font-size="11" fill="{DIM}">{esc(_fmt_range(current_range))}</text>')

    # divider
    mid = W / 2
    body.append(f'<line x1="{mid}" y1="44" x2="{mid}" y2="{H-24}" stroke="{DIM}" stroke-width="1" opacity="0.35"/>')

    # longest streak, right column
    rx = mid + 32
    body.append(f'<text x="{rx}" y="76" font-size="34" font-weight="700" fill="{INK}">'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="0.1s" fill="freeze"/>{longest}</text>')
    body.append(f'<text x="{rx}" y="96" font-size="12" fill="{DIM}">day longest streak</text>')
    body.append(f'<text x="{rx}" y="114" font-size="11" fill="{DIM}">{esc(_fmt_range(longest_range))}</text>')

    return wrap_svg(W, H, "\n  ".join(body))


if __name__ == "__main__":
    today = dt.date.today()
    demo = render_streak_svg(7, (today - dt.timedelta(days=6), today), 21,
                              (today - dt.timedelta(days=90), today - dt.timedelta(days=70)))
    with open("streak.svg", "w") as f:
        f.write(demo)
    print("wrote streak.svg (demo data)")
