# Decisions log

Short records of each choice and why we made it. Add new entries at the bottom. Status is **accepted**, **to verify** (depends on a fact we haven't checked yet), or **superseded**.

---

### D1: Next.js for the frontend, not a plain React app. *Accepted, 2026-11-20*
**Why:** a plain React single-page app sends empty HTML, and many AI crawlers don't run JavaScript. Our score includes Search Console impressions and AI traffic, so the public pages must be server-rendered. Next.js is still React.
**Alternative:** Vite React SPA (rejected for the reason above).

### D2: FastAPI (Python) for the backend. *Accepted, 2026-11-20*
**Why:** the user's preference. The LLM, Bluesky (`atproto`) and Google API libraries are all good in Python. Node is not used.

### D3: Host both on Vercel; Render free tier as the API fallback. *To verify*
**Why:** free, and the user chose it. **Risk:** serverless time limits on long LLM calls. **Check:** a Day-1 deploy test.

### D4: Neon Postgres. *Accepted, 2026-11-20 (added at Level 2, not before)*
**Why:** free serverless Postgres that works with serverless functions. **Alternative:** Supabase (built-in auth, but free projects pause when idle). Admin login is just an `ADMIN_PASSWORD` environment variable.

### D5: Gemini free tier (Flash-class) behind one `llm()` function. *To verify the limits*
**Why:** it has a genuine free tier. Grok's free API access is uncertain. A single wrapper makes swapping models a one-line change.

### D6: Bluesky only for social. *Accepted, 2026-11-20*
**Why:** the guide says one account is enough. Bluesky's API is free and simple. Mastodon, X and LinkedIn are optional, so we skip them.

### D7: Expert review by email (Resend) with signed one-time links. *Accepted, 2026-11-20*
**Why:** the guide allows email or the official WhatsApp Business Platform only. Email is far simpler. Links mean the expert needs no login.

### D8: Scheduler is an external cron calling secret-protected `/jobs/*` endpoints. *To verify*
**Why:** Bluesky has no scheduled posting. Vercel's free cron is believed to be limited (about once a day). We'll use GitHub Actions cron or cron-job.org every 5–15 minutes.

### D9: Log AI-crawler hits ourselves in Next.js middleware. *Accepted, 2026-11-20*
**Why:** Level 6 needs crawler hits "from server or CDN logs". Vercel's free log retention is short, so we write our own.

### D10: Source-grounded drafting with a fact table and a human pre-check. *Accepted, 2026-11-20*
**Why:** an unchecked provider claim disqualifies the entry. The LLM drafts only from sources we supply, and each fact keeps its URL, snippet and date. The user pre-checks before the expert sees the draft.

### D11: Scope cuts. *Accepted, 2026-11-20*
Skip Level 7. Exactly 2 question sources. 8–10 answers (the hard cap of 20 stays in code). No fancy UI. The demo goes on YouTube or X (HR waived the LinkedIn post on 19 Nov).
**Why:** the user's exams start 30 Nov, and a working system (35%) plus content (25%) matter more than extras.

### D12: Scaffold has no DB or extra libraries. *Accepted, 2026-11-20*
**Why:** YAGNI. Each level adds only what it needs.
