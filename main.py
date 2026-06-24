#!/usr/bin/env python3
"""Daily cybersecurity email digest bot.

Usage:
  python main.py          # Start scheduler (sends at SEND_HOUR UTC daily)
  python main.py --now    # Send digest immediately and exit
"""
import argparse
import sys

import config
from fetcher import fetch_articles
from emailer import send_digest


def run_digest():
    print("[bot] Fetching cybersecurity articles...")
    articles = fetch_articles(top_n=config.TOP_N)
    print(f"[bot] Total articles fetched: {len(articles)}")
    send_digest(articles)


def main():
    parser = argparse.ArgumentParser(description="Cybersecurity email digest bot")
    parser.add_argument(
        "--now", action="store_true", help="Send digest immediately and exit"
    )
    args = parser.parse_args()

    if args.now:
        run_digest()
        return

    # Scheduled mode
    from apscheduler.schedulers.blocking import BlockingScheduler

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(run_digest, "cron", hour=config.SEND_HOUR, minute=0)
    print(
        f"[bot] Scheduler started — digest will be sent daily at {config.SEND_HOUR:02d}:00 UTC"
    )
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("[bot] Scheduler stopped.")


if __name__ == "__main__":
    main()
