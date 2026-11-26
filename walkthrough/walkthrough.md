# Demo video walkthrough: Part 1 (question → draft)

Your script for recording. Each scene has: **Screen** (where you are), **Do** (what to click), **Say** (read it aloud), **You should see** (what to expect), and a screenshot.

## What Vyohm asks for (from the guide)

- **One video, 5 minutes or less**, showing **one answer** going from **question → expert check → published page → social post**.
- It is scored under "Demo and write-up" (10%): *how clearly you explain what you built, what failed and what you would do next.*
- **Nothing private on screen:** no API keys, passwords, your expert's phone number or email, or commenters' names.
- The same file gets uploaded to your LinkedIn post, so keep it tight.

## Time budget for the whole video

| Part | Covers | Time |
|---|---|---|
| **1 (this file)** | Intro, collect, rank, pick, draft | **~1:50** |
| 2 | Check facts, send to expert | ~0:45 |
| 3 | Expert's review page, approve or edit | ~0:50 |
| 4 | Publish, public answer page | ~0:50 |
| 5 | Bluesky post, wrap-up (what broke, what's next) | ~0:45 |

Ranking takes 1 to 2 minutes and drafting takes 1 to 4. **Cut those waits in editing** (or pause recording and resume). Never leave a spinner on screen for more than a second or two.

## Before you press record (privacy checklist)

- [ ] **Sign in before recording.** Go to `https://gpu.aiatlasindia.com/login` and sign in, then start recording on `/admin`. That keeps your username and password typing off the video. (If you want to show that the desk is private, show this empty sign-in page for 2 seconds, then cut to the desk.)

  ![Admin sign-in page](screens/01-login.png)
- [ ] Use a **clean browser window**: one tab, no bookmarks bar, no extensions showing your email or Gmail avatar. Incognito plus sign-in is easiest.
- [ ] **Do not show** VS Code, `.env` files, the API terminal (its error lines name your accounts), Vercel or Neon dashboards, or your Gmail inbox.
- [ ] Zoom the browser to about **110–125%** so text is readable on LinkedIn.
- [ ] The live database is empty right now (checked 26 Nov), so the video starts cleanly from "Collect". Don't run Collect before recording.

> The screenshots below for scenes 3 to 6 come from the **local test copy** of the database, so the question list and the left sidebar will differ from what you see live. The screens, buttons and messages are the same.

---

## Scene 0: Intro (0:00 – 0:15)

**Screen:** Public home page, `https://gpu.aiatlasindia.com/`

**Do:** Nothing. Let the page sit, scroll down a little if you like.

**Say:**
> "Hi, I'm Rohit. For the Vyohm AI assignment I built a content engine for the GPU and cloud section of AI Atlas India.
> The AI finds the questions Indian businesses ask about renting GPUs, and drafts answers. A real expert approves every answer before it goes live, and then it's posted to Bluesky.
> Let me show one answer going all the way through."

**You should see:** The "GPU and cloud" hero, "Owned and run by Vyohm AI" strip on top. "No published answers yet" lower down (until you publish).

![Public home page](screens/00-home.png)

---

## Scene 1: Open the answer desk (0:15 – 0:25)

**Screen:** Admin desk, `https://gpu.aiatlasindia.com/admin` (already signed in)

**Do:** Switch to the tab, or type `/admin` in the address bar.

**Say:**
> "This is my private answer desk. These seven boxes are the pipeline: collect, rank, select, draft, check facts, expert review, publish.
> The yellow box is always the one next step. Right now it's step one: collect."

**You should see:** All counters at 0, step 1 **Collect** in yellow, and the yellow button **Collect new questions**.

![Empty answer desk](screens/02-desk-empty.png)

---

## Scene 2: Collect questions (0:25 – 0:40)

**Screen:** Same desk.

**Do:** Click **Collect new questions**. Wait a few seconds.

**Say:**
> "Collect pulls real questions from the official Stack Exchange and Hacker News APIs. No scraping of Google or Quora, and no Reddit, as the rules say.
> It saves at most 20 new questions per run and skips ones it already has."

**You should see:** A message pops up at the bottom like `stackexchange: 12 new of 40, hackernews: 8 new of 25` (numbers will vary). Box 1 now shows a number of questions, and step 2 **Rank** turns yellow.

---

## Scene 3: Rank them (0:40 – 1:00)

**Screen:** Same desk.

**Do:** Click **Rank unscored**. The button says "Ranking (1 to 2 minutes)…". **Cut the wait.** When it's done, scroll down to **Ranked questions**.

**Say:**
> "Now the AI scores every question from 0 to 10: how likely is it that someone asking this is about to rent GPU compute? It writes a one-line reason for each score and merges duplicates.
> The reasons are the AI's, so I still judge them myself."

**You should see:** A message like `Ranked 20, merged 1 duplicates`. Below, a list sorted best first, each row with a red score, the question, the AI's reason, the site it came from, and a **Select** button.

![Ranked questions list](screens/04-ranked-list.png)

---

## Scene 4: Pick a question (1:00 – 1:15)

**Screen:** Question page, `/admin?q=<id>` (opens when you click a question's title)

**Do:** Click the **title** of a high-scoring buying question. Best kind: "Where can I rent a GPU cheaply?" or "Which cloud GPU for …". Avoid debugging or driver questions. Then click the yellow **Select this question**.

**Say:**
> "I'll pick this one: '[read the question title]'. It scored [score] because [read the AI's reason].
> The link at the top goes back to where a real person asked it. I select it, and it goes on my shortlist."

**You should see:** Before you click, the badge says **RANKED** with a "Why the AI ranked it" box. After you click, the message says `Added to your shortlist`, the badge changes to **SELECTED**, and the draft form appears.

![Question before selecting](screens/05-question-ranked.png)

---

## Scene 5: Draft the answer (1:15 – 1:35)

**Screen:** Same question page, now showing "Tick the provider pages…"

**Do:** Tick **2 provider pages** that fit the question (for example **E2E Networks GPU cloud (prices in rupees)** and **Google Cloud GPU pricing**). Click **Draft the answer**. The button says "Reading the pages and drafting (1 to 4 minutes, keep this tab open)…". **Cut the wait.**

**Say:**
> "Now I choose the sources. The AI may only use these provider pages, nothing from its own memory.
> It downloads the pages, writes the answer, and for every fact it has to copy the exact sentence from the page as proof."

**You should see:** The four provider tick boxes, "Use another page" for any other URL, and the yellow **Draft the answer** button. When it finishes, the page jumps to the draft screen by itself.

![Draft form with provider pages](screens/07-draft-form.png)

> ⚠ **If drafting fails** (a red message like *"the draft was rejected 3 times, last reason: fact 7: the snippet is not word for word…"*): this happened twice in my test run on 26 Nov. Just click **Draft the answer** again, or tick a different page. Cut the failed attempt from the video, or keep 5 seconds of it and say: *"Here my code caught the AI misquoting its source and refused the draft. That's the check working."* It's a good "what broke" moment for the write-up.
>
> **Tip:** do one practice draft on a different question before recording, so you know how long it takes today.

---

## Scene 6: The draft is ready (1:35 – 1:50)

**Screen:** Draft screen, `/admin?draft=<id>`

**Do:** Scroll the left side slowly: title, search-result text, the answer with its `[1] [2]` markers. Then point at the facts panel on the right. **Don't tick anything yet** (that's Part 2).

**Say:**
> "Here's the draft: a title, the text Google will show, and the answer, with a numbered marker on every fact.
> On the right is every fact with its source link, the exact quote and the date it was checked. My code rejects any fact whose quote isn't word for word on the page, and the AI gets up to three tries to fix it.
> But a quote existing doesn't prove it supports the sentence, so next I check each fact myself before the expert sees it."

**You should see:** On the left, **Draft v1 · DRAFT**, the title, the search-result text, the image alt text, a **Timeline (India time)** box (question collected → selected → draft written), then the answer. On the right, the **Facts** panel showing "0 of N checked", and for each fact: the claim, the exact quote, "Show the quote on …" with the date read, and a **The source says this** tick box. Below them is the yellow **Save ticked facts** button.

![Draft screen with facts panel](screens/08-draft.png)

*(This screenshot is a Google Cloud test draft, so your title and facts will match your own question.)*

---

**End of Part 1.** Stop here. Tell me when it's recorded and I'll write Part 2 (check facts → send to the expert).
