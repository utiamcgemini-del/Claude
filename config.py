import os
from dotenv import load_dotenv

load_dotenv()

RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]
SENDER_EMAIL = os.environ["SENDER_EMAIL"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SEND_HOUR = int(os.getenv("SEND_HOUR", "8"))
TOP_N = int(os.getenv("TOP_N", "5"))
