# GitHub Project Monitor — project-pop

Automated daily digest. Every morning at 9 AM UTC, an AI agent scans your repo and posts a summary as a GitHub Issue and email.

## Setup (5 minutes)

### 1 — Add secrets in GitHub
Go to **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | From https://console.anthropic.com |
| `SMTP_HOST` | e.g. `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | Your sending email |
| `SMTP_PASS` | Gmail: use an App Password |
| `DIGEST_EMAIL_TO` | Recipient email |

### 2 — Test it manually
Go to **Actions → Daily Project Digest → Run workflow**

## File structure
```
.github/workflows/daily-digest.yml  ← scheduler
scripts/collect_activity.py         ← fetches GitHub data
scripts/generate_digest.py          ← calls Claude AI
scripts/deliver_issue.py            ← posts GitHub Issue
scripts/deliver_email.py            ← sends HTML email
```

*Powered by Claude AI · Built with GitHub Actions*
