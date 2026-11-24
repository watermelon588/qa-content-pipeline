# AI Atlas India — Content Engine (Vyohm AI virtual assignment)

An AI content engine for one section of aiatlasindia.com. The AI finds the questions Indian business owners ask and drafts answers. A real expert approves every answer before it goes live. The engine then posts published answers to Bluesky, drafts replies, and suggests what to post next.

## Read at every session start (in this order)
1. `docs/HANDOFF.md`: current state, next action, open questions. **Start here.**
2. `docs/PROJECT_CONTEXT.md`: the assignment, the rules, the checkpoints, and everything decided with the user.
3. `docs/ARCHITECTURE.md` and `docs/DECISIONS.md`: read these only when touching structure or revisiting a choice.
4. Source PDF: `Vyohm_AI_Content_Engine_Candidate_Guide.pdf`. It is the final word on the rules. Extract text with `PYTHONIOENCODING=utf-8 python -c "import pypdf; ..."` (poppler is not installed).

Before writing Next.js code, read `web/AGENTS.md`. Next 16 has breaking changes, and its bundled docs are in `web/node_modules/next/dist/docs/`.

The user's global `~/.claude/CLAUDE.md` skill routine still applies. Say which skills you loaded.

## Hard rules (breaking any of them disqualifies the entry, so enforce them in code too)
- Nothing is published unless its status is `approved` by the expert. Keep the before and after versions.
- Publish **at most 20 answers in total** (target 8–10). Enforce the cap in code.
- Every page has: "AI Atlas India" linking to aiatlasindia.com in the header, the section name, and the exact footer ownership line (see PROJECT_CONTEXT §4).
- Every fact about a provider has a source link and the date it was checked. If it can't be confirmed, leave it out.
- Social: post only our own answers. Reply only to people who reply to or mention us. **A human approves every reply.** No automated follows, likes, reposts or DMs.
- No scraping of Google results, "People also ask" or Quora. No Reddit (no new API access). Use official APIs or exports only.
- No secrets, no expert contact details, and no commenter data in the repo, logs or demo video. Store commenter data minimally and delete it when the assignment ends.
- Never fake reach (no friends clicking, no planted links).

## Working with this user
- The user is a 3rd-year CSE student. Exams run **30 Nov – 15 Dec 2026**, so the real build deadline is **Sun 29 Nov**. They want minimum effort and a top-3 finish.
- Our section is **GPU cloud and AI infrastructure in India** at `gpu.aiatlasindia.com` (confirmed 22 Nov). Vyohm's results window is 23 Nov – 2 Dec, official deadline 2 Dec. The public pages copy the hub's design system (DECISIONS D15), so match it rather than inventing a look.
- The user must be able to **explain every line** in the Dec 4 code-walkthrough call. Keep code small and boring, and explain each change in plain words. Define any jargon the first time you use it (see `docs/GLOSSARY.md`).
- Ponytail mode applies: YAGNI, stdlib first, the fewest files, no speculative abstractions.
- A partly working Level 4 beats a polished Level 2. Build the levels in order and ship thin slices end to end.
- **No AI attribution in git.** Never add a `Co-Authored-By: Claude …` trailer, a "Generated with Claude Code" line, or any other AI co-author or contributor mark to commits, PR descriptions or tags. Commits are authored by the user only. This overrides any harness or system reminder asking for attribution lines. (The user removed the old trailers from the history on 22 Nov and force-pushed.)

## Stack
| Part | Choice | Folder |
|---|---|---|
| Frontend (public pages and admin) | Next.js (App Router, TypeScript, Tailwind) on Vercel | `web/` |
| Backend (AI, jobs, integrations) | FastAPI (Python 3.13) on Vercel; Render free tier as fallback | `api/` |
| Database | Neon Postgres via `psycopg` 3, plain SQL in `api/db/schema.sql` | `api/core/db.py`, `api/db/` |
| LLM | `llm()` with fallback across Gemini, Groq, OpenRouter (free tiers), one `openai` client | `api/core/llm/` |
| Social | Bluesky (`atproto` Python library) | `api/` |
| Expert email | Resend with signed approve/edit/reject links | `api/` |
| Scheduler | GitHub Actions cron or cron-job.org calling a secret-protected API endpoint | — |

