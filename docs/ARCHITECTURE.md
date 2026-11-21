# Architecture

Status: **mostly planned**. Built so far: a Next.js placeholder; a FastAPI `/health` endpoint that also checks the database; `api/core/` (settings, DB connection, `llm()` with fallback across Gemini, Groq and OpenRouter); and `api/db/schema.sql` (the `questions` table). Update this file as pieces become real, and mark each one **built** or **planned**.

## Backend folders (built)
| Folder | Holds |
|---|---|
| `api/core/` | Shared plumbing: `config.py` (env vars), `db.py` (`get_conn()`), `llm/models.py` (providers and fallback order), `llm/client.py` (`llm()`) |
| `api/db/` | `schema.sql` (tables) and `init_db.py` (creates them) |
| `api/<feature>/` | Planned: one folder per feature (`questions/`, `drafts/`, …), each with its own `prompts/` folder |

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
 Expert ◄── email with approve / edit / reject links ──► api /review/{token}
```

## The one flow that matters (the demo shows exactly this)
1. **Collect.** A cron job pulls questions from 2 official sources and stores them with where they came from.
2. **Rank and merge.** The LLM groups near-duplicates and scores each question. The reason is stored.
3. **Draft.** For a chosen question, we supply source URLs. The API fetches the page text, and the LLM drafts the answer, title, meta description, alt text and JSON-LD **only from those sources**. Each fact is stored with its URL, snippet and checked date.
4. **Pre-check.** The admin fact-check screen shows each fact next to its source. The user ticks them.
5. **Expert review.** Resend emails the expert a draft with signed one-time links (approve / edit / reject), plus 2–3 questions asking for first-hand advice. Every version is kept.
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

## Planned data (Neon Postgres, added at Level 2, kept minimal)
| Table | Holds |
|---|---|
| `questions` | text, source, source_url, score, rank_reason, merged_into, status |
| `drafts` | question_id, version, body, title, meta_description, alt_text, json_ld, status |
| `facts` | draft_id, claim, source_url, snippet, checked_on, verified |
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
