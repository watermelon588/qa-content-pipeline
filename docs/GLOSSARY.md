# Glossary: jargon in plain words

This file is for the user, not the agent. **Group A**: understand before building (about 2–3 hours). **Group B**: learn when we reach that level.

## Group A: before building
| Term | Plain meaning | Where it shows up |
|---|---|---|
| **GA4 (Google Analytics 4)** | Google's free visitor counter. You paste a small tag (the "measurement ID", like `G-XXXX`) into the site, and it records visits. | Level 1 (install the tag), Level 6 (read the numbers) |
| GA4 *property* | One site's analytics account. Vyohm creates ours. | Level 1 |
| *Sessions / users* | Visits / unique visitors. | Level 6 |
| *Traffic source / medium* | Where a visitor came from, e.g. `chatgpt.com / referral`. This is how we spot AI referrals. | Level 6 |
| **Search Console (GSC)** | Google's tool showing which searches show our pages, and whether pages are indexed. | Levels 1, 2, 6 |
| *Impressions / clicks* | Times our page was shown in Google / times someone clicked it. | Level 6 |
| *Queries* | The search words people used. These are also a source of new questions. | Level 2 |
| *Indexing / URL Inspection* | Whether Google has stored a page / the tool to check one page. | Level 1 |
| *Generative AI report* | Impressions in Google's AI features. It has **no API**, so we export a CSV by hand. | Level 6 |
| **Sitemap** (`sitemap.xml`) | A list of all our pages for Google. | Level 1 |
| **robots.txt** | A file telling bots what they may crawl. | Level 1 |
| **Server-rendered (SSR) vs SPA** | Whether the server sends finished HTML (bots can read it) or empty HTML that JavaScript fills in (many bots can't read it). This is why we use Next.js. | Everywhere |
| **Bluesky** | A free social network like X, with a free official API. | Levels 1, 5 |
| *App password* | A separate password just for our code, so the real password never goes in the code. | Level 1 |
| *Bot self-label* | A setting that marks the account as automated. Required. | Level 1 |
| **Status flow** | A draft moves `draft → in_review → approved/edited/rejected → published`. Only approved drafts publish. | Levels 3–4 |
| **Ground rules** | The 8 rules that disqualify the entry if broken (PROJECT_CONTEXT §5). | Always |

## Group B: learn as we build
**Question sources (Level 2)**
- **Stack Exchange API**: free Q&A data from sites like Server Fault, using a free key with rate limits.
- **Hacker News API**: free, no key. Search works through Algolia's HN Search API.
- **YouTube Data API**: free key with a daily quota. Used to read comments on relevant videos.
- **Google Trends**: shows what's rising in searches. There is no official API, so use the manual CSV export.

**Bluesky (Level 5)**
- **AT Protocol**: the technical rules Bluesky runs on. We just use the `atproto` Python library.
- **Handle**: the account name, e.g. `gpu-atlas.bsky.social`.
- **Notifications API**: how we fetch replies and mentions.
- **Rate limits**: the maximum number of requests per time window.

**Page metadata (Level 3)**
- **Meta description**: the snippet under the title in Google results.
- **Alt text**: an image description for screen readers and search engines.
- **Canonical URL**: tells Google which URL is the "real" one for a page.
- **JSON-LD / structured data**: hidden machine-readable data about the page, such as the article, author and reviewer.
- **E-E-A-T**: Google's idea of Experience, Expertise, Authoritativeness and Trust. It's why the expert is named.

**AI traffic (Level 6)**
- **User-agent**: the name tag a browser or bot sends with every request.
- **GPTBot, ClaudeBot, PerplexityBot**: AI companies' crawlers. We count their visits.
- **Referrer**: the site a visitor clicked from.

**LLM work (Level 3)**
- **Prompt / system prompt**: the instructions our code sends to the AI model. The write-up must list these.
- **Structured output**: making the model return JSON we can store.
- **Grounding**: forcing the model to use only the sources we give it.
- **Hallucination**: the model confidently making something up, which is why we fact-check.
- **Quota / rate limit**: the free-tier caps on requests.

**Backend and infrastructure**
- **FastAPI / Pydantic**: the Python web framework / its data validation.
- **CORS**: browser rules about which sites may call our API.
- **Environment variables (`.env`)**: where secrets live. Never commit them.
- **Cron**: a job that runs on a timer, e.g. "every 10 minutes, send due posts".
- **Magic link**: a signed one-time link in the expert's email, so they can approve without logging in.
- **Resend**: a service for sending email from code (free tier).
- **Service account**: a robot Google account our backend uses to read GA4 and Search Console.
- **Neon**: a hosted Postgres database (free tier).
- **Serverless function**: code that runs per request on Vercel. It has time limits.
- **DNS / CNAME**: how the subdomain gets pointed at Vercel. Vyohm does this; we give them the target.
