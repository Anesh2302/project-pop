#!/usr/bin/env python3
import os, json, sys, anthropic
from datetime import datetime, timezone

def load_activity(path):
    with open(path) as f:
        return json.load(f)

def build_prompt(activity):
    repo = activity["repo"]
    commits = activity.get("commits", [])
    prs = activity.get("pull_requests", [])
    issues = activity.get("issues", [])
    ci_runs = activity.get("ci_runs", [])
    changed_files = activity.get("changed_files", [])
    failed_ci = [r for r in ci_runs if r.get("conclusion") == "failure"]
    merged_prs = [p for p in prs if p.get("merged")]
    open_prs = [p for p in prs if p["state"] == "open" and not p.get("merged")]
    bug_issues = [i for i in issues if any(l in ["bug","critical","blocker"] for l in i.get("labels",[]))]
    data_summary = f"""
Repository: {repo}
COMMITS ({len(commits)}): {json.dumps(commits[:10], indent=2)}
PULL REQUESTS ({len(prs)}): Merged={len(merged_prs)} Open={len(open_prs)}
{json.dumps(prs[:10], indent=2)}
ISSUES ({len(issues)}): Bugs={len(bug_issues)}
{json.dumps(issues[:10], indent=2)}
CI RUNS ({len(ci_runs)}): Failed={len(failed_ci)}
{json.dumps(ci_runs, indent=2)}
CHANGED FILES ({len(changed_files)}):
{json.dumps(changed_files[:20], indent=2)}
"""
    return f"""You are a senior engineering lead. Analyze the last 24h of GitHub activity and write a concise daily digest in Markdown.

Structure:
# Daily Digest — {repo}
*{datetime.now(timezone.utc).strftime("%A, %B %-d %Y")}*
## Summary
## Commits & code changes
## Pull requests
## Issues
## CI / build status
## Action items

Rules: Be direct. Use checkmark for good, warning for needs attention, x-mark for failures. Keep under 500 words.

Data:
{data_summary}"""

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    activity = load_activity(sys.argv[1])
    prompt = build_prompt(activity)
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=1024,
                                     messages=[{"role": "user", "content": prompt}])
    print(message.content[0].text)

if __name__ == "__main__":
    main()
