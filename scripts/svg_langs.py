from svg_common import wrap_svg, esc, INK, DIM

TITLE_Y = 16      # fixed row for column titles, well clear of the first bar
ROWS_START_Y = 46  # first bar row starts here -- 30px below the title,
                   # enough clearance even for all-caps names like "CSS"
                   # which sit taller in their line box than mixed case


def _column(x0: float, col_w: float, title: str, rows: list[tuple[str, str, float, str]],
            body: list, row_h: int, bar_h: int, delay0: float):
    """rows: [(name, color, fraction_of_max, value_label), ...]"""
    body.append(f'<text x="{x0}" y="{TITLE_Y}" font-size="11" fill="{DIM}" letter-spacing="1">{esc(title)}</text>')
    bar_max_w = col_w - 46
    y = ROWS_START_Y
    for i, (name, color, frac, value_label) in enumerate(rows):
        bw = max(frac, 0.02) * bar_max_w
        body.append(f'<text x="{x0}" y="{y-6}" font-size="12" fill="{INK}">{esc(name)}</text>')
        body.append(f'<text x="{x0+col_w}" y="{y-6}" font-size="11" fill="{DIM}" text-anchor="end">{esc(value_label)}</text>')
        body.append(f'<rect x="{x0}" y="{y}" width="{bar_max_w:.1f}" height="{bar_h}" rx="3" fill="{DIM}" opacity="0.18"/>')
        body.append(
            f'<rect x="{x0}" y="{y}" width="{bw:.1f}" height="{bar_h}" rx="3" fill="{color}">'
            f'<animate attributeName="width" from="0" to="{bw:.1f}" dur="0.5s" '
            f'begin="{delay0 + i*0.06:.2f}s" fill="freeze"/>'
            f'</rect>'
        )
        y += row_h


def render_langs_svg(by_bytes: list[tuple[str, str, int]], by_repos: list[tuple[str, str, int]]) -> str:
    W = 640
    pad = 4
    row_h = 26
    bar_h = 7
    rows = max(len(by_bytes), len(by_repos), 1)
    H = ROWS_START_Y + row_h * rows + 6

    body = []

    total_bytes = sum(b for _, _, b in by_bytes) or 1
    bytes_rows = [(name, color, size / total_bytes, f"{size/total_bytes*100:.0f}%")
                  for name, color, size in by_bytes]

    max_repos = max((c for _, _, c in by_repos), default=1) or 1
    repo_rows = [(name, color, count / max_repos, str(count))
                 for name, color, count in by_repos]

    col_w = (W - 2 * pad - 40) / 2
    left_x = pad
    right_x = pad + col_w + 40

    _column(left_x, col_w, "by bytes", bytes_rows, body, row_h=row_h, bar_h=bar_h, delay0=0.0)
    _column(right_x, col_w, "by repos", repo_rows, body, row_h=row_h, bar_h=bar_h, delay0=0.15)

    return wrap_svg(W, H, "\n  ".join(body))


if __name__ == "__main__":
    by_bytes = [
        ("JavaScript", "#f1e05a", 65000),
        ("CSS", "#563d7c", 10000),
        ("HTML", "#e34c26", 10000),
        ("TypeScript", "#2b7489", 7000),
        ("Python", "#3572A5", 6000),
        ("Java", "#b07219", 3000),
    ]
    by_repos = [
        ("CSS", "#563d7c", 11),
        ("HTML", "#e34c26", 10),
        ("JavaScript", "#f1e05a", 7),
        ("Python", "#3572A5", 2),
        ("Dockerfile", "#384d54", 2),
        ("Shell", "#89e051", 1),
    ]
    demo = render_langs_svg(by_bytes, by_repos)
    with open("langs.svg", "w") as f:
        f.write(demo)
    print("wrote langs.svg (using your actual repo's top languages as test data)")
