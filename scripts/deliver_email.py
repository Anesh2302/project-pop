#!/usr/bin/env python3
"""
deliver_email.py
Sends the digest as a formatted HTML email via SMTP.
Usage: python deliver_email.py digest.md

Required env vars:
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
  DIGEST_EMAIL_TO (comma-separated)
  REPO_NAME
"""

import os
import sys
import smtplib
import re
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def build_html(md: str, repo: str) -> str:
    today = datetime.now(timezone.utc).strftime("%A, %B %-d %Y")
    body_lines = []
    in_list = False
    for line in md.split("\n"):
        if line.startswith("# "):
            if in_list: body_lines.append("</ul>"); in_list = False
            body_lines.append(f"<h1 style='color:#0d1117;font-size:22px;margin:0 0 4px'>{line[2:]}</h1>")
        elif line.startswith("## "):
            if in_list: body_lines.append("</ul>"); in_list = False
            body_lines.append(f"<h2 style='color:#0d1117;font-size:15px;font-weight:600;margin:20px 0 6px;border-bottom:1px solid #e5e7eb;padding-bottom:4px'>{line[3:]}</h2>")
        elif line.strip() == "---":
            if in_list: body_lines.append("</ul>"); in_list = False
            body_lines.append("<hr style='border:none;border-top:1px solid #e5e7eb;margin:20px 0'>")
        elif line.startswith("- ") or line.startswith("* "):
            if not in_list:
                body_lines.append("<ul style='margin:6px 0;padding-left:20px'>")
                in_list = True
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line[2:])
            body_lines.append(f"<li style='margin:4px 0;color:#374151;font-size:14px'>{content}</li>")
        elif line.startswith("*") and line.endswith("*") and len(line) > 2:
            if in_list: body_lines.append("</ul>"); in_list = False
            body_lines.append(f"<p style='color:#6b7280;font-size:13px;margin:0 0 10px'>{line[1:-1]}</p>")
        elif line.strip() == "":
            if in_list: body_lines.append("</ul>"); in_list = False
        else:
            if in_list: body_lines.append("</ul>"); in_list = False
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            if text.strip():
                body_lines.append(f"<p style='color:#374151;margin:4px 0;line-height:1.6;font-size:14px'>{text}</p>")
    if in_list:
        body_lines.append("</ul>")
    body_html = "\n".join(body_lines)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6;padding:32px 16px">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;border:1px solid #e5e7eb;overflow:hidden;max-width:600px">
        <tr><td style="background:#0d1117;padding:20px 28px;color:#ffffff">
          <span style="font-size:13px;opacity:0.6">GitHub Project Monitor</span><br>
          <span style="font-size:18px;font-weight:600">{repo}</span>
          <span style="float:right;font-size:13px;opacity:0.6;line-height:2.4">{today}</span>
        </td></tr>
        <tr><td style="padding:24px 28px">{body_html}</td></tr>
        <tr><td style="background:#f9fafb;padding:14px 28px;border-top:1px solid #e5e7eb">
          <span style="font-size:12px;color:#9ca3af">Automated daily digest · {repo} · Powered by Claude AI</span>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>"""


def main():
    if len(sys.argv) < 2:
        print("Usage: deliver_email.py <digest.md>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        md = f.read()

    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", 587))
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASS"]
    to_addresses = [a.strip() for a in os.environ["DIGEST_EMAIL_TO"].split(",")]
    repo = os.environ.get("REPO_NAME", "project-pop")

    today = datetime.now(timezone.utc).strftime("%A, %B %-d %Y")
    subject = f"Daily Digest — {repo} · {today}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = ", ".join(to_addresses)
    msg.attach(MIMEText(md, "plain"))
    msg.attach(MIMEText(build_html(md, repo), "html"))

    with smtplib.SMTP(host, port) as server:
        server.ehlo()
        server.starttls()
        server.login(user, password)
        server.sendmail(user, to_addresses, msg.as_string())

    print(f"Email sent to: {', '.join(to_addresses)}")


if __name__ == "__main__":
    main()
