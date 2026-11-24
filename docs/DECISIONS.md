# Decisions log

Short records of each choice and why we made it. Add new entries at the bottom. Status is **accepted**, **to verify** (depends on a fact we haven't checked yet), or **superseded**.

---

### D1: Next.js for the frontend, not a plain React app. *Accepted, 2026-11-20*
**Why:** a plain React single-page app sends empty HTML, and many AI crawlers don't run JavaScript. Our score includes Search Console impressions and AI traffic, so the public pages must be server-rendered. Next.js is still React.
**Alternative:** Vite React SPA (rejected for the reason above).

### D2: FastAPI (Python) for the backend. *Accepted, 2026-11-20*
**Why:** the user's preference. The LLM, Bluesky (`atproto`) and Google API libraries are all good in Python. Node is not used.

### D3: Host both on Vercel; Render free tier as the API fallback. *Accepted, verified in the docs 2026-11-23*
**Why:** free, and the user chose it. **Risk:** serverless time limits on long LLM calls. **Checked 23 Nov (vercel.com/docs/functions/limitations):** Hobby functions run up to **300 s** (default and maximum), so a 20-30 s draft fits. Vercel finds a FastAPI `app` in `main.py` by itself (vercel.com/docs/frameworks/backend/fastapi), so `api/` needs no `vercel.json`. Python defaults to 3.12; `api/.python-version` pins 3.13. The API writes no files, so the read-only filesystem is fine. **Setup:** two Vercel projects from one repo: `web` (root `web/`, gets `gpu.aiatlasindia.com`) and `api` (root `api/`, stays on its `*.vercel.app` address; only the web server calls it, plus the expert's review page through the web app).

### D4: Neon Postgres. *Accepted, 2026-11-20 (added at Level 2, not before)*
**Why:** free serverless Postgres that works with serverless functions. **Alternative:** Supabase (built-in auth, but free projects pause when idle). Admin login is just an `ADMIN_PASSWORD` environment variable.

### D5: Gemini free tier (Flash-class) behind one `llm()` function. *Superseded by D13*
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

### D13: Three free LLM providers with fallback, through one `openai` client. *Accepted, 2026-11-20*
**Why:** the user wanted Gemini, Groq and OpenRouter. All three accept the OpenAI chat API, so one library (`openai`) talks to all of them; only the base URL and key change. `llm()` in `api/core/llm/client.py` tries the models in `FALLBACK` (`api/core/llm/models.py`) in order and moves on when one fails. A provider with no key is skipped.
**Order:** `gemini-3.8-flash` → Groq `openai/gpt-oss-120b` → Groq `openai/gpt-oss-20b` → `gemini-3.5-flash-lite`. OpenRouter is added once its key is in and a `:free` model is picked (free tier is 20 req/min and 50 req/day).
**To verify:** Gemini free-tier numbers (only visible in AI Studio when logged in) and whether Groq's published table is the free plan.

### D14: Database driver is `psycopg` 3 with plain SQL. *Accepted, 2026-11-20*
**Why:** no ORM to learn or explain. Tables live in `api/db/schema.sql`; `python -m db.init_db` creates them. Each level adds only its own tables.

### D15: Our pages copy the hub's design system (tokens and class names) instead of inventing a look. *Accepted, 2026-11-22*
**Why:** the user asked for design parity with gpu.aiatlasindia.com, and Vyohm will check the section against their "section kit". We read the live site's CSS and copied its tokens (ink navy `#0f1b2d`, signal yellow `#f4c430`, route red `#c9361a`, square corners, grid paper background) and class names (`atlas-header`, `atlas-footer`, `band--sea`, `btn`, `badge`, `entry-list`) into `web/app/globals.css`. Fonts are the kit's three: Bricolage Grotesque (headings), IBM Plex Sans (body), IBM Plex Mono (labels), loaded with `next/font`.
**Consequence:** when the official kit arrives, diff it against `globals.css` and swap values. Tailwind stays installed for the admin screens later; its reset removes list bullets and link underlines, so `globals.css` puts those back.
**Note:** the section name in the header chip is "GPU and cloud" (the hub's short name). The formal name "GPU cloud and AI infrastructure in India" is in the page title and the About page.

### D16: Footer shows the guide's exact ownership line **and** the hub's own sentence. *Accepted, 2026-11-22. Kit arrived 23 Nov: its footer uses the hub's sentence, word for word; the guide demands its own line. Keep both, the kit's sentence unchanged.*
**Why:** the guide requires one exact wording ("...which also sells AI products. We cover every provider, Vyohm included, by the same rules."). The hub's live footer says something different ("...owned and run by Vyohm AI Private Limited. Vyohm's own products (wotbot.ai, shotbot.ai) are judged by the same criteria..."). The PDF wins (PROJECT_CONTEXT intro), so the guide line is shown in full, with the hub's second sentence under it. Ask Vyohm which wording the kit will use.

### D17: How the section reaches the subdomain. *RESOLVED 2026-11-23: we host everything ourselves*
**Answer (Vyohm email, 23 Nov):** no shared repository and no pull request. We host both the public pages and the engine, add `gpu.aiatlasindia.com` as a custom domain on our host, and reply to Vyohm with the DNS record the host shows (type, name, value). They add it within 12 hours. The kit page's "Going live" steps are the old route: ignore them.

_Original note, kept for the record:_
**Conflict:** the setup email says "build your section in its own folder and open a pull request... we'll put it live on your subdomain", which sounds like their repo hosts it (the hub looks like an Astro site: `/_astro/` asset paths, inferred). Our engine needs a Python backend, a database, an admin screen and cron jobs, which a static hub cannot host. The earlier plan (PROJECT_CONTEXT §3 and the guide) was that we host anywhere and they point the subdomain at us.
**Plan until answered:** keep building `web/` and `api/` here. Ask Vyohm whether the subdomain can point at our Vercel deployment, and what the pull request should contain (for example, a folder with a link and the code). Do not restructure anything before they reply.

### D18: Question sources are one file each, behind a registry. Stack Exchange and Hacker News for now. *Accepted, 2026-11-22*
**Why:** Level 2 needs two official sources. Both work with no key. Each lives in `api/questions/sources/<name>.py` with a `fetch()`; `sources/__init__.py` lists them in `SOURCES`, and `collect.py` loops over that list. Adding Search Console, YouTube comments or Bluesky later is one new file plus one line.
**Facts checked on 2026-11-22 (they differ from what the docs imply):**
- Stack Exchange without an app key allows about **300 requests a day** (`quota_remaining` was 299), not the 10,000 the throttle page gives to registered apps. One collect run costs 12 (4 sites x 3 queries). Long query phrases returned nothing, so `queries.py` keeps them short.
- Hacker News: the docs page is built with JavaScript, so the endpoint `hn.algolia.com/api/v1/search` and the `ask_hn` tag were confirmed by calling them. Plain "story" results are mostly "Show HN" launches, so we use `ask_hn`.
**Known weakness:** both sources are global and technical, not India-specific. The ranking step scores buying relevance to compensate. Better sources are listed in HANDOFF.

### D19: Light models while building, strong models at the end, switched by `LLM_MODE`. *Accepted, 2026-11-22*
**Why:** the user wants fast, cheap tests now and the best models only for the real run. `core/llm/models.py` holds `FALLBACK_DEV` (default: Gemini 3.1 Flash-Lite, Groq gpt-oss-20b, OpenRouter Gemma 4 26B free, Groq Qwen3.8 27B) and `FALLBACK_FINAL`. Set `LLM_MODE=final` in `api/.env` to switch; `python -m core.llm.client` tests both lists. Model names come from each provider's own `/models` list.
**Before submitting:** retest the final list. On 2026-11-22 `gemini-3.8-flash` timed out after 60 s, and OpenRouter free models often return 429 (rate limited). The fallback chain covers both, but check the order.

### D20: Standard library for HTTP and tests; one bearer secret for every `/jobs/*` route. *Accepted, 2026-11-22*
**Why:** `httpx` and `pytest` are not installed, and a 20-line `urllib` helper (`core/http.py`) does the job, including unzipping Stack Exchange's guaranteed gzip. Tests use `unittest` (`python -m unittest tests.test_questions -v`). Routes under `questions/router.py` need `Authorization: Bearer <CRON_SECRET>`; an empty secret rejects everyone, and the comparison is constant-time (`core/auth.py`).
**LLM output is untrusted:** (see also D21 for drafts) the ranking prompt marks the question list as data, and `parse_ranking` only accepts known ids, clamps scores to 0-10, and drops duplicate loops, so a bad or manipulated reply cannot corrupt the table.

### D21: Drafts come only from pages you supply, and code checks every quote. *Accepted, 2026-11-22*
**Why:** an unchecked provider claim disqualifies the entry (D10). You give 1 to 4 https addresses per draft (`source_urls`), or paste the text of a page we can't download (`source_texts`, for pages drawn by JavaScript, PDFs or blocked pages). The LLM may use only that text and must list each fact with a quote. `parse_draft()` rejects the draft if a quote is not word for word in its source (spacing and capitals ignored), a `[n]` marker has no fact, a fact cites an address that is not a source, or one fact is cited more than 3 times. One automatic retry sends the reason back to the LLM. The model never searches the web: search results would be unsourced.
**Known limit:** code cannot tell whether a quote supports the sentence citing it. The human pre-check and the expert cover that, so the admin screen (Level 4) must show claim, quote and source side by side.
**Also:** pages are cut at 10,000 characters each (free-tier models have small limits). Only https addresses are fetched. The slow part runs without a database connection held open.

### D22: JSON-LD is built by code; selecting and pre-checking are API calls until Level 4. *Accepted, 2026-11-22*
**Why:** structured data written by an LLM can be invalid or claim things the page doesn't. `build_json_ld()` makes a schema.org `Article` from the checked title, description and source list, so it is always valid. Level 4 adds the page address, publish date and expert reviewer. The user chose to defer the admin panel: select, draft and pre-check are `curl` calls with the bearer secret. All status changes go through `core/status.py` (`check_move`), which refuses, for example, drafting a question nobody selected.
**Plain code, not LangGraph:** the order of steps is fixed and the slow steps are humans, so the `status` column in Postgres is the workflow state and each step is one endpoint. Sources are modules our code calls, not tools the LLM chooses.

### D23: The admin is Next.js Server Components + Server Actions behind a Basic Auth proxy; three designs until the user picks one. *Accepted, 2026-11-22*
**Why:** the user wanted a working front end for Levels 2 and 3 instead of Swagger. The browser never talks to FastAPI: server code in `web/app/admin/_lib/` calls it with `CRON_SECRET`, which has no `NEXT_PUBLIC_` prefix and so never reaches the browser. Each button is a Server Action (`useActionState` gives the pending state and message; `refresh()` re-renders with fresh data). Live data sits inside `<Suspense>` because `cacheComponents` is on.
**Login:** replaced by a sign-in page on 24 Nov (D27). Level 4's expert links are separate (one-time random codes, no login).
**Provider pages:** a short tick-box list in `_lib/sources.ts` of pages checked to download as text, plus a box for other addresses and a pasted-text option. No drop-down of every provider: we only list pages we have verified.
**Three designs, then one (S8):** Atlas, Ledger and Board were built on the same components; the user kept **Atlas** and asked for Ledger's two columns once a question is open. Now one page, `/admin`, with three views picked by the address (`?q=` question, `?draft=` draft with a facts side panel). Rules: yellow (the hub's signal colour) marks only the next step, one per screen; every action's result is a toast from `sonner` (one `<Toaster />` in the layout, `toast()` in `ActionForm`; chosen over a hand-made toast because it already handles stacking, timers and screen readers). Error toasts stay until closed.
**Route group:** public pages moved to `app/(site)/` so the admin has no public header, footer or analytics. URLs are unchanged.

### D24: The expert check uses one-time random links, not signed links; publishing is a separate admin click. *Accepted, 2026-11-22*
**Link:** `POST /drafts/{id}/send` makes a random code (`secrets.token_urlsafe(32)`) and stores only its sha256 hash with a 14-day expiry, so a database leak gives no working links. The code is the expert's only permission: it opens one draft and works once (the save runs `UPDATE ... WHERE decision IS NULL`, so two clicks can't both count). Sending again expires the old unanswered link. Only the newest version of a draft can be sent. Chosen over signed (HMAC) links because a stored row can be made one-time and expired, which a signature alone can't.
**Email:** Resend's REST API with stdlib `urllib`. With no `RESEND_API_KEY`/`EXPERT_EMAIL` (or if Resend fails) the API returns the link and the admin desk shows it to copy, so Level 4 works before email is set up. Resend's test sender (`onboarding@resend.dev`) only delivers to the Resend account's own address.
**Changed S11 (23 Nov), user's choice:** `EXPERT_EMAIL` is the user's own inbox (the Resend account address), and the user forwards the email to the expert. This needs no verified domain (we don't control aiatlasindia.com's DNS). The API now returns the link on every send, emailed or not, so the desk always shows it to copy. The link is still never stored (only its hash), so it is shown once, at send time; sending again makes a fresh one.
**Expert page:** `web/app/review/[token]`, outside `/admin` (no password) and outside `(site)` so Google Analytics never sees the secret address; `noindex`, `no-referrer`, and the code's shape is checked before it reaches the API. Approve, edit (their text is saved as the AFTER version; the AI draft stays as BEFORE) or reject (a reason is required). Optional 2-3 lines of advice. "Edit" with no change is refused.
**Publish:** a separate yellow button in the admin after approval, so the owner sees the expert's version first. `POST /drafts/{id}/publish` locks the `pages` table, refuses the 21st page (`MAX_PAGES = 20`) and a second page for the same question, and makes the address from the title. `GET /pages/{slug}` only returns drafts joined to an approved or edited review, so an unapproved draft can't be served even by mistake. The public page `/q/[slug]` says it was drafted with AI, lists each source with its date, and names the expert only if `EXPERT_NAME` is set (after written consent).
**Expert email content (S10):** subject "Please review: <title>"; body has the title, the one-time link, a line on approve/edit/reject and the advice box, and the expert questions. The answer itself is NOT in the email: the expert reads and decides on the page, so the decision is recorded in one place and the link can expire. The address comes only from `EXPERT_EMAIL` on the server; the admin can't type a recipient.
**Forms keep their input after an error:** `ActionForm` submits through `onSubmit` + `startTransition` instead of `<form action>`, because React 19 empties a form after a form action, which wiped the expert's edit when a save failed. Cost: forms need JavaScript (only the desk and the expert page have forms).

### D25: Bluesky through its plain HTTP API; the AI drafts, a person schedules every post and sends every reply. *Accepted, 2026-11-23*
**Why stdlib, not the `atproto` SDK:** five calls (log in, create a record, read notifications, read and write the profile) are a few lines of `urllib` each, the same pattern as Resend and Stack Exchange (D20), and every line is explainable. Checked against Bluesky's docs source (github.com/bluesky-social/bsky-docs) and lexicons (github.com/bluesky-social/atproto, `packages/api/lexicons`), because docs.bsky.app is JavaScript-rendered and unreadable to our tools.
**Flow:** for each published answer the AI writes a post (`social/prompts/post.txt`, only from the page's title, summary and advice); you edit it and pick a time (`/admin?view=social`); `POST /jobs/social` sends posts whose time has passed, with a link card to the answer, then saves new notifications whose reason is `reply` or `mention` and lets the AI suggest an answer (`social/prompts/reply.txt`, the commenter's text marked as data, not instructions). Nothing is sent until you press "Send this reply"; the decision is stored as approved (sent as suggested), edited, or rejected, with the suggestion kept beside what was sent.
**Rules in code:** `bluesky.py` has no follow, like, repost or DM function, and a test fails if those record types ever appear in `social/`; we answer only rows that came from replies or mentions, never our own posts; one post per answer (`posts.page_id` UNIQUE); row locks stop a post or reply going out twice; Bluesky allows 300 logins a day, so each run logs in once.
**Commenter data:** only their post's address and text (no names or handles). Delete it after the results with `DELETE FROM replies;`.
**Bot label:** Bluesky's docs ask bots to add the self-label `bot` to their profile; `python -m social.setup` does it once.
**Scheduler:** "Check Bluesky now" in the admin runs the job by hand until the API is online; then GitHub Actions cron or cron-job.org calls it every 15-30 minutes with the bearer secret.


### D26: Level 6 counts AI traffic in our own proxy, takes GA4 and Search Console as uploaded CSVs, and the AI only suggests. *Accepted, 2026-11-24*
**AI traffic from our own logs:** `web/proxy.ts` now runs on every request (not only `/admin`). `web/lib/aiTraffic.ts` matches the User-Agent against known AI crawlers (GPTBot, ClaudeBot, PerplexityBot and 9 others) and the Referer or `utm_source` against AI assistants (ChatGPT, Perplexity, Gemini, Copilot, Claude). A match is sent to `POST /hits` in the background (`event.waitUntil`, so the page isn't slowed; a failed report is dropped). The `hits` table keeps only a count per kind, name, page and day: no IP address, no user agent.
**GA4 and Search Console:** Vyohm gave Viewer access to the user's Google account only, no service account, and the Generative AI report has no API at all, so the dashboard takes CSV exports uploaded by hand (`POST /uploads`). `stats/stats.py` skips GA4's `#` comment lines, keeps the biggest table, drops "Total" rows and adds up only count columns (clicks, impressions, users, sessions, views, events), never averages like CTR or position. The same file name again replaces the old copy.
**Post performance:** each `/jobs/social` run copies like, repost, reply and quote counts from Bluesky (`app.bsky.feed.getPosts`, up to 25 posts) into `posts`. The post's link card now carries `?utm_source=bluesky&utm_medium=social` so GA4 can tell those visits apart; the page's canonical link stays the plain address.
**What to answer next:** `POST /jobs/suggest` gives the AI the published titles, post counts, AI traffic, the top rows of each export and the 15 best-ranked open questions (`stats/prompts/suggest.txt`, all marked as data). It returns what the audience responds to and up to 3 picks with reasons; code accepts only ids it offered. A person picks with the normal Select button, which feeds Level 3. With no data yet the AI says so honestly (seen in the first run).
**Timeline (added later 24 Nov):** every step's time already lived in its own table except two, so `questions.selected_at` and `drafts.prechecked_at` were added and `drafts/timeline.py` lines them all up with one query for the draft screen. No separate event-log table: it would copy data we already store.
**No charts:** a handful of numbers reads better as stat tiles and tables (dataviz skill: sometimes the answer is not a chart).
**Scheduler:** `.github/workflows/jobs.yml` calls `/jobs/social` every 30 minutes and `/jobs/collect` + `/jobs/rank` daily at 06:00 IST, using the repository secrets `API_URL` and `CRON_SECRET`; it skips every step until `API_URL` is set.

### D27: The admin signs in on a page and keeps a signed cookie, instead of the browser's login box. *Accepted, 2026-11-24 (replaces the login part of D23)*
**Why:** the grey Basic Auth box had no design, no sign out and no link to it. The user asked for a sign-in page.
**How:** `web/app/login/` has the form and the Server Actions `login` and `logout`. A correct username and password set the cookie `atlas_admin`, whose value is `<expiry>.<signature>`: an HMAC-SHA256 of the expiry, keyed by `ADMIN_USER:ADMIN_PASSWORD` (`web/lib/session.ts`, Web Crypto only because `proxy.ts` and the actions both use it). `proxy.ts` accepts only a cookie we signed that hasn't expired; anything else is sent to `/login`. Changing the password signs everyone out. The cookie is `httpOnly`, `sameSite=lax`, `secure` in production, 7 days. After login it always goes to `/admin`, never to an address taken from the URL (no open redirect). Passwords are compared in constant time. No password set still means `/admin` is closed.
**Limits (ponytail):** no real rate limit (serverless keeps no memory between requests), only a one-second wait after a wrong password; "Sign out" removes this browser's cookie but a copied cookie stays valid until it expires or the password changes. Fine for one owner on a short-lived site; the upgrade is Upstash rate limiting and a server-side session list.
**No footer link:** the kit says to use its footer unchanged, so the way in is a bookmark on `/login`.

### D28: The expert sees everything that will be published and can edit all of it; one database view gives every page the final version. *Accepted, 2026-11-24*
**Why:** the expert page showed the answer and facts but not the title's search text (meta description) or the image alt text, so they approved metadata they never saw, and "edit" covered only the answer. The guide scores "metadata checked", and the user asked that the expert has everything on one page.
**What the expert sees:** page title, search-result text, image description, the answer, each fact beside its quote and source, and the structured data (read-only, built by code from the title and text). Choosing "Approve with my edits" opens editable boxes for title (120 characters), search text (300), image text (300) and answer; anything they leave as it was is not recorded as an edit, and an edit with no change is refused. Nothing is forced: they can approve as written.
**How it is stored:** `reviews.edited_title`, `edited_meta_description`, `edited_alt_text` (plus the existing `edited_body`), NULL = unchanged. The AI's draft is never overwritten, so BEFORE and AFTER both stay; the desk shows both.
**One view, not eight edits:** `final_drafts` (schema.sql) returns each approved or edited draft with the expert's value where there is one. Published pages, `/pages`, the sitemap, the slug at publish time, Bluesky posts and link cards, the suggestions prompt and the dashboard read it instead of `drafts`, so an edited title can't show in one place and the AI's in another. The JSON-LD headline and description are set from the final title and text when a page is read, so structured data always matches the page.
**Image:** the AI still writes alt text for a "lead illustration", but no image is published yet; the expert page says so. Making a share image per answer is an open option.

### D29: Drafts and ranking use a separate list of stronger, slower models, read whole pages, and ask for JSON mode. *Accepted, 2026-11-24 (extends D13)*
**Why:** the user saw ranking and drafting fail with "no JSON" errors and asked for top quality at any speed. The errors came from the reply limit (thinking models used it up) and from Gemini Flash being overloaded, not from the prompts.
**What:** `llm()` sets a 32,000-token reply limit, treats an empty or cut-off reply as a failure (next model), can ask for JSON mode, and stops trying at 270 s (Vercel ends a request at 300 s; `/admin` declares `maxDuration = 300`). `FALLBACK_BEST`, used for drafts and ranking in every mode: Nemotron 3 Ultra 550B (free, OpenRouter), Gemini 3.8 Flash, Nemotron 3.5 Super, Gemini 3.5 Flash, Groq gpt-oss-120b. Picked by running the real draft prompt with two full provider pages (74,000 characters) through each candidate: both Nemotrons and gpt-oss (on short pages) passed every check; Gemini Pro has no free quota (429); Gemini Flash was 503 all day. Pages now go in whole (60,000 characters each, 120,000 total), so a price far down a pricing page is no longer cut off. Social posts, replies and suggestions keep the fast lists.
**Cost:** a draft takes 1-4 minutes and ranking 20 questions about 1-2. Groq, last in the list, refuses prompts over about 8,000 tokens, so it only rescues drafts with short pages. If Gemini billing is ever turned on, put a Pro model first.
**Also:** a collect run saves at most 20 new questions (the guide sets no number; we publish 8-10), and fact links highlight their quote on the source page.

### D30: A review link opens only with the personal code of the expert it was sent to. *Accepted, 2026-11-24 (extends D24)*
**Why:** with two experts, the one-time link alone couldn't show who reviewed an answer, and the same link sent to both could be used by either. The user asked for a code per expert, checked on the server, asked once and then remembered by the browser.
**How:** `EXPERT_CODES` (env, never the repo) holds an 8-character code per expert (no look-alike characters, about 850 billion possibilities). Sending a draft names the expert (`reviews.expert`). The page asks for the code once and keeps it in an httpOnly cookie on `/review` for 30 days; a cookie, not a bearer token, because a browser sends cookies by itself on every click from an email, while a bearer token needs page JavaScript. The page only forwards it; the API checks the link and the code on every read and decision (401 wrong code after a 1 s wait, 403 the other expert's). Codes are compared in constant time. Each answer page names the expert who approved it.
**Limits:** an expert who shares their code shares their access, but every decision is recorded under their name. The 1 s wait is per request, not a real rate limit; enough for these codes. Sending again (to either expert) cancels the old link.
**Rejected:** a second Gemini key from another Google account for extra free quota. Google's API terms forbid getting around usage limits, and today's failures were "overloaded" (503) and "no free quota for Pro" (429), which a second free key would not fix. Turning on billing for the existing key is the allowed route if more is needed.
