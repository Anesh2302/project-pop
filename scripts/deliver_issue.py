#!/usr/bin/env python3
import os, sys
from datetime import datetime, timezone
from github import Github

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    with open(sys.argv[1]) as f:
        body = f.read()
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.environ["REPO_NAME"])
    try:
        repo.get_label("digest")
    except Exception:
        repo.create_label(name="digest", color="0075ca", description="Automated daily project digest")
    today = datetime.now(timezone.utc).strftime("%A, %B %-d %Y")
    issue = repo.create_issue(title=f"Daily Digest — {today}", body=body, labels=["digest"])
    print(f"Issue created: {issue.html_url}")

if __name__ == "__main__":
    main()
