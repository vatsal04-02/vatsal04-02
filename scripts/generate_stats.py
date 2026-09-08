#!/usr/bin/env python3
"""
Entry point run nightly by .github/workflows/refresh-stats.yml.

Reads GH_LOGIN + GITHUB_TOKEN from the environment (both provided
automatically by the workflow -- no personal access token needed), pulls
contribution + language data, and writes:

    hero.svg     total + active days + best week + sparkline
    streak.svg   current / longest streak
    langs.svg    top languages, by bytes and by repos
    year.svg     one ramp character per day, month/weekday labelled

Only the Python standard library is imported here (via gh_graphql.py),
so there is nothing for CI to fail to install.
"""
import os
import sys

from fetch_data import (
    fetch_contributions,
    compute_streaks,
    compute_active_days,
    compute_best_week,
    weekly_sparkline,
    fetch_top_languages,
)
from svg_hero import render_hero_svg
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

    print("computing streaks / active days / best week...")
    streaks = compute_streaks(contrib.days)
    active_days = compute_active_days(contrib.days)
    best_week = compute_best_week(contrib.days)
    sparkline = weekly_sparkline(contrib.days, weeks=12)

    print("fetching top languages...")
    langs = fetch_top_languages(login, token, top_n=6)

    print("rendering SVGs...")
    with open("hero.svg", "w") as f:
        f.write(render_hero_svg(contrib.total, active_days, best_week, sparkline))

    with open("streak.svg", "w") as f:
        f.write(render_streak_svg(
            streaks["current"], streaks["current_range"],
            streaks["longest"], streaks["longest_range"],
        ))

    with open("langs.svg", "w") as f:
        f.write(render_langs_svg(langs["by_bytes"], langs["by_repos"]))

    with open("year.svg", "w") as f:
        f.write(render_year_svg(contrib.days))

    print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
