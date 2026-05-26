#!/usr/bin/env python3
"""
collect_activity.py
Fetches all GitHub repo activity from the last 24 hours and outputs JSON.
Run before generate_digest.py.
"""

import os
import json
import sys
from datetime import datetime, timedelta, timezone
from github import Github

REPO_NAME = os.environ["REPO_NAME"]
TOKEN = os.environ["GITHUB_TOKEN"]
g = Github(TOKEN)
repo = g.get_repo(REPO_NAME)

since = datetime.now(timezone.utc) - timedelta(hours=24)

def safe_list(gen, limit=50):
    results = []
    try:
        for item in gen:
            results.append(item)
            if len(results) >= limit:
                break
    except Exception:
        pass
    return results

# --- Commits on default branch ---
commits = []
for c in safe_list(repo.get_commits(since=since)):
    commits.append({
        "sha": c.sha[:7],
        "message": c.commit.message.split("\n")[0][:120],
        "author": c.commit.author.name,
        "date": c.commit.author.date.isoformat(),
        "url": c.html_url,
    })

# --- Pull requests (opened or updated in last 24h) ---
prs = []
for pr in safe_list(repo.get_pulls(state="all", sort="updated", direction="desc")):
    updated = pr.updated_at.replace(tzinfo=timezone.utc)
    if updated < since:
        break
    prs.append({
        "number": pr.number,
        "title": pr.title[:120],
        "state": pr.state,
        "merged": pr.merged,
        "author": pr.user.login,
        "updated_at": pr.updated_at.isoformat(),
        "url": pr.html_url,
        "review_comments": pr.review_comments,
        "draft": pr.draft,
    })

# --- Issues (opened or updated in last 24h) ---
issues = []
for issue in safe_list(repo.get_issues(state="all", sort="updated", direction="desc", since=since)):
    if issue.pull_request:
        continue
    issues.append({
        "number": issue.number,
        "title": issue.title[:120],
        "state": issue.state,
        "author": issue.user.login,
        "labels": [l.name for l in issue.labels],
        "updated_at": issue.updated_at.isoformat(),
        "url": issue.html_url,
    })

# --- CI / workflow runs ---
ci_runs = []
for run in safe_list(repo.get_workflow_runs(), limit=10):
    created = run.created_at.replace(tzinfo=timezone.utc)
    if created < since:
        continue
    ci_runs.append({
        "name": run.name,
        "status": run.status,
        "conclusion": run.conclusion,
        "branch": run.head_branch,
        "created_at": run.created_at.isoformat(),
        "url": run.html_url,
    })

# --- Changed files ---
changed_files = []
try:
    commits_list = list(repo.get_commits(since=since))
    if commits_list:
        oldest_sha = commits_list[-1].sha
        comparison = repo.compare(oldest_sha + "^", repo.default_branch)
        for f in comparison.files[:30]:
            changed_files.append({
                "filename": f.filename,
                "status": f.status,
                "additions": f.additions,
                "deletions": f.deletions,
            })
except Exception:
    pass

output = {
    "repo": REPO_NAME,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "window_hours": 24,
    "commits": commits,
    "pull_requests": prs,
    "issues": issues,
    "ci_runs": ci_runs,
    "changed_files": changed_files,
}

print(json.dumps(output, indent=2))
