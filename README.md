# AI Atlas India: Content Engine

An AI content engine for one section of [AI Atlas India](https://aiatlasindia.com), built for the Vyohm AI software-track assignment. The AI finds questions and drafts answers, a real expert approves every answer before it goes live, and the engine shares published answers on Bluesky.

**Status:** scaffold only. See `docs/HANDOFF.md`.

## Layout
```
web/    Next.js: public pages and admin
api/    FastAPI: AI drafting, expert review, social, metrics
docs/   PROJECT_CONTEXT, ARCHITECTURE, DECISIONS, HANDOFF, GLOSSARY
```

## Run locally
```bash
npm --prefix web install && npm --prefix web run dev        # http://localhost:3000
python -m venv api/.venv
api/.venv/Scripts/python -m pip install -r api/requirements.txt
api/.venv/Scripts/python -m uvicorn main:app --app-dir api --reload --port 8000   # /health
```
