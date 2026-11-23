# Project Context: everything we know and decided

This is the single source of truth for the assignment, the rules, and what was discussed with the user. The source is `Vyohm_AI_Content_Engine_Candidate_Guide.pdf` (issued 16 Nov 2026) plus the email thread with Vyohm. If this file and the PDF disagree, **the PDF wins**: fix this file.

> This repo is shared with the Vyohm GitHub org. Keep personal contact details (phone numbers, emails, the expert's contact info) **out** of it.

---

## 1. What we are building (plain words)
This is **not a chatbot**. It is a pipeline with human checkpoints, like a small automated newsroom:

```
FIND questions → AI DRAFTS answer (with sources) → you PRE-CHECK facts
→ EXPERT approves / edits / rejects (by email) → PUBLISH approved page
→ AI writes SOCIAL post, auto-posted at a set time → fetch replies → AI drafts reply → YOU approve → sent
→ DASHBOARD measures everything → AI suggests what to post next → you pick
```

The rule that holds it together: **AI drafts, people decide what goes public.** The guide says this is the point of the assignment and what Google expects from sites that use AI.

The output is a section of **aiatlasindia.com** (Vyohm's guide to AI providers in India). Each page answers one real buying question an Indian business owner asks, covering cost, compatibility and how to choose between providers.

## 2. Key dates (all 2026, all IST)
| Date | What |
|---|---|
| Sun 22 Nov | Setup email arrived (late). Section and subdomain confirmed. Dates moved for everyone. |
| Mon 23 Nov – Wed 2 Dec | **Results window (moved from 21–30 Nov).** Traffic is counted over these dates, the same for everyone. |
| Sat 28 Nov | Reminder email from Vyohm (original date, may have moved). |
| **Sun 29 Nov** | **Our real deadline.** The user's exams start Mon 30 Nov. |
| Wed 2 Dec, 11:59 PM IST | Official submission deadline (moved from Mon 30 Nov). |
| By Tue 1 Dec | Vyohm confirms receipt. |
| By Fri 4 Dec | Review, plus **short calls with the strongest entries to walk through their code**. This falls during exams. |
| Sun 6 Dec | Results and prizes. |
| 30 Nov – 15 Dec | User's exams. |

## 3. Arrangements with Vyohm (from the email thread, 19 Nov)
- **Spot confirmed** on the software track.
- **LinkedIn post is waived.** HR wrote that the demo can be shared on **YouTube or X, or sent directly with the submission** instead of the LinkedIn post. Quote this in the submission email, because the guide still says LinkedIn is required. Keep that email.
- **Section: CONFIRMED on 22 Nov (setup email from Vyohm).** "GPU cloud and AI infrastructure in India" at `gpu.aiatlasindia.com` (the 1st choice). The hub lists it as "GPU and cloud", Plate 06B2, with the line "Where to rent compute in India and what it costs."
- **Received 23 Nov (second setup email):** GA4 measurement ID `G-54RWD73RW5` (property "AI Atlas India - gpu", the user has Viewer access); Search Console full access to `https://gpu.aiatlasindia.com/` (submit the sitemap there once live); the section kit at aiatlasindia.com/kit/aiatlasindia-kit.zip (header.html, footer.html, tokens.css, logo.svg; rules at aiatlasindia.com/kit/, but ignore its "Going live" part).
- **Delivery (23 Nov, replaces the 22 Nov PR plan):** no shared repository. We host the public pages and the engine ourselves (Vercel, Netlify or Cloudflare Pages), add `gpu.aiatlasindia.com` as a custom domain, and reply to the email with the DNS record the host shows (type, name, value). Vyohm adds it within 12 hours. Nothing goes into their repository. See D17.
- **Kit rules worth remembering:** use the header, footer, tokens and logo unchanged; the logo on ink has a yellow marker; never add colours; never add trackers of our own (the GA4 tag is theirs, so it is allowed); caption AI images "Illustration"; label Vyohm products with the ownership label.
- **Prize:** top 3 get ₹3,000, ₹2,000 or ₹1,000 plus a paid internship offer (6 months, ₹15,000–22,000/month depending on hours).
- The guide does **not** say whether there is a further interview after winning. It says the assignment "stands in for" the missed in-person round. Assume the Dec 4 call is a code walkthrough, so the user must understand all the code.

## 4. Rules for building on aiatlasindia.com (from the guide, on every page)
- **Name and link:** call the site "AI Atlas India", link to aiatlasindia.com from the header, and name the section.
- **Footer ownership line, exact wording:**
  > AI Atlas India is owned by Vyohm AI Private Limited, which also sells AI products. We cover every provider, Vyohm included, by the same rules.
- **No paid placements:** no affiliate links, sponsored listings, or rankings in exchange for anything.
- **Vyohm gets no special treatment.** If Vyohm, wotbot.ai or shotbot.ai fits a question, include it next to the alternatives, labelled exactly **"Owned by Vyohm, the company that runs this site"**, and judge it by the same criteria.
- **Source every fact about a provider.** Prices, features, languages and data location come from the provider's own site or docs, linked, with the date checked. If it can't be confirmed, leave it out.
- **Fair criticism only.** A negative point needs a source or the expert's stated first-hand experience.
- **Answer real buying questions** ("What does it cost per month?", "Does it work with X?"). No generic "What is AI" pages.
- **Work stays up.** Approved answers may stay on the site afterwards, credited to the user and the expert.
- **Expert independence.** The expert is not employed or paid by any provider the section covers. If they have any link to one, the page says so.

## 5. Ground rules (breaking any one disqualifies the entry)
| Rule | Meaning |
|---|---|
| No bought or faked reach | No ads, boosted posts, bought followers, traffic exchanges, scripts, or friends and family clicking. Vyohm can see this in GA4. |
| No planted mentions | Never post our links on forums, comment sections or other people's accounts, and never ask anyone to. |
| No mass publishing | **Max 20 answers in total**, and never more than the expert approved. 10 strong answers beat 20 thin ones. |
| No fake experts | A real person who agreed **in writing** to be named. No invented names, AI headshots or made-up credentials. |
| No hidden relationships | Ownership line on every page. Disclose any link between us, the expert and a covered provider. |
| No unchecked claims about companies | Every provider fact has a source link and the date checked. |
| No copied content | Brief quotes with a link only. Never republish others' text or images. |
| Look after people's data | Store only what the reply workflow needs from commenters, and delete it when the assignment ends. |

## 6. What Vyohm gives and what we pay
- **Given:** a subdomain (we host anywhere; they point it at our host), a GA4 property (we install their tag; Viewer access), and Search Console access (including the Generative AI performance report).
- **We pay:** hosting, AI model and API costs. Free tiers should cover it.
- **To ask Vyohm:** a way for our backend to read GA4 and Search Console through an API (a service account added as viewer).

## 7. The levels: acceptance criteria (build in order)
### Level 1: Go live
- [ ] Section live on our subdomain, GA4 tag installed, sitemap submitted in Search Console.
- [ ] Header (AI Atlas India link and section name) and the exact footer line on every page.
- [ ] About page: who built it, who the expert is, how AI drafts answers, and that Vyohm AI owns the site.
- [ ] One social account linked (Bluesky), **marked as automated** with the bot self-label.

### Level 2: Find questions
- [x] (done 22 Nov: Stack Exchange and Hacker News, see DECISIONS D18) Questions from **at least two sources**, through official APIs or exports. Options: Search Console queries, Google Trends export, Stack Exchange API, Bluesky/Mastodon search, YouTube Data API comments, Hacker News API.
- [ ] Never scrape Google results, "People also ask", or Quora. No Reddit.
- [x] Rank the questions, with a stored reason for each pick. (done 22 Nov, `questions.rank_reason`)
- [x] Merge near-duplicates: one strong page per question. (done 22 Nov within a batch, `questions.merged_into`; see the ponytail note in `rank.py` for the limit)

### Level 3: AI drafts answers
- [x] Each draft cites its sources and stays a draft until checked. (S6: every fact has a quote and date; `prechecked` needs every fact ticked)
- [x] The AI also drafts the page title, meta description, image alt text and structured data. All are checked with the answer. (S6: JSON-LD is built by code from the checked fields; title, meta and alt are reviewed by the expert in Level 4)
- [ ] Every answer adds something a generic AI summary wouldn't: the expert's own advice, a real price checked on a date, a screenshot, or a worked example.

### Level 4: Expert check
- [ ] Each draft goes to the expert by **email** (WhatsApp only through the official Business Platform, so skip it).
- [ ] The reply is recorded: **approved / edited / rejected**.
- [ ] Only approved answers publish. Before and after versions are shown in the admin view.
- [ ] Each page credits the expert as reviewer by real name, with written permission, and says it was drafted with AI.

### Level 5: Social
- [ ] The AI writes a post for each published answer and schedules it. Posts go out on their own at the set time.
- [ ] Fetch replies and mentions, draft responses, and **a human approves every reply** before it's sent.
- [ ] Reply only to people who reply to or mention us. No automated follows, likes, reposts or DMs.

### Level 6: Measure and suggest
- [ ] Dashboard showing human visitors and **AI traffic**: referrals from ChatGPT, Perplexity, Gemini and Copilot, plus AI-crawler hits (GPTBot, ClaudeBot, PerplexityBot) from our own logs.
- [ ] Search Console impressions, including the Generative AI report (no API, so a manual export and upload).
- [ ] How each post performed.
- [ ] The AI says what the audience responds to and what to post next, and why. A person picks.

### Level 7 (bonus, up to +10): A/B test. **SKIP unless everything else is done.**
If done: use our own GrowthBook or PostHog account; write the hypothesis, metric and stop date first; test presentation only (not facts); follow Google's testing rules (no cloaking, `rel="canonical"` on variants, 302 redirects, remove the test after). Report honestly: "not enough data", with the numbers, earns full marks.

## 8. How we are judged
| Criterion | Weight | What they look at |
|---|---|---|
| Working system | **35%** | Highest level reached, end-to-end runs, reliability, code quality |
| Content and expert review | **25%** | Accuracy and usefulness, handling of expert edits, metadata checked |
| Results | 20% | Human visitors, Search Console impressions (including AI features), AI referrals, social engagement. **LinkedIn visits don't count.** |
| Judgment | 10% | Ground rules kept, AI use and ownership disclosed, sources cited, accounts labelled automated |
| Demo and write-up | 10% | Clear explanation of what was built, what failed, and what comes next |

## 9. Submission (one email to careers@vyohm.com)
- [ ] Link to the live section.
- [ ] Code repository, **shared with the `vyohm` GitHub org**.
- [ ] Demo video of **5 minutes or less**: one answer going question → expert check → published page → social post.
- [ ] **One-page write-up:** how it works, **the prompts the engine sends to the LLM** (not our chat with Claude), how we checked the AI's output, and what broke. Add a line saying AI coding tools were used to build it.
- [ ] Demo link (YouTube or X, per HR's waiver) instead of the LinkedIn post, quoting the waiver.
- [ ] Video check: **no API keys, passwords, expert phone or email, or commenter names on screen.**

## 10. Checkpoints
### Every session
- [ ] Read `docs/HANDOFF.md`. Know the next action before coding.
- [ ] Is the current work on the critical path to the next unfinished level? If not, stop.
- [ ] At the end, update HANDOFF (state, next step, what broke).

### Before sending a draft to the expert (the user's pre-check, about 10–15 minutes per answer)
- [ ] Every provider fact has a source URL, a snippet and a checked date, and matches the source.
- [ ] No facts beyond the sources. Unconfirmed facts are removed.
- [ ] Title, meta description, alt text and structured data read correctly.
- [ ] Any Vyohm product is labelled and judged the same way as the others.
- [ ] Negative points have a source or are marked as the expert's experience.
- [ ] There is a slot for the expert's own advice (the "added value").

### Before publishing a page
- [ ] Status is `approved` (or `edited` and approved). Before and after versions are saved.
- [ ] Expert credited by real name, plus "drafted with AI" disclosure.
- [ ] Header, section name and exact footer line are present.
- [ ] Published count after this page is **≤ 20**.
- [ ] Page is in the sitemap and server-rendered (view source shows the text).

### Before any social action
- [ ] The post is about our own published answer.
- [ ] The reply goes to someone who replied to or mentioned us, and a human approved it.
- [ ] No follows, likes, reposts or DMs anywhere in the code.

### Before submission
- [ ] Every ground rule is re-read and confirmed.
- [ ] Commenter data deletion is planned (or done after results).
- [ ] Repo has no secrets (`git log -p | grep -i key` and similar).

## 11. Decisions from our discussion with the user
- **Stack:** Next.js (React) for the frontend, FastAPI (Python) for the backend, Neon Postgres, Gemini free tier, Bluesky, Resend email, external cron, all on Vercel. Details and reasons are in `docs/DECISIONS.md`.
- **Scope cuts to save time:** skip Level 7, use only Bluesky, use exactly 2 question sources, publish 8–10 answers, no fancy UI.
- **Do not cut:** the real expert, the sources with dates, the disclosures, and the end-to-end loop.
- **"Sourced content" means:** the AI drafts **only from sources we supply** (provider pricing and docs pages). Each fact is stored with its URL, snippet and date. The user spends about 10–15 minutes per answer checking facts before the expert sees the draft. The expert also gives 2–3 lines of first-hand advice per answer (the "added value").
- **Expert:** a college senior is acceptable **if** they have real hands-on cloud or DevOps experience and their credentials are stated honestly. A working professional is stronger. They must reply fast (8–10 reviews within about a week). Disclose a friendship on the About page.
- **Effort estimate:** about 3,000 lines of code; 20–30 focused hours of building; 10–15 minutes a day after go-live.
- **Priority:** get the site live early (impressions count from Nov 21), and get the first 3 drafts to the expert by about Nov 23.

## 12. Open questions
- [x] Which section is assigned? GPU cloud and AI infrastructure in India (22 Nov).
- [x] How does the section reach the subdomain? We host it; Vyohm adds our DNS record (23 Nov, D17).
- [x] Which footer wording does the kit use? The hub's sentence. We show it unchanged plus the guide's exact line (D16).
- [ ] Who is the expert? (The user is lining someone up.)
- [ ] Ask Vyohm: is a student with hands-on cloud experience acceptable as the expert?
- [ ] Ask Vyohm: what format is the Dec 4 call? (Exams.)
- [ ] Ask Vyohm: can a service account get GA4 and Search Console API read access?
- [ ] Verify the current free-tier limits: Vercel (cron, function timeout, logs), Neon, Gemini, Resend.
- [x] Verify how to set the Bluesky bot self-label. (23 Nov: profile self-label `bot`, set by `python -m social.setup`; D25)
