import calendar
import datetime as dt
from svg_common import wrap_svg, esc, INK, DIM, RAMP


def _ramp_char(count: int, max_count: int) -> str:
    if count <= 0 or max_count <= 0:
        return RAMP[0]
    steps = len(RAMP) - 1
    level = max(1, min(steps, round((count / max_count) * steps)))
    return RAMP[level]


def render_year_svg(days: list) -> str:
    """days: list of objects with .date (datetime.date) and .count (int),
    sorted ascending, covering the last ~364 days."""
    if not days:
        return wrap_svg(640, 60, f'<text x="4" y="30" fill="{DIM}">no data</text>')

    max_count = max(d.count for d in days) or 1
    active = sum(1 for d in days if d.count > 0)
    total_days = len(days)

    first = days[0].date
    lead_pad = (first.weekday() + 1) % 7  # shift so week starts Sunday
    cells = [None] * lead_pad + list(days)

    cols = (len(cells) + 6) // 7
    cell = 10
    gap = 3
    left_label_w = 30
    pad = 4
    top = 46

    W = 640
    grid_w = cols * (cell + gap)
    grid_x0 = left_label_w
    # if the grid would overflow the fixed width, shrink cell+gap to fit
    if grid_x0 + grid_w > W - pad:
        avail = W - pad - grid_x0
        cell_gap = avail / cols
        gap = 3
        cell = max(4, cell_gap - gap)

    H = round(top + 7 * (cell + gap) + 22)

    body = [f'<text x="{pad}" y="16" font-size="11" fill="{DIM}">{active} of {total_days} days had a contribution</text>']
    body.append(f'<text x="{W-pad}" y="16" font-size="10" fill="{DIM}" text-anchor="end">less {RAMP[1]} {RAMP[4]} {RAMP[8]} {RAMP[-1]} more</text>')

    # weekday labels (mon / wed / fri), sparse like the reference
    for row, label in [(1, "mon"), (3, "wed"), (5, "fri")]:
        y = top + row * (cell + gap) + cell - 1
        body.append(f'<text x="0" y="{y:.1f}" font-size="9" fill="{DIM}">{label}</text>')

    # month labels along the top of the grid, placed at the first column of each month
    last_month = None
    for i, d in enumerate(cells):
        if d is None:
            continue
        col = i // 7
        if d.date.day <= 7 and d.date.month != last_month:
            x = grid_x0 + col * (cell + gap)
            body.append(f'<text x="{x:.1f}" y="{top-8}" font-size="9" fill="{DIM}">{calendar.month_abbr[d.date.month].lower()}</text>')
            last_month = d.date.month

    for i, d in enumerate(cells):
        col = i // 7
        row = i % 7
        x = grid_x0 + col * (cell + gap)
        y = top + row * (cell + gap)
        if d is None:
            continue
        ch = _ramp_char(d.count, max_count)
        delay = col * 0.012
        body.append(
            f'<text x="{x:.1f}" y="{y+cell-1:.1f}" class="ramp" font-size="{cell+2:.1f}" fill="{INK}" opacity="0">{esc(ch)}'
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
    demo_days = [D(today - dt.timedelta(days=i), random.choice([0, 0, 0, 1, 2, 4, 8, 15]))
                 for i in range(364, -1, -1)]
    demo = render_year_svg(demo_days)
    with open("year.svg", "w") as f:
        f.write(demo)
    print("wrote year.svg (demo data)")
