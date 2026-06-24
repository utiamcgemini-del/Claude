import feedparser
import time
from datetime import datetime, timezone, timedelta

FEEDS = [
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("SecurityWeek", "https://feeds.feedburner.com/Securityweek"),
    ("SANS Internet Stormcast", "https://isc.sans.edu/rssfeed_full.xml"),
    ("Bleeping Computer", "https://www.bleepingcomputer.com/feed/"),
]

CUTOFF_HOURS = 24


def _parse_time(entry) -> datetime:
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    if t:
        return datetime(*t[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def fetch_articles(top_n: int = 5) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=CUTOFF_HOURS)
    results = []

    for source_name, url in FEEDS:
        try:
            feed = feedparser.parse(url)
            entries = feed.entries or []
            recent = [e for e in entries if _parse_time(e) >= cutoff]
            # Fall back to most recent if nothing in last 24 h (e.g. low-volume feeds)
            if not recent:
                recent = entries
            recent.sort(key=_parse_time, reverse=True)
            for entry in recent[:top_n]:
                summary = entry.get("summary", "")
                # Strip HTML tags simply
                import re
                summary = re.sub(r"<[^>]+>", "", summary)[:300]
                results.append(
                    {
                        "source": source_name,
                        "title": entry.get("title", "(no title)"),
                        "link": entry.get("link", ""),
                        "summary": summary.strip(),
                        "published": _parse_time(entry).strftime("%Y-%m-%d %H:%M UTC"),
                    }
                )
            print(f"[fetcher] {source_name}: {len(recent[:top_n])} articles")
        except Exception as exc:
            print(f"[fetcher] ERROR fetching {source_name}: {exc}")

    return results
