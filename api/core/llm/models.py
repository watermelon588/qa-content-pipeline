"""Which LLMs we use, and in what order. Change models here only."""
from core.config import GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY

# All three providers accept the OpenAI chat API, so only the address and the key differ.
# Sources (checked 2026-11-20):
#   https://ai.google.dev/gemini-api/docs/openai
#   https://console.groq.com/docs/openai
#   https://openrouter.ai/docs/quickstart
PROVIDERS = {
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "api_key": GEMINI_API_KEY},
    "groq": {"base_url": "https://api.groq.com/openai/v1", "api_key": GROQ_API_KEY},
    "openrouter": {"base_url": "https://openrouter.ai/api/v1", "api_key": OPENROUTER_API_KEY},
}

# Tried top to bottom. If one fails (rate limit, outage), the next one is used.
FALLBACK = [
    ("gemini", "gemini-3.8-flash"),          # best quality, newest stable Flash
    ("groq", "openai/gpt-oss-120b"),         # fast; only 8K tokens per minute on the free plan
    ("groq", "openai/gpt-oss-20b"),          # smaller sibling; Groq's limits are per model, so it has its own quota
    ("gemini", "gemini-3.5-flash-lite"),     # lighter Gemini, last resort
    # ("openrouter", "..."),                 # add a ":free" model once the OpenRouter key is in .env
]
