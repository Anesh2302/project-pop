#!/usr/bin/env python3
"""
deliver_issue.py
Posts the digest markdown as a GitHub Issue with label 'digest'.
Usage: python deliver_issue.py digest.md
"""

import os
import sys
from datetime import datetime, timezone
from github import Github

def main():
    if len(sys.argv) < 2:
        print("Usage: deliver_issue.py <digest.md>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        body = f.read()

    token = os.environ["GITHUB_TOKEN"]
    repo_name = os.environ["REPO_NAME"]

    g = Github(token)
    repo = g.get_repo(repo_name)

    try:
        repo.get_label("digest")
    except Exception:
        repo.create_label(
            name="digest",
            color="0075ca",
            description="Automated daily project digest",
        )

    today = datetime.now(timezone.utc).strftime("%A, %B %-d %Y")
    title = f"Daily Digest — {today}"

    issue = repo.create_issue(
        title=title,
        body=body,
        labels=["digest"],
    )

    print(f"Issue created: {issue.html_url}")

if __name__ == "__main__":
    main()