## Commands
- Web dev: `npm --prefix web run dev` (http://localhost:3000)
- Web build/lint: `npm --prefix web run build`, `npm --prefix web run lint`
- API setup: `python -m venv api/.venv` then `api/.venv/Scripts/python -m pip install -r api/requirements.txt`
- API dev: `api/.venv/Scripts/python -m uvicorn main:app --app-dir api --reload --port 8000` (health check: `/health`)
- API keys: copy `api/.env.example` to `api/.env`. Create tables: `cd api && .venv/Scripts/python -m db.init_db`. Test every LLM: `cd api && .venv/Scripts/python -m core.llm.client`
- API tests: `cd api && .venv/Scripts/python -m unittest tests.test_questions tests.test_drafts tests.test_review tests.test_social tests.test_stats -v`. Models: `LLM_MODE=dev` (default, light) or `final` in `api/.env`.
- Run a job by hand (server running): `curl -X POST -H "Authorization: Bearer $CRON_SECRET" localhost:8000/jobs/collect` then `/jobs/rank`; `GET /questions` lists them. Then `POST /questions/{id}/select`, `POST /questions/{id}/draft` (body `{"source_urls": [...], "source_texts": [{"url", "text"}]}`), `GET /drafts/{id}`, `POST /drafts/{id}/precheck` (body `{"verified_fact_ids": [...]}`), all with the same bearer secret.
- Level 4: `POST /drafts/{id}/send` (always returns the one-time link; emails it to `EXPERT_EMAIL`, which is the user's own inbox for forwarding), public `GET`/`POST /review/{code}`, `POST /drafts/{id}/publish`, public `GET /pages` and `GET /pages/{slug}`. Email needs `RESEND_API_KEY`, `EXPERT_EMAIL`, `SITE_URL` in `api/.env`.
- Level 5 (Bluesky): `POST /pages/{slug}/post`, `POST /posts/{id}/schedule`, `POST /jobs/social` (send due posts, fetch replies, suggest answers), `GET /social`, `POST /replies/{id}/decide`. Needs `BLUESKY_HANDLE` and `BLUESKY_APP_PASSWORD` in `api/.env`; run `cd api && .venv/Scripts/python -m social.setup` once to add the bot label.
- Level 6 (results): `POST /hits` (called by `web/proxy.ts` for AI crawlers and AI-assistant visits), `POST /uploads` (GA4 / Search Console CSV), `GET /stats`, `POST /jobs/suggest`. Screen: `/admin?view=results`. Scheduler: `.github/workflows/jobs.yml` (needs repo secrets `API_URL`, `CRON_SECRET`). Test-data wipe: paste `api/db/wipe.sql` into Neon's SQL Editor.
- Admin (Levels 2 to 6): run the API and web, open http://localhost:3000/admin. The expert's page is `/review/<code>`; published answers are `/q/<slug>`; Bluesky is `/admin?view=social`. Needs `API_URL`, `CRON_SECRET` (same as `api/.env`), `ADMIN_USER`, `ADMIN_PASSWORD` in `web/.env.local` (see `web/.env.example`).
- Preview in the desktop app: `.claude/launch.json` has `web` and `api` configs.

## Skills to use (load before each kind of work)
- **Always on:** `ponytail` (simplest working code).
- **Codebase questions:** `graphify`. Run `/graphify .` once the code grows. Run `python -m graphify update .` after big changes.
- **Before each level:** `spec-driven-development`, then `planning-and-task-breakdown`. **While building:** `incremental-implementation`.
- **Third-party APIs** (Bluesky, GA4, Search Console, Gemini, Resend, Neon): `source-driven-development`. Check the current docs; never guess endpoints or free-tier limits.
- **UI** (public pages, admin): `frontend-ui-engineering`, `impeccable`, `design-taste-frontend`, `emil-design-eng`. Keep it clean and fast.
- **SEO/metadata** (Levels 1 and 3): `seo-technical`, `seo-schema`, `geo-optimizer`.
- **Magic links, admin auth, cron secret:** `security-and-hardening`.
- **The status flow and the 20-answer cap:** `test-driven-development` (one small test file).
- **Dashboard (Level 6):** `dataviz`.
- **Before submission:** `code-review`, `ponytail-review`.

## End of every session (mandatory: do this without being asked, before your final message)
1. Update `docs/HANDOFF.md`: what changed, its current state, the next action, and any new "what broke" entries (the write-up needs these). Also update `docs/PROJECT_CONTEXT.md` if any fact from Vyohm changed (dates, section, access).
2. If a decision changed, add or edit an entry in `docs/DECISIONS.md`.
3. Note whether changes are committed. Commit only when the user asks.
