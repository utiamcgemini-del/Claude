import re
import feedparser
from datetime import datetime, timezone, timedelta

import config

FEEDS = [
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
    ("SecurityWeek", "https://feeds.feedburner.com/Securityweek"),
    ("Sophos News", "https://news.sophos.com/en-us/feed/"),
    ("Graham Cluley", "https://grahamcluley.com/feed/"),
    ("Malwarebytes Labs", "https://www.malwarebytes.com/blog/feed/index.xml"),
    ("FTC Consumer Alerts", "https://consumer.ftc.gov/consumer-alerts/feed"),
]

# Only articles matching at least one of these keyword groups are kept.
# Each match tags the article with its topic category for downstream
# analysis, grouping, and display.
TOPIC_KEYWORDS = {
    "Data Breach": [
        "data breach", "breach", "data leak", "leaked database",
        "exposed database", "records exposed", "compromised data",
        "stolen data", "hacked database",
    ],
    "Cyber Fraud": [
        "cyber fraud", "wire fraud", "business email compromise", "bec scam",
        "invoice fraud", "payment fraud", "account takeover", "identity theft",
        "bank fraud",
    ],
    "Scam": [
        "scam", "scammer", "phishing", "smishing", "vishing", "fake invoice",
        "impersonation scam", "romance scam", "investment scam",
        "tech support scam", "pig butchering", "fraudulent website",
    ],
    "AI Scam/Fraud": [
        "ai scam", "deepfake", "voice clone", "voice cloning",
        "ai-generated scam", "ai fraud", "artificial intelligence scam",
        "synthetic voice", "chatgpt scam", "generative ai fraud", "ai voice fraud",
    ],
    "Regulatory Fine": [
        "fined", "fine of", "regulatory fine", "penalty", "settles with",
        "settlement", "enforcement action", "sanctioned", "gdpr fine",
        "ftc order", "sec charges", "consent order", "civil penalty",
        "class action",
    ],
}


def _parse_time(entry) -> datetime:
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    if t:
        return datetime(*t[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def _match_categories(text: str) -> list[str]:
    text = text.lower()
    return [cat for cat, kws in TOPIC_KEYWORDS.items() if any(kw in text for kw in kws)]


def fetch_articles(top_n: int = 5) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=config.CUTOFF_HOURS)
    results = []

    for source_name, url in FEEDS:
        try:
            feed = feedparser.parse(url)
            entries = feed.entries or []

            relevant = []
            for entry in entries:
                title = entry.get("title", "(no title)")
                summary = re.sub(r"<[^>]+>", "", entry.get("summary", ""))[:300].strip()
                categories = _match_categories(f"{title} {summary}")
                if not categories:
                    continue
                relevant.append(
                    {
                        "source": source_name,
                        "title": title,
                        "link": entry.get("link", ""),
                        "summary": summary,
                        "published": _parse_time(entry).strftime("%Y-%m-%d %H:%M UTC"),
                        "_published_dt": _parse_time(entry),
                        "categories": categories,
                    }
                )

            recent = [a for a in relevant if a["_published_dt"] >= cutoff]
            # Fall back to most recent relevant articles if none in the cutoff window
            if not recent:
                recent = relevant
            recent.sort(key=lambda a: a["_published_dt"], reverse=True)

            for a in recent[:top_n]:
                del a["_published_dt"]
                results.append(a)

            print(f"[fetcher] {source_name}: {len(recent[:top_n])} relevant articles")
        except Exception as exc:
            print(f"[fetcher] ERROR fetching {source_name}: {exc}")

    return results
