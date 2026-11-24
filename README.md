# AI Atlas India: Content Engine (GPU cloud and AI infrastructure)

An AI content engine for one section of [AI Atlas India](https://aiatlasindia.com), built for Vyohm AI's
content-engine assignment. **Live: [gpu.aiatlasindia.com](https://gpu.aiatlasindia.com)**

The engine finds the questions Indian business owners ask about renting GPU and cloud compute, drafts answers from
provider pages with every fact quoted and sourced, and sends each draft to a real expert. **Nothing is published until
the expert approves it.** Published answers are shared on Bluesky, replies are drafted for a person to approve, and a
results screen suggests what to write next.

## How it works

| Step | What happens | Where |
|---|---|---|
| 1. Collect | Questions from Stack Exchange and Hacker News (official APIs), at most 20 new per run | `api/questions/` |
| 2. Rank | The AI scores each question as a buying question, gives a reason, merges duplicates | `api/questions/rank.py` |
| 3. Draft | The AI writes from 1-4 whole provider pages; every fact must quote its source word for word or the draft is rejected | `api/drafts/` |
| 4. Pre-check | The admin ticks each fact after opening its source (the link highlights the quote) | `/admin` |
| 5. Expert review | A one-time link, assigned to one expert, opens only with that expert's personal code. They approve, edit (title, search text, image text, answer) or reject | `api/review/`, `/review/<link>` |
| 6. Publish | The admin publishes approved answers (hard cap of 20 in code). Each page credits the expert who approved it | `api/pages/`, `/q/<slug>` |
| 7. Share | Bluesky posts and replies are AI-drafted; a person schedules every post and approves every reply | `api/social/`, `/admin?view=social` |
| 8. Results | AI-crawler and AI-assistant visits, GA4 and Search Console uploads, and AI suggestions for the next questions | `api/stats/`, `/admin?view=results` |

The AI calls go through one function, `llm()` (`api/core/llm/`), with a fallback across free models on Gemini, Groq and
OpenRouter. Drafting and ranking use the strongest list (`FALLBACK_BEST`) with JSON mode.

## Stack
- **Web** (`web/`): Next.js 16 (App Router, TypeScript), the public pages, the admin desk and the expert review page. On Vercel.
- **API** (`api/`): FastAPI on Python 3.13, plain SQL with `psycopg` on Neon Postgres (`api/db/schema.sql`). On Vercel.
- **Email**: Resend. **Social**: Bluesky (AT Protocol over HTTP). **Scheduler**: GitHub Actions (`.github/workflows/jobs.yml`).

## Run locally
```bash
npm --prefix web install && npm --prefix web run dev            # http://localhost:3000
python -m venv api/.venv
api/.venv/Scripts/python -m pip install -r api/requirements.txt
api/.venv/Scripts/python -m uvicorn main:app --app-dir api --reload --port 8000   # /health
```
Copy `api/.env.example` to `api/.env` and `web/.env.example` to `web/.env.local`, and fill them in. Create the tables
with `cd api && .venv/Scripts/python -m db.init_db`. To try the whole flow without touching live data, see "Local test
copy" in `docs/HANDOFF.md`.

## Tests
```bash
cd api && .venv/Scripts/python -m unittest tests.test_questions tests.test_drafts tests.test_review tests.test_social tests.test_stats -v
cd web && node --test lib/session.test.mjs && npm run lint && npm run build
```

## Rules enforced in code
- Only drafts with an expert's `approved` or `edited` decision can be published; the AI's version and the expert's are both kept.
- At most 20 published answers (`api/pages/pages.py`).
- Every fact carries its source link, an exact quote and the date it was checked.
- Bluesky: our own answers only, a person approves every reply, no automated follows, likes or reposts.
- No secrets, expert contact details or commenter data in the repo.

## Docs
- `docs/HANDOFF.md`: current state and next steps. `docs/DECISIONS.md`: every decision and why.
- `docs/ARCHITECTURE.md`: how the parts fit. `docs/GLOSSARY.md`: the terms used.
- `docs/expert-guide/`: the guide sent to expert reviewers (PDF and the real screens).
