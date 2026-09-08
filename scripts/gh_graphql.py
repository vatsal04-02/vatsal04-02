"""
Minimal GitHub GraphQL client using only the Python standard library.
No dependencies -> nothing to break inside GitHub Actions.
"""
import json
import os
import urllib.request
import urllib.error

API_URL = "https://api.github.com/graphql"


def run_query(query: str, variables: dict, token: str) -> dict:
    """POST a GraphQL query to GitHub and return the parsed JSON response.

    Raises RuntimeError with the response body on any GraphQL-level error,
    so failures show up clearly in the Action log instead of failing silently.
    """
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "self-generating-profile-readme",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API HTTP {e.code}: {e.read().decode('utf-8')}")

    if "errors" in body:
        raise RuntimeError(f"GitHub GraphQL error: {json.dumps(body['errors'])}")
    return body["data"]
