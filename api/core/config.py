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
