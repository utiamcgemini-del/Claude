import os
from dotenv import load_dotenv

load_dotenv()

RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]
SENDER_EMAIL = os.environ["SENDER_EMAIL"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
# Comma-separated HH:MM times (24h, India Standard Time) to send the digest daily.
SEND_TIMES_IST = os.getenv("SEND_TIMES_IST", "08:45,18:45")
TOP_N = int(os.getenv("TOP_N", "5"))
CUTOFF_HOURS = int(os.getenv("CUTOFF_HOURS", "48"))
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
