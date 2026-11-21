# Handoff: read this first

_Last updated: 2026-11-20 (session 1)_

## Current state
- Scaffold only. `web/` is a minimal Next.js app with a placeholder home page showing the required header and footer. `api/` is a FastAPI app with `GET /health`.
- Docs written: `CLAUDE.md`, `docs/PROJECT_CONTEXT.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/GLOSSARY.md`, `README.md`.
- Verified on 2026-11-20: `npm --prefix web run lint` is clean; `npm --prefix web run build` passes, with `/` prerendered as static HTML containing the header link and the exact footer line; the API's `health()` returns `{"ok": True}`. Versions: Next 16.4.6, React 19.3, Tailwind 4.3, FastAPI 0.165, uvicorn 0.54.
- Initial commit `3d21a52` is on `main`. No remote has been added yet. Nothing is deployed.
- Waiting on Vyohm's setup email (section, subdomain, GA4 ID, Search Console access).
- **Session 2 (not committed):** backend foundation built. `api/core/` has `config.py`, `db.py` and `llm/` (`models.py` with the fallback order, `client.py` with `llm()`). `api/db/` has `schema.sql` (the `questions` table) and `init_db.py`. `/health` now reports `db`. Verified: Groq `gpt-oss-120b` and `gpt-oss-20b` answer; Gemini is skipped (no key yet); DB is not connected yet (no `DATABASE_URL`).

## Next actions (in order)
0. **User:** create `api/.env` from `api/.env.example`, add the Neon `DATABASE_URL`, the Gemini key and (optionally) the OpenRouter key. Then run `python -m db.init_db` and `python -m core.llm.client` from `api/`. Check your real free limits at aistudio.google.com/rate-limit and console.groq.com/settings/limits. Once the OpenRouter key is in, pick a `:free` model and add it to `FALLBACK`.
1. **User:** read the setup email. Note the section and subdomain, and update `web/lib/site.ts` and PROJECT_CONTEXT §3.
2. **User:** line up the expert (written consent to be named). Send Vyohm the open questions (PROJECT_CONTEXT §12).
3. **User:** read up on GA4, Search Console and the Bluesky app password (`docs/GLOSSARY.md`, group A).
4. **Agent and user:** run the Day-1 deploy test (ARCHITECTURE "Hosting") and push the repo to GitHub.
5. **Level 1:** About page, GA4 tag, sitemap and robots, Bluesky account with the bot label, live on the subdomain.

## Open questions and blockers
See PROJECT_CONTEXT §12. Blocker: no section or subdomain until the setup email arrives.

## What broke and how we fixed it (needed for the write-up)
_Add an entry each time something breaks: date, what broke, the root cause, the fix._
- 2026-11-20: `create-next-app` took over 10 minutes on the first run (slow npm install). No fix needed. Noted for reference.
- 2026-11-20: Groq returned 404 for `llama-3.3-70b-versatile`, even though its models page lists it. Root cause: the model isn't available to this account. Fix: replaced it with `openai/gpt-oss-20b`, which was tested and works. Lesson: test every model in `FALLBACK` with `python -m core.llm.client` instead of trusting the docs list.

## Session log
- **S1, 2026-11-20:** read the guide and email thread; agreed the stack (D1–D12); wrote the docs; scaffolded `web/` and `api/`.
- **S2, 2026-11-20:** agreed the workflow (plan first, build on "i understand now build"); built the DB connection and `llm()` with fallback across 3 providers (D13, D14).
