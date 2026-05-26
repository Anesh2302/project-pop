
#!/usr/bin/env python3
"""
collect_activity.py
Fetches activity from ALL Work-Flow- repos for the last 24 hours.
Outputs a single JSON blob with per-repo sections.
"""
import os
import json
from datetime import datetime, timedelta, timezone
from github import Github

OWNER      = os.environ["GITHUB_OWNER"]
REPO_NAMES = os.environ["WATCHED_REPOS"].split(",")
TOKEN      = os.environ["GITHUB_TOKEN"]

g     = Github(TOKEN)
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

def collect_repo(repo_name: str) -> dict:
    full_name = f"{OWNER}/{repo_name}"
    try:
        repo = g.get_repo(full_name)
    except Exception as e:
        return {"repo": full_name, "error": str(e)}

    commits = []
    for c in safe_list(repo.get_commits(since=since)):
        commits.append({
            "sha": c.sha[:7],
            "message": c.commit.message.split("\n")[0][:120],
            "author": c.commit.author.name,
            "date": c.commit.author.date.isoformat(),
            "url": c.html_url,
        })

    prs = []
    for pr in safe_list(repo.get_pulls(state="all", sort="updated", direction="desc")):
        if pr.updated_at.replace(tzinfo=timezone.utc) < since:
            break
        prs.append({
            "number": pr.number,
            "title": pr.title[:120],
            "state": pr.state,
            "merged": pr.merged,
            "author": pr.user.login,
            "updated_at": pr.updated_at.isoformat(),
            "url": pr.html_url,
            "draft": pr.draft,
        })

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

    ci_runs = []
    for run in safe_list(repo.get_workflow_runs(), limit=5):
        if run.created_at.replace(tzinfo=timezone.utc) < since:
            continue
        ci_runs.append({
            "name": run.name,
            "status": run.status,
            "conclusion": run.conclusion,
            "branch": run.head_branch,
            "created_at": run.created_at.isoformat(),
            "url": run.html_url,
        })

    changed_files = []
    try:
        commits_list = list(repo.get_commits(since=since))
        if commits_list:
            oldest_sha = commits_list[-1].sha
            comparison = repo.compare(oldest_sha + "^", repo.default_branch)
            for f in comparison.files[:20]:
                changed_files.append({
                    "filename": f.filename,
                    "status": f.status,
                    "additions": f.additions,
                    "deletions": f.deletions,
                })
    except Exception:
        pass

    return {
        "repo": full_name,
        "url": repo.html_url,
        "default_branch": repo.default_branch,
        "commits": commits,
        "pull_requests": prs,
        "issues": issues,
        "ci_runs": ci_runs,
        "changed_files": changed_files,
    }

repos_data = [collect_repo(name.strip()) for name in REPO_NAMES]

output = {
    "owner": OWNER,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "window_hours": 24,
    "repos": repos_data,
}

print(json.dumps(output, indent=2))
