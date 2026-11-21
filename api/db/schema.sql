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
