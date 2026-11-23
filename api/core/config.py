"""All settings, read from environment variables (api/.env when running locally)."""
import os
from pathlib import Path

from dotenv import load_dotenv

# api/.env sits one folder above this file's folder (core/).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Password for the /jobs/* endpoints. The scheduler sends it as "Authorization: Bearer <secret>".
CRON_SECRET = os.getenv("CRON_SECRET", "")

# Level 4: emailing the expert through Resend. With no key or no address, the API hands the link back to the
# admin screen instead, so you can test the review page yourself.
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EXPERT_EMAIL = os.getenv("EXPERT_EMAIL", "")  # kept here only: never in the repo (the rules)
MAIL_FROM = os.getenv("MAIL_FROM", "AI Atlas India <onboarding@resend.dev>")  # Resend's test sender
SITE_URL = os.getenv("SITE_URL", "http://localhost:3000")  # where the review link and the answer pages live

# Level 5: the Bluesky account. Use an APP password (Settings > Privacy and security > App passwords),
# never the account's real password: an app password can be revoked on its own.
BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE", "")              # e.g. gpu-aiatlasindia.bsky.social
BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD", "")

# "dev" = light, fast models while we build. "final" = the stronger models, set it before submitting.
LLM_MODE = os.getenv("LLM_MODE", "dev")
