# Architecture

Status: **Levels 1 to 5 built** (see the tables below); metrics and the dashboard (Level 6) are planned. Built so far: the Level 1 public pages in `web/` (`app/` pages, `components/Header.tsx` and `Footer.tsx`, `lib/site.ts` for shared facts, hub-style `globals.css`, `sitemap.ts`, `robots.ts`); a FastAPI `/health` endpoint that also checks the database; `api/core/` (settings, DB connection, `llm()` with fallback across Gemini, Groq and OpenRouter); and `api/db/schema.sql` (the `questions` table). Update this file as pieces become real, and mark each one **built** or **planned**.

## Frontend folders (built)
| Folder | Holds |
|---|---|
| `web/app/(site)/` | Public pages with the hub header and footer: home (lists published answers), about, and `q/[slug]/` (**Level 4, built:** one published answer with the AI disclosure, sources and dates, expert advice, JSON-LD). The brackets keep "(site)" out of the URL |
| `web/app/admin/` | **Admin for Levels 2 to 4, built.** `_lib/api.ts` (types, loaders, `nextStep()`), `_lib/actions.ts` (Server Actions for every button, including send to expert and publish), `_lib/sources.ts` (known provider pages), `_components/` (DraftForm, DraftView with the side panel for facts and next step plus the before/after view, QuestionPanel, SocialView, Problem). One page, `page.tsx`: `/admin` overview, `/admin?q=ID` question, `/admin?draft=ID` draft, `/admin?view=social` Bluesky. Styles in `admin.css` |
| `web/app/review/` | **Level 4, built.** The expert's page `[token]/page.tsx` (approve / edit / reject), its Server Action `actions.ts`, and `code.ts` (checks the code's shape). No password, no analytics, `noindex`, `no-referrer` |
| `web/lib/`, `web/components/` | Shared: `lib/api.ts` (the server-side API caller and shared types), `lib/site.ts` (site facts), `components/` (Header, Footer, ActionForm with toasts, Markdown) |
| `web/proxy.ts` | Signed login cookie for every `/admin` URL (no cookie: sent to `/login`); also counts AI crawler and AI-assistant visits |

