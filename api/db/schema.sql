-- Database tables. Safe to run more than once (IF NOT EXISTS).
-- Each level adds only the tables it needs.

-- Level 2: questions people ask, collected from official APIs.
CREATE TABLE IF NOT EXISTS questions (
    id          SERIAL PRIMARY KEY,
    text        TEXT NOT NULL,
    source      TEXT NOT NULL,                       -- where it came from, e.g. 'stackexchange'
    source_url  TEXT,                                -- link to the original question
    score       REAL,                                -- rank score given by the LLM
    rank_reason TEXT,                                -- why it got that score (the guide asks us to store this)
    merged_into INTEGER REFERENCES questions(id),    -- set when this is a near-duplicate of another question
    status      TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'selected', 'drafted')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- The same question must never be stored twice, so collecting can safely run again and again.
CREATE UNIQUE INDEX IF NOT EXISTS questions_source_url_key ON questions (source_url);

-- Level 3: the AI's draft answer to one selected question. Every regeneration is a new version, so older ones stay.
-- The status list is the whole flow from ARCHITECTURE.md; core/status.py decides which moves are allowed.
CREATE TABLE IF NOT EXISTS drafts (
    id               SERIAL PRIMARY KEY,
    question_id      INTEGER NOT NULL REFERENCES questions(id),
    version          INTEGER NOT NULL,
    title            TEXT NOT NULL,
    body             TEXT NOT NULL,                      -- markdown; [1], [2] point to the facts below
    meta_description TEXT NOT NULL,
    alt_text         TEXT NOT NULL,
    json_ld          JSONB NOT NULL,                     -- structured data for search engines, built by code
    expert_questions TEXT[] NOT NULL DEFAULT '{}',       -- what we will ask the expert (Level 4 emails them)
    status           TEXT NOT NULL DEFAULT 'draft'
                     CHECK (status IN ('draft', 'prechecked', 'in_review', 'approved', 'edited', 'rejected', 'published')),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (question_id, version)
);

-- Level 3: every claim about a provider, with where it came from and when we looked.
CREATE TABLE IF NOT EXISTS facts (
    id         SERIAL PRIMARY KEY,
    draft_id   INTEGER NOT NULL REFERENCES drafts(id),
    n          INTEGER NOT NULL,                         -- the [n] marker in the draft body
    claim      TEXT NOT NULL,
    source_url TEXT NOT NULL,
    snippet    TEXT NOT NULL,                            -- the exact words copied from the source page
    checked_on DATE NOT NULL,                            -- the day we read the page (India time)
    verified   BOOLEAN NOT NULL DEFAULT false,           -- ticked by a person during the pre-check
    UNIQUE (draft_id, n)
);

-- Level 4: a draft can now also be 'published'. A table that already exists keeps its old CHECK, so swap it.
ALTER TABLE drafts DROP CONSTRAINT IF EXISTS drafts_status_check;
ALTER TABLE drafts ADD CONSTRAINT drafts_status_check
    CHECK (status IN ('draft', 'prechecked', 'in_review', 'approved', 'edited', 'rejected', 'published'));

