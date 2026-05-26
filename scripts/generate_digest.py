#!/usr/bin/env python3
import os
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

def load_activity(path: str) -> dict:
    with open(path) as f:
        return json.load(f)

def repo_summary(r: dict) -> str:
    if "error" in r:
        return f"### {r['repo']}\n⚠️ Could not fetch: {r['error']}\n"
    commits   = r.get("commits", [])
    prs       = r.get("pull_requests", [])
    issues    = r.get("issues", [])
    ci_runs   = r.get("ci_runs", [])
    files     = r.get("changed_files", [])
    failed_ci = [x for x in ci_runs if x.get("conclusion") == "failure"]
    merged_pr = [p for p in prs if p.get("merged")]
    open_pr   = [p for p in prs if p["state"] == "open" and not p.get("merged")]
    bugs      = [i for i in issues if any(l in ["bug","critical","blocker"] for l in i.get("labels", []))]
    return f"""
### {r['repo']}
Commits: {len(commits)} | PRs open: {len(open_pr)} merged: {len(merged_pr)} | Issues: {len(issues)} (bugs: {len(bugs)}) | CI failures: {len(failed_ci)} | Files changed: {len(files)}
Recent commits: {json.dumps([c['message'] for c in commits[:5]])}
CI: {json.dumps([{"name": x["name"], "conclusion": x["conclusion"]} for x in ci_runs])}
Changed files: {json.dumps([f['filename'] for f in files[:10]])}
"""

def build_prompt(activity: dict) -> str:
    owner         = activity["owner"]
    window        = activity["window_hours"]
    generated     = activity["generated_at"]
    repos         = activity.get("repos", [])
    total_commits = sum(len(r.get("commits", [])) for r in repos)
    total_prs     = sum(len(r.get("pull_requests", [])) for r in repos)
    total_issues  = sum(len(r.get("issues", [])) for r in repos)
    active_repos  = [r["repo"].split("/")[-1] for r in repos if r.get("commits")]
    sections      = "\n".join(repo_summary(r) for r in repos)
    return f"""You are a senior engineering lead reviewing GitHub activity.
Developer: {owner} | Period: last {window} hours | Generated: {generated}
Totals: {total_commits} commits, {total_prs} PRs, {total_issues} issues across {len(repos)} repos.
Active repos: {active_repos}

{sections}

Write a daily digest with these sections:
# Daily Digest — {owner}/Work-Flow-
## Overall pulse
## Project activity
## Spotlight: wins & concerns
## Action items

Rules: ✅ good ⚠️ needs attention ❌ blocker. Under 600 words.
"""

def main():
    if len(sys.argv) < 2:
        print("Usage: generate_digest.py <activity.json>", file=sys.stderr)
        sys.exit(1)

    activity = load_activity(sys.argv[1])
    prompt   = build_prompt(activity)
    api_key  = os.environ.get("GEMINI_API_KEY", "").strip()

    if not api_key:
        print("ERROR: GEMINI_API_KEY is empty or not set", file=sys.stderr)
        sys.exit(1)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        print(data["candidates"][0]["content"]["parts"][0]["text"])
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"ERROR {e.code}: {body}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
