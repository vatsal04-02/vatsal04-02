"""
Pulls everything the stats SVGs need from the GitHub GraphQL API.

Two correctness rules baked in on purpose (see README notes):
  1. contributionsCollection window is pinned to whole UTC days, computed
     once per run, so two runs minutes apart bucket days identically.
  2. repositories() is filtered to privacy: PUBLIC, so the numbers are the
     same whether a human's PAT or the workflow's GITHUB_TOKEN runs this.
"""
from __future__ import annotations
import datetime as dt
from dataclasses import dataclass, field

from gh_graphql import run_query

CONTRIB_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

LANG_QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    repositories(
      first: 100
      after: $cursor
      privacy: PUBLIC
      isFork: false
      ownerAffiliations: OWNER
      orderBy: {field: UPDATED_AT, direction: DESC}
    ) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node { name color }
          }
        }
      }
    }
  }
}
"""


def utc_day_window(days: int = 364) -> tuple[str, str, dt.date, dt.date]:
    """Whole-UTC-day window ending today. Deterministic regardless of the
    time of day the workflow happens to run at."""
    today = dt.datetime.now(dt.timezone.utc).date()
    start = today - dt.timedelta(days=days)
    from_iso = dt.datetime.combine(start, dt.time(0, 0, 0), dt.timezone.utc).isoformat()
    to_iso = dt.datetime.combine(today, dt.time(23, 59, 59), dt.timezone.utc).isoformat()
    return from_iso, to_iso, start, today


@dataclass
class DayCount:
    date: dt.date
    count: int


@dataclass
class ContribData:
    total: int
    days: list[DayCount] = field(default_factory=list)


def fetch_contributions(login: str, token: str) -> ContribData:
    from_iso, to_iso, _, _ = utc_day_window()
    data = run_query(CONTRIB_QUERY, {"login": login, "from": from_iso, "to": to_iso}, token)
    cal = data["user"]["contributionsCollection"]["contributionCalendar"]
    days = []
    for week in cal["weeks"]:
        for d in week["contributionDays"]:
            days.append(DayCount(dt.date.fromisoformat(d["date"]), d["contributionCount"]))
    days.sort(key=lambda d: d.date)
    return ContribData(total=cal["totalContributions"], days=days)


def compute_streaks(days: list[DayCount]) -> dict:
    """Returns current + longest streak, each with its date range."""
    best_len, best_start, best_end = 0, None, None
    run_len, run_start = 0, None

    cur_len, cur_start = 0, None

    for d in days:
        if d.count > 0:
            if run_len == 0:
                run_start = d.date
            run_len += 1
            if run_len > best_len:
                best_len, best_start, best_end = run_len, run_start, d.date
        else:
            run_len = 0

    # current streak = trailing run ending on the last day that has data
    for d in reversed(days):
        if d.count > 0:
            if cur_len == 0:
                cur_start = d.date
            cur_len += 1
        else:
            break

    cur_end = days[-1].date if days else None
    return {
        "current": cur_len,
        "current_range": (cur_start, cur_end) if cur_len else None,
        "longest": best_len,
        "longest_range": (best_start, best_end) if best_len else None,
    }


def compute_active_days(days: list[DayCount]) -> int:
    return sum(1 for d in days if d.count > 0)


def compute_best_week(days: list[DayCount]) -> int:
    if not days:
        return 0
    buckets: dict[tuple[int, int], int] = {}
    for d in days:
        iso_year, iso_week, _ = d.date.isocalendar()
        key = (iso_year, iso_week)
        buckets[key] = buckets.get(key, 0) + d.count
    return max(buckets.values())


def weekly_sparkline(days: list[DayCount], weeks: int = 12) -> list[int]:
    """Sum contributions into ISO weeks, most recent `weeks` buckets."""
    if not days:
        return []
    buckets: dict[tuple[int, int], int] = {}
    for d in days:
        iso_year, iso_week, _ = d.date.isocalendar()
        key = (iso_year, iso_week)
        buckets[key] = buckets.get(key, 0) + d.count
    ordered = sorted(buckets.items())
    return [v for _, v in ordered[-weeks:]]


def fetch_top_languages(login: str, token: str, top_n: int = 6) -> dict:
    """Returns both rankings the reference layout shows side by side:
        by_bytes: [(name, color, total_bytes), ...] desc
        by_repos: [(name, color, repo_count), ...] desc
    A repo counts once per language it contains, regardless of size."""
    cursor = None
    bytes_totals: dict[str, dict] = {}
    repo_counts: dict[str, dict] = {}
    while True:
        data = run_query(LANG_QUERY, {"login": login, "cursor": cursor}, token)
        repos = data["user"]["repositories"]
        for repo in repos["nodes"]:
            for edge in repo["languages"]["edges"]:
                name = edge["node"]["name"]
                color = edge["node"]["color"] or "#999999"
                size = edge["size"]
                b = bytes_totals.setdefault(name, {"color": color, "size": 0})
                b["size"] += size
                r = repo_counts.setdefault(name, {"color": color, "count": 0})
                r["count"] += 1
        if not repos["pageInfo"]["hasNextPage"]:
            break
        cursor = repos["pageInfo"]["endCursor"]

    by_bytes = sorted(bytes_totals.items(), key=lambda kv: kv[1]["size"], reverse=True)
    by_repos = sorted(repo_counts.items(), key=lambda kv: kv[1]["count"], reverse=True)
    return {
        "by_bytes": [(name, v["color"], v["size"]) for name, v in by_bytes[:top_n]],
        "by_repos": [(name, v["color"], v["count"]) for name, v in by_repos[:top_n]],
    }
