# GitHub Project Monitor — project-pop

Automated daily digest for your GitHub repo. Every morning at 9 AM UTC, an AI agent scans your repo for commits, PRs, issues, CI failures, and file changes — then posts a summary as a GitHub Issue and sends it to your email.

---

## How it works

```
9 AM UTC → GitHub Actions wakes up
         → collect_activity.py fetches last 24h of data
         → generate_digest.py calls Claude AI to write the summary
         → deliver_issue.py posts it as a GitHub Issue
         → deliver_email.py sends the HTML email
```

---

## Setup (5 minutes)

### Step 1 — Add your Anthropic API key

Go to your repo on GitHub:
**Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your key from https://console.anthropic.com |

### Step 2 — Add email secrets

| Secret name | Example value | Notes |
|---|---|---|
| `SMTP_HOST` | `smtp.gmail.com` | Your email provider's SMTP host |
| `SMTP_PORT` | `587` | Usually 587 (TLS) |
| `SMTP_USER` | `you@gmail.com` | The address that sends the email |
| `SMTP_PASS` | `abcd efgh ijkl mnop` | For Gmail: use an App Password |
| `DIGEST_EMAIL_TO` | `you@gmail.com` | Delivery address |

> **Gmail users:** Google Account → Security → 2-Step Verification → App passwords.

### Step 3 — Test it manually

Go to: **Actions → Daily Project Digest → Run workflow**

---

## File structure

```
.github/workflows/daily-digest.yml   ← scheduler
scripts/collect_activity.py          ← gathers GitHub data
scripts/generate_digest.py           ← calls Claude AI
scripts/deliver_issue.py             ← posts GitHub Issue
scripts/deliver_email.py             ← sends email
```

---

*Powered by Claude AI · Built with GitHub Actions*
