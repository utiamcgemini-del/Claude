#!/usr/bin/env python3
"""Daily cyber fraud & scam news email digest bot.

Tracks cyber fraud, data breaches, scams, AI-enabled scams/fraud, and
regulatory fines/enforcement actions.

Usage:
  python main.py          # Start scheduler (sends daily at SEND_TIMES_IST)
  python main.py --now    # Send digest immediately and exit
"""
import argparse
import sys

import config
from fetcher import fetch_articles
from summarizer import analyze_articles
from emailer import send_digest


def run_digest():
    print("[bot] Fetching cyber fraud / scam / breach articles...")
    articles = fetch_articles(top_n=config.TOP_N)
    print(f"[bot] Total keyword-relevant articles fetched: {len(articles)}")
    articles = analyze_articles(articles)
    send_digest(articles)


def main():
    parser = argparse.ArgumentParser(description="Cyber fraud & scam news email digest bot")
    parser.add_argument(
        "--now", action="store_true", help="Send digest immediately and exit"
    )
    args = parser.parse_args()

    if args.now:
        run_digest()
        return

    # Scheduled mode
    from zoneinfo import ZoneInfo
    from apscheduler.schedulers.blocking import BlockingScheduler

    ist = ZoneInfo("Asia/Kolkata")
    times = []
    for chunk in config.SEND_TIMES_IST.split(","):
        hour_str, minute_str = chunk.strip().split(":")
        times.append((int(hour_str), int(minute_str)))

    scheduler = BlockingScheduler(timezone=ist)
    for hour, minute in times:
        scheduler.add_job(run_digest, "cron", hour=hour, minute=minute, timezone=ist)

    times_display = ", ".join(f"{h:02d}:{m:02d}" for h, m in times)
    print(f"[bot] Scheduler started — digest will be sent daily at {times_display} IST")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("[bot] Scheduler stopped.")


if __name__ == "__main__":
    main()
