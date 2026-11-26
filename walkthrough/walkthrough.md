# Demo video walkthrough: Parts 1–2 (question → draft → sent to the expert)

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
| **2 (this file)** | Check facts, send to expert | **~0:45** |
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

> ⚠ **If drafting fails** (a red message like *"the draft was rejected 2 time(s), last reason: …"*): since the 26 Nov fix (D31) this should be rare. A misquoted fact is now dropped with the sentence that used it, instead of failing the whole draft, and the request always ends in time with a message instead of a blank "failed to load". If it still happens, click **Draft the answer** again, or tick fewer pages. Cut the failed attempt, or keep 5 seconds and say: *"Here my code caught the AI misquoting its sources and refused the draft. That's the check working."*
>
> **Tip:** do one practice draft on a different question before recording, so you know how long it takes today.

---

## Scene 6: The draft is ready (1:35 – 1:50)

**Screen:** Draft screen, `/admin?draft=<id>`

**Do:** Scroll the left side slowly: title, search-result text, the answer with its `[1] [2]` markers. Then point at the facts panel on the right. **Don't tick anything yet** (that's Part 2).

**Say:**
> "Here's the draft: a title, the text Google will show, and the answer, with a numbered marker on every fact.
> On the right is every fact with its source link, the exact quote and the date it was checked. If a quote isn't word for word on that page, my code deletes the fact and every sentence that used it, so nothing unsourced survives.
> But a quote existing doesn't prove it supports the sentence, so next I check each fact myself before the expert sees it."

**You should see:** On the left, **Draft v1 · DRAFT**, the title, the search-result text, the image alt text, a **Timeline (India time)** box (question collected → selected → draft written), then the answer. On the right, the **Facts** panel showing "0 of N checked", and for each fact: the claim, the exact quote, "Show the quote on …" with the date read, and a **The source says this** tick box. Below them is the yellow **Save ticked facts** button.

![Draft screen with facts panel](screens/08-draft.png)

*(This screenshot is a Google Cloud test draft, so your title and facts will match your own question.)*

---

**End of Part 1.**

---

# Part 2: check the facts, send to the expert (1:50 – 2:35)

Picks up on the draft screen where Scene 6 ended. Nothing has been ticked yet.

> The screenshots below come from the local test copy (test draft 8, a Google Cloud draft with 8 facts). Your title and facts will differ; the buttons and messages are the same.

### Extra privacy rules for this part

- [ ] **Don't open your Gmail.** On the live site, "Send" emails the review link to *your* inbox for forwarding. Never show the inbox or the email in the video.
- [ ] **Never show an expert's personal code.** The code isn't on this screen, so just don't type it or paste it anywhere while recording.
- [ ] **The one-time link appears on screen after sending.** It's useless without the expert's code, but don't zoom in on it or leave it on screen for long. Blur it in editing if you can.
- [ ] Showing the expert's **name and title** is fine: it's already on the About page and on every answer they approve. Their email and phone are not.

---

## Scene 7: Check one fact against its source (1:50 – 2:10)

**Screen:** Draft screen, `/admin?draft=<id>`, the **Facts** panel on the right.

**Do:**
1. Point at the hint at the top of the panel.
2. On fact **[1]**, read the claim aloud, then click **Show the quote on cloud.google.com ↗** (the host will match your fact's source).
3. A new tab opens on the provider's page with the quote **highlighted in yellow**. Hold it there for 2 seconds.
4. Go back to the desk tab and tick **The source says this** under fact [1].

**Say:**
> "Before any expert sees it, I check every fact myself. This claim says [read claim 1].
> I click 'Show the quote', and the provider's own page opens with that exact sentence highlighted. It says the same thing, so I tick it."

**You should see:** "0 of N checked" at the top. Each fact has its claim in bold, the quote in a grey box, the link with "read <date>", and a **The source says this** box. After ticking, the box turns yellow.

![Facts panel before checking](screens/10-facts-unchecked.png)

> **If nothing is highlighted** on the provider's page (some browsers or pages don't support it): press **Ctrl+F** and type a few words of the quote. If it's genuinely not there, leave that fact unticked (see the box after Scene 8).

---

## Scene 8: Tick the rest and save (2:10 – 2:20)

**Screen:** Same Facts panel.

**Do:** **Before recording,** check every other fact the same way. Then, on camera, tick the remaining boxes and click the yellow **Save ticked facts** at the bottom of the panel.

**Say:**
> "I've checked the other facts the same way. I tick them and save.
> Only when every single fact is ticked does the draft move on. One unticked fact and it stays here."

**You should see:** Every box yellow before you save. After saving, a green message: **"Every fact checked. The draft is pre-checked."** The badge at the top changes from **DRAFT** to a yellow **PRECHECKED**, each fact now says **CHECKED**, the counter says "N of N checked", and the timeline gets a new line, **"Every fact checked"**.

![All facts ticked, before saving](screens/11-facts-ticked.png)

> **Honesty note:** don't tick a fact on camera that you haven't actually checked. "I checked the rest off camera" is fine, as long as it's true.
>
> **If a fact is wrong** (the quote isn't on the page, or it doesn't say what the claim says): leave it unticked and click Save. The message says `Saved. 1 fact still to check.` and the draft can't go to the expert. Go **← Back to the question** and click **Draft a new version**, perhaps with different pages. That's a good honest moment to show if it happens.

---

## Scene 9: Send it to the expert (2:20 – 2:35)

**Screen:** Same draft screen. The top of the Facts panel now shows a **NEXT STEP** box.

**Do:** In **Send to**, choose the expert (Sanath W or Prince Patel). Click **Send to the expert**. The button says "Sending…" for a second or two.

**Say:**
> "Now it goes to a real expert. I pick who reviews it. The link only opens with that expert's personal code, so a forwarded email is useless to anyone else, and every decision is recorded under their name.
> Nothing gets published without their approval. My code enforces that, it's not just a promise."

**You should see:** Before clicking, the box says *"Every fact is checked. Choose the expert: the link opens only with their personal code."*

![Pre-checked draft with the Send to box](screens/12-prechecked.png)

After clicking:
- A green message: **"Review email for Sanath W, Senior DevOps Engineer sent to your inbox. Forward it to them, or copy the link below. It opens only with their code."** (The screenshot shows the wording from the test copy, where email is turned off.)
- The badge changes to **IN REVIEW**.
- The box changes to **WAITING FOR THE EXPERT**: *"… has a one-time link (it expires in 14 days). They haven't opened it yet."*
- Below it: **Send this one-time link to the expert** with the link. Don't linger on it (see the privacy rules).
- The timeline adds **"Sent for review to <expert>"**.

![Sent: waiting for the expert](screens/13-sent.png)

**After you stop recording:** forward the email from your inbox to the expert you chose (off camera). Their personal code was sent to them separately before, so don't send it again in the same email. Part 3 starts when they open the link.

---

**End of Part 2** (video so far: about 2:35). Tell me when it's recorded and I'll write Part 3 (the expert's review page: approve, edit or reject).
