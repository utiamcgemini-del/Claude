import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config


_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; background: #f4f4f4; color: #222; margin: 0; padding: 20px; }}
  .container {{ max-width: 680px; margin: 0 auto; background: #fff; border-radius: 8px; overflow: hidden; }}
  .header {{ background: #1a1a2e; color: #e0e0e0; padding: 24px 32px; }}
  .header h1 {{ margin: 0; font-size: 22px; }}
  .header p {{ margin: 4px 0 0; font-size: 13px; color: #aaa; }}
  .source-block {{ padding: 20px 32px; border-bottom: 1px solid #eee; }}
  .source-block h2 {{ font-size: 15px; color: #c0392b; margin: 0 0 12px; text-transform: uppercase; letter-spacing: 1px; }}
  .article {{ margin-bottom: 14px; }}
  .article a {{ font-size: 15px; font-weight: bold; color: #1a1a2e; text-decoration: none; }}
  .article a:hover {{ text-decoration: underline; }}
  .meta {{ font-size: 11px; color: #888; margin: 2px 0 4px; }}
  .snippet {{ font-size: 13px; color: #555; }}
  .footer {{ padding: 16px 32px; font-size: 11px; color: #aaa; text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>&#128737; Daily Cybersecurity Digest</h1>
    <p>{date}</p>
  </div>
  {sections}
  <div class="footer">
    You are receiving this because you subscribed to the daily cybersecurity digest bot.
  </div>
</div>
</body>
</html>
"""

_SECTION_TEMPLATE = """\
<div class="source-block">
  <h2>{source}</h2>
  {articles}
</div>
"""

_ARTICLE_TEMPLATE = """\
<div class="article">
  <a href="{link}" target="_blank">{title}</a>
  <div class="meta">{published}{importance_badge}</div>
  <div class="snippet">{summary}</div>
</div>
"""


def _importance_badge(score) -> str:
    if score is None:
        return ""
    score = int(score)
    if score >= 8:
        color, label = "#c0392b", f"&#9888; Critical ({score}/10)"
    elif score >= 5:
        color, label = "#e67e22", f"&#9888; Medium ({score}/10)"
    else:
        color, label = "#27ae60", f"({score}/10)"
    return f' &nbsp;<span style="color:{color};font-weight:bold;font-size:11px">{label}</span>'


def _build_html(articles: list[dict]) -> str:
    date_str = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
    grouped: dict[str, list[dict]] = {}
    for a in articles:
        grouped.setdefault(a["source"], []).append(a)

    sections = ""
    for source, items in grouped.items():
        arts = "".join(
            _ARTICLE_TEMPLATE.format(
                link=i["link"],
                title=i["title"],
                published=i["published"],
                summary=i.get("ai_summary") or i["summary"] or "No summary available.",
                importance_badge=_importance_badge(i.get("importance")),
            )
            for i in items
        )
        sections += _SECTION_TEMPLATE.format(source=source, articles=arts)

    return _HTML_TEMPLATE.format(date=date_str, sections=sections)


def _build_plain(articles: list[dict]) -> str:
    lines = [
        f"Daily Cybersecurity Digest — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "=" * 60,
        "",
    ]
    grouped: dict[str, list[dict]] = {}
    for a in articles:
        grouped.setdefault(a["source"], []).append(a)

    for source, items in grouped.items():
        lines.append(f"[ {source} ]")
        for i in items:
            lines.append(f"  * {i['title']}")
            lines.append(f"    {i['link']}")
            lines.append(f"    {i['published']}")
            if i["summary"]:
                lines.append(f"    {i['summary'][:200]}")
            lines.append("")
    return "\n".join(lines)


def send_digest(articles: list[dict]) -> None:
    if not articles:
        print("[emailer] No articles to send.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = (
        f"Cybersecurity Digest — {datetime.now(timezone.utc).strftime('%b %d, %Y')}"
    )
    msg["From"] = config.SENDER_EMAIL
    msg["To"] = config.RECIPIENT_EMAIL

    msg.attach(MIMEText(_build_plain(articles), "plain"))
    msg.attach(MIMEText(_build_html(articles), "html"))

    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(config.SENDER_EMAIL, config.SMTP_PASSWORD)
        smtp.sendmail(config.SENDER_EMAIL, config.RECIPIENT_EMAIL, msg.as_string())

    print(f"[emailer] Digest sent to {config.RECIPIENT_EMAIL} ({len(articles)} articles)")