-- Level 4: each time a draft is sent to the expert. The link's code is stored only as a SHA-256 fingerprint.
-- The draft's own body is the BEFORE version; edited_body is the expert's AFTER version.
CREATE TABLE IF NOT EXISTS reviews (
    id          SERIAL PRIMARY KEY,
    draft_id    INTEGER NOT NULL REFERENCES drafts(id),
    token_hash  TEXT NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    decision    TEXT CHECK (decision IN ('approved', 'edited', 'rejected')),  -- empty until the expert answers
    edited_body TEXT,                                    -- the expert's version, when they edit
    advice      TEXT,                                    -- their first-hand advice, shown on the page with their name
    note        TEXT,                                    -- why they rejected it
    decided_at  TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Level 4: published answers. pages/router.py refuses a 21st row (the guide's hard limit is 20).
CREATE TABLE IF NOT EXISTS pages (
    id           SERIAL PRIMARY KEY,
    draft_id     INTEGER NOT NULL UNIQUE REFERENCES drafts(id),
    slug         TEXT NOT NULL UNIQUE,                   -- the page address: /q/<slug>
    published_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Level 5: one Bluesky post per published answer. The AI drafts it; you edit it and pick when it goes out;
-- POST /jobs/social sends it once that time has passed.
CREATE TABLE IF NOT EXISTS posts (
    id         SERIAL PRIMARY KEY,
    page_id    INTEGER NOT NULL UNIQUE REFERENCES pages(id),   -- only our own answers, once each
    text       TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'drafted' CHECK (status IN ('drafted', 'scheduled', 'sent', 'failed')),
    send_at    TIMESTAMPTZ,                                     -- when it may go out (set when scheduled)
    uri        TEXT,                                            -- Bluesky's address for the post, once sent
    error      TEXT,                                            -- why sending failed
    sent_at    TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Level 5: posts that replied to or mentioned us, and our answer to each. A person approves every reply.
-- Commenter data kept to the minimum a reply needs: their post's address (it contains their account id) and
-- its text. No names or handles. Delete it all when the assignment ends: DELETE FROM replies;
CREATE TABLE IF NOT EXISTS replies (
    id         SERIAL PRIMARY KEY,
    their_uri  TEXT NOT NULL UNIQUE,                            -- the post that replied to or mentioned us
    their_cid  TEXT NOT NULL,
    root_uri   TEXT NOT NULL,                                   -- the first post of that thread
    root_cid   TEXT NOT NULL,
    their_text TEXT NOT NULL,
    reason     TEXT NOT NULL CHECK (reason IN ('reply', 'mention')),
    draft      TEXT,                                            -- the AI's suggested reply (BEFORE)
    final_text TEXT,                                            -- what was actually sent (AFTER)
    decision   TEXT CHECK (decision IN ('approved', 'edited', 'rejected')),
    status     TEXT NOT NULL DEFAULT 'fetched' CHECK (status IN ('fetched', 'drafted', 'sent', 'discarded')),
    our_uri    TEXT,                                            -- our reply on Bluesky, once sent
    decided_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Level 6: how each Bluesky post performed. POST /jobs/social copies Bluesky's counts here each run.
ALTER TABLE posts ADD COLUMN IF NOT EXISTS likes    INTEGER NOT NULL DEFAULT 0;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS reposts  INTEGER NOT NULL DEFAULT 0;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS replies  INTEGER NOT NULL DEFAULT 0;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS quotes   INTEGER NOT NULL DEFAULT 0;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS stats_at TIMESTAMPTZ;

-- Level 6: AI traffic from our own logs. web/proxy.ts reports each AI-crawler visit and each visit that came from
-- an AI assistant. Only a count per (kind, name, page, day): no IP address, no user agent, nothing about a person.
CREATE TABLE IF NOT EXISTS hits (
    kind  TEXT NOT NULL CHECK (kind IN ('crawler', 'referral')),
    name  TEXT NOT NULL,                                  -- e.g. 'GPTBot' or 'ChatGPT'
    path  TEXT NOT NULL,                                  -- the page, e.g. /q/h100-price
    day   DATE NOT NULL,                                  -- India date
    count INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (kind, name, path, day)
);

-- Level 6: CSV exports uploaded by hand (GA4 and Search Console give the user Viewer access, not an API key, and
-- the Generative AI report has no API at all). Uploading the same file name again replaces the old copy.
CREATE TABLE IF NOT EXISTS uploads (
    id          SERIAL PRIMARY KEY,
    kind        TEXT NOT NULL CHECK (kind IN ('ga4', 'gsc', 'gsc_ai')),
    filename    TEXT NOT NULL,
    header      TEXT[] NOT NULL,
    rows        JSONB NOT NULL,                           -- list of rows, each a list of cells
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (kind, filename)
);

-- Level 6: what the AI suggests answering next, and why. A person picks by selecting the question (Level 2's button).
CREATE TABLE IF NOT EXISTS suggestions (
    id         SERIAL PRIMARY KEY,
    insight    TEXT NOT NULL,                             -- what the audience responds to
    picks      JSONB NOT NULL,                            -- [{"question_id": 12, "reason": "..."}]
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Timeline: the two steps that had no time of their own. Every other step's time is already in its table.
ALTER TABLE questions ADD COLUMN IF NOT EXISTS selected_at   TIMESTAMPTZ;   -- when you put it on the shortlist
ALTER TABLE drafts    ADD COLUMN IF NOT EXISTS prechecked_at TIMESTAMPTZ;   -- when the last fact was ticked
