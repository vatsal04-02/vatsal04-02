#!/usr/bin/env python3
"""
Entry point run nightly by .github/workflows/refresh-stats.yml.

Reads GH_LOGIN + GITHUB_TOKEN from the environment (both are provided
automatically by the workflow -- no personal access token needed), pulls
contribution + language data, and writes:

    stats.svg    hero total + weekly sparkline
    streak.svg   current / longest streak
    langs.svg    top languages by bytes
    year.svg     one ramp character per day

Only the Python standard library is imported here (via gh_graphql.py),
so there is nothing for CI to fail to install.
"""
import os
import sys

from fetch_data import fetch_contributions, compute_streaks, weekly_sparkline, fetch_top_languages
from svg_stats import render_stats_svg
from svg_streak import render_streak_svg
from svg_langs import render_langs_svg
from svg_year import render_year_svg


def main() -> int:
    login = os.environ.get("GH_LOGIN")
    token = os.environ.get("GITHUB_TOKEN")
    if not login or not token:
        print("GH_LOGIN and GITHUB_TOKEN must both be set", file=sys.stderr)
        return 1

    print(f"fetching contributions for {login}...")
    contrib = fetch_contributions(login, token)

    print("computing streaks...")
    streaks = compute_streaks(contrib.days)

    print("building weekly sparkline...")
    sparkline = weekly_sparkline(contrib.days, weeks=12)

    print("fetching top languages...")
    langs = fetch_top_languages(login, token, top_n=6)

    print("rendering SVGs...")
    with open("stats.svg", "w") as f:
        f.write(render_stats_svg(contrib.total, sparkline, login))

    with open("streak.svg", "w") as f:
        f.write(render_streak_svg(
            streaks["current"], streaks["current_range"],
            streaks["longest"], streaks["longest_range"],
        ))

    with open("langs.svg", "w") as f:
        f.write(render_langs_svg(langs))

    with open("year.svg", "w") as f:
        f.write(render_year_svg(contrib.days, login))

    print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
