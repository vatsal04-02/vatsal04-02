import datetime as dt
from svg_common import wrap_svg, esc, INK, DIM, RAMP


def _ramp_char(count: int, max_count: int) -> str:
    if count <= 0 or max_count <= 0:
        return RAMP[0]
    # skip index 0 (blank) for any real activity, spread the rest across the ramp
    steps = len(RAMP) - 1
    level = max(1, min(steps, round((count / max_count) * steps)))
    return RAMP[level]


def render_year_svg(days: list, login: str) -> str:
    """days: list of objects with .date (datetime.date) and .count (int),
    sorted ascending, covering the last ~364 days."""
    if not days:
        return wrap_svg(480, 60, f'<text x="24" y="30" fill="{DIM}">no data</text>')

    max_count = max(d.count for d in days) or 1

    # lay out as GitHub does: columns = weeks, rows = weekdays (Sun-Sat)
    first = days[0].date
    # pad to the preceding Sunday so week columns line up
    lead_pad = (first.weekday() + 1) % 7  # Python Mon=0..Sun=6 -> shift so Sun=0
    cells = [None] * lead_pad + list(days)

    cols = (len(cells) + 6) // 7
    cell = 10
    gap = 3
    pad = 24
    top = 40
    W = pad * 2 + cols * (cell + gap)
    H = top + 7 * (cell + gap) + 20

    body = [f'<text x="{pad}" y="24" class="head" font-size="13" fill="{DIM}">{esc(login)} · the year</text>']

    for i, d in enumerate(cells):
        col = i // 7
        row = i % 7
        x = pad + col * (cell + gap)
        y = top + row * (cell + gap)
        if d is None:
            continue
        ch = _ramp_char(d.count, max_count)
        delay = col * 0.012
        body.append(
            f'<text x="{x}" y="{y+cell-1}" class="ramp" font-size="{cell+2}" fill="{INK}" opacity="0">{esc(ch)}'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.25s" begin="{delay:.3f}s" fill="freeze"/>'
            f'</text>'
        )

    return wrap_svg(W, H, "\n  ".join(body))


if __name__ == "__main__":
    import random

    class D:
        def __init__(self, date, count):
            self.date = date
            self.count = count

    today = dt.date.today()
    demo_days = [D(today - dt.timedelta(days=i), random.choice([0,0,0,1,2,4,8,15]))
                 for i in range(364, -1, -1)]
    demo = render_year_svg(demo_days, "vatsal04-02")
    with open("year.svg", "w") as f:
        f.write(demo)
    print("wrote year.svg (demo data)")
