import json
import anthropic
import config

VALID_CATEGORIES = ["Data Breach", "Cyber Fraud", "Scam", "AI Scam/Fraud", "Regulatory Fine"]

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


def analyze_articles(articles: list[dict]) -> list[dict]:
    """Use Claude to filter, categorize, and rank fraud/scam/breach articles.

    Returns the enriched, sorted article list. Articles Claude judges to be
    off-topic (not about cyber fraud, breaches, scams, AI-enabled fraud, or
    regulatory fines/enforcement) are dropped.
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
                "keyword_categories": a.get("categories", []),
            }
            for i, a in enumerate(articles)
        ],
        indent=2,
    )

    prompt = f"""You are a fraud-intelligence analyst curating a digest focused ONLY on:
- Cyber fraud (BEC, payment/invoice/wire fraud, account takeover, identity theft)
- Cybersecurity data breaches
- Scams (phishing, romance/investment/tech-support scams, impersonation)
- AI-enabled scams or fraud (deepfakes, voice cloning, generative-AI fraud)
- Regulatory fines / enforcement actions (fines, settlements, sanctions, consent orders)

Each article below was pre-filtered by keyword matching (see "keyword_categories"), but that
filter is noisy. Your job:
1. Decide if the article is truly ON-TOPIC for the five categories above. If it's just a generic
   vulnerability/patch/malware story with no fraud, scam, breach, or regulatory-fine angle, mark
   it NOT relevant.
2. For relevant articles: assign exactly one "category" from {VALID_CATEGORIES} (the best fit).
3. Score importance 1-10 (10 = major breach/fine/scam campaign with broad impact, 1 = minor/routine).
4. Write a concise 1-2 sentence ai_summary highlighting the fraud/scam/breach/regulatory angle.
5. Return ONLY valid JSON — an array of objects with fields: id, relevant, category, importance, ai_summary.
   For irrelevant articles, still include the id with relevant=false (other fields can be omitted).

Articles:
{articles_text}

Return JSON only, no prose. Example format:
[{{"id": 0, "relevant": true, "category": "Scam", "importance": 7, "ai_summary": "..."}},
 {{"id": 1, "relevant": false}}]"""

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
        info = ranking_map.get(i)
        if info is None:
            continue
        if not info.get("relevant", False):
            continue
        category = info.get("category")
        if category not in VALID_CATEGORIES:
            category = (article.get("categories") or ["Scam"])[0]
        enriched.append(
            {
                **article,
                "category": category,
                "importance": info.get("importance", 5),
                "ai_summary": info.get("ai_summary", article["summary"]),
            }
        )

    enriched.sort(key=lambda a: a["importance"], reverse=True)
    print(f"[summarizer] Claude kept {len(enriched)}/{len(articles)} articles as on-topic.")
    return enriched