## Backend folders (built)
| Folder | Holds |
|---|---|
| `api/core/` | Shared plumbing: `config.py` (env vars), `db.py` (`get_conn()`), `http.py` (`get_json()`), `auth.py` (`require_secret`, the bearer check for `/jobs/*`), `llm/models.py` (providers; dev, final and best model lists), `llm/client.py` (`llm()`, with JSON mode and a 270 s limit) |
| `api/db/` | `schema.sql` (tables) and `init_db.py` (creates them) |
| `api/questions/` | **Level 2, built.** `queries.py` (search phrases), `sources/` (one file per source: `stackexchange.py`, `hackernews.py`; `__init__.py` is the registry), `collect.py` (run sources, save new questions), `rank.py` (LLM scores and merges), `prompts/rank.txt` (the exact prompt), `router.py` (`POST /jobs/collect`, `POST /jobs/rank`, `GET /questions`) |
| `api/drafts/` | **Level 3, built.** `sources.py` (download a page and strip it to text, or accept pasted text), `draft.py` (build the prompt, `parse_draft()` check, one retry, code-built JSON-LD, save), `prompts/draft.txt` (the exact prompt), `router.py` (`POST /questions/{id}/draft`, `GET /drafts`, `GET /drafts/{id}`, `POST /drafts/{id}/precheck`) |
| `api/review/` | **Level 4, built.** `review.py` (one-time codes stored as sha256 hashes, `check_decision()`, the email text, Resend call), `router.py` (`POST /drafts/{id}/send`, public `GET`/`POST /review/{code}`) |
| `api/pages/` | **Level 4, built.** `pages.py` (`MAX_PAGES = 20`, `check_cap()`, `slugify()`), `router.py` (`POST /drafts/{id}/publish`, public `GET /pages`, `GET /pages/{slug}`) |
| `api/core/status.py` | The one table of allowed status changes (`check_move`). A question can't be drafted until selected; a draft can't go to the expert until pre-checked, or be published until approved |
| `api/tests/` | `test_questions.py` (ranking parser, secret check, source mapping), `test_drafts.py` (draft validator, page fetcher, status guard, JSON-LD) and `test_review.py` (status flow, 20-page cap, slugs, codes, the expert's decision, email) and `test_social.py` (text limit, link bytes, who we answer, threads, no follow/like/repost/DM in the code). No network, no database, no LLM |
| `api/social/` | **Level 5, built.** `bluesky.py` (the only Bluesky code: log in, post, notifications, bot label; no follow/like/repost/DM), `social.py` (rules with no network: 300-character check, link positions in bytes, which notifications we may answer, thread references), `write.py` + `prompts/post.txt`, `prompts/reply.txt` (the LLM's two jobs), `jobs.py` (send due posts, fetch replies, suggest answers), `router.py` (endpoints), `setup.py` (run once: bot label) |
| `api/<feature>/` | Planned: `metrics/` (Level 6) |

## Overview
```
                 ┌────────────────────────── web/ (Next.js on Vercel) ──────────────────────────┐
 Readers ──────► │ Public pages (server-rendered): / , /q/[slug] , /about , sitemap.xml, robots │
 AI crawlers ──► │ middleware: logs bot user-agents (GPTBot, ClaudeBot, PerplexityBot) → api      │
                 │ Admin (password): questions, drafts, fact check, review status, social, dash │
                 └───────────────────────────────┬──────────────────────────────────────────────┘
                                                 │ HTTPS (JSON)
                 ┌───────────────────────────────▼──── api/ (FastAPI on Vercel) ─────────────────┐
 Cron (GitHub ─► │ /jobs/* (secret-protected): collect questions, send due posts, fetch replies │
 Actions or      │ questions · drafts (LLM) · review (email + magic links) · publish · social   │
 cron-job.org)   │ metrics (GA4 API, Search Console API, bot hits, CSV upload) · insights (LLM) │
                 └──────┬──────────────┬─────────────┬──────────────┬───────────────┬───────────┘
                        │              │             │              │               │
                   Neon Postgres   Gemini API     Resend        Bluesky API    GA4 / GSC APIs
                                   (drafts)   (expert email)  (post, replies)  (read-only)
 Expert ◄── email with a one-time link ──► web /review/{code} ──► api /review/{code}
```

## The one flow that matters (the demo shows exactly this)
1. **Collect.** A cron job pulls questions from 2 official sources and stores them with where they came from.
2. **Rank and merge.** The LLM groups near-duplicates and scores each question. The reason is stored.
3. **Draft.** For a chosen question, we supply source URLs. The API fetches the page text, and the LLM drafts the answer, title, meta description, alt text and JSON-LD **only from those sources**. Each fact is stored with its URL, snippet and checked date.
4. **Pre-check.** The admin fact-check screen shows each fact next to its source. The user ticks them.
5. **Expert review.** Resend emails the expert a one-time link (a random code; only its hash is stored, D24) to a page where they approve, edit or reject, plus 2–3 questions asking for first-hand advice. Every version is kept.
6. **Publish.** Only approved drafts become pages. The 20-page cap is enforced. The page credits the expert and discloses that AI drafted it.
7. **Social.** The LLM writes a post. It is scheduled, and the cron job sends it when due. Replies and mentions are fetched, the LLM drafts responses, and a human approves each one before it is sent.
8. **Measure.** The dashboard reads GA4 (human visitors, AI referrers), our bot-hit logs, Search Console (API plus a manual CSV upload of the Generative AI report), and post stats. The LLM suggests what to post next, and the user picks.

## Status flow (enforce it in one place and test it)
```
question: new → selected → drafted
draft:    draft → prechecked → in_review → approved | edited | rejected
                                            approved/edited → published (max 20)
reply:    fetched → drafted → approved → sent   (or → discarded)
post:     drafted → scheduled → sent | failed
```

## Data (Neon Postgres, kept minimal). `questions`, `drafts` and `facts` are built; the rest are planned
| Table | Holds |
|---|---|
| `questions` | text, source, source_url, score, rank_reason, merged_into, status (built, Level 2) |
| `drafts` | question_id, version, body, title, meta_description, alt_text, json_ld, expert_questions, status (built, Level 3) |
| `facts` | draft_id, n, claim, source_url, snippet, checked_on, verified (built, Level 3) |
| `reviews` | draft_id, decision, expert_edit, expert_advice, token_hash, decided_at |
| `pages` | draft_id, slug, published_at |
| `posts` | page_id, text, scheduled_for, sent_at, uri, stats |
| `replies` | post_uri, author_handle, text, draft_reply, status. **Deleted after the assignment.** |
| `bot_hits` | user_agent, path, at |

## Secrets (environment variables, never committed)
`DATABASE_URL`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `RESEND_API_KEY`, `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD`, `ADMIN_PASSWORD`, `CRON_SECRET`, `REVIEW_LINK_SECRET`, `GOOGLE_SERVICE_ACCOUNT_JSON`, `GA4_PROPERTY_ID`, `NEXT_PUBLIC_GA_ID`, `API_URL`.

## Hosting
- Two Vercel projects from this one repo: `web/` (the subdomain points here) and `api/`.
- The public pages must be **server-rendered** so search engines and AI crawlers see real text.
- Day-1 test: deploy the `/health` endpoint plus one DB call and one Gemini call to Vercel. If the function time limits bite, move `api/` to Render's free tier.
