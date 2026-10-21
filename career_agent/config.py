import os

from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
APP_API_KEY = os.getenv("APP_API_KEY", "")
DATABASE_PATH = os.getenv("DATABASE_PATH", "career_agent.sqlite3")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MONITOR_INTERVAL_SECONDS = max(300, int(os.getenv("MONITOR_INTERVAL_SECONDS", "300")))
ALERT_MODE = os.getenv("ALERT_MODE", "immediate").strip().lower()
MONITOR_ENABLED = os.getenv("MONITOR_ENABLED", "false").strip().lower() in {"1", "true", "yes"}
ALERT_WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "").strip()
