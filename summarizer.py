import json
import anthropic
import config


_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


def analyze_articles(articles: list[dict]) -> list[dict]:
    """Use Claude to rank articles by importance and rewrite summaries.

    Returns the same article list, sorted by AI-assigned importance score,
    with enriched 'ai_summary' and 'importance' fields added to each article.
    """
    if not articles:
        return articles

    client = _get_client()

    articles_text = json.dumps(
        [
            {
                "id": i,
                "source": a["source"],
                "title": a["title"],
                "link": a["link"],
                "published": a["published"],
                "summary": a["summary"],
            }
            for i, a in enumerate(articles)
        ],
        indent=2,
    )

    prompt = f"""You are a cybersecurity expert analyst tasked with curating a daily digest.

Below is a list of cybersecurity articles fetched from RSS feeds today.

Your job:
1. Score each article from 1-10 for importance (10 = critical vulnerability/breach, 1 = minor/routine).
2. Write a concise 1-2 sentence AI summary highlighting the key security implication.
3. Return ONLY valid JSON — an array of objects with fields: id, importance, ai_summary.

Articles:
{articles_text}

Return JSON only, no prose. Example format:
[{{"id": 0, "importance": 8, "ai_summary": "..."}}]"""

    print("[summarizer] Sending articles to Claude for analysis...")
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    )

    raw = ""
    for block in response.content:
        if block.type == "text":
            raw = block.text
            break

    try:
        rankings = json.loads(raw)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            rankings = json.loads(match.group())
        else:
            print("[summarizer] WARNING: Could not parse Claude response; returning original articles.")
            return articles

    ranking_map = {r["id"]: r for r in rankings}

    enriched = []
    for i, article in enumerate(articles):
        info = ranking_map.get(i, {})
        enriched.append(
            {
                **article,
                "importance": info.get("importance", 5),
                "ai_summary": info.get("ai_summary", article["summary"]),
            }
        )

    enriched.sort(key=lambda a: a["importance"], reverse=True)
    print(f"[summarizer] Claude analyzed {len(enriched)} articles.")
    return enriched
