-- Empty every table of test data before real drafting starts. Keeps the tables themselves.
-- Paste it into Neon's SQL Editor (console.neon.tech -> your project -> SQL Editor) and run it. It can't be undone.
-- Also the end-of-assignment cleanup for commenter data (the replies table).
TRUNCATE replies, posts, pages, reviews, facts, drafts, suggestions, hits, uploads, questions RESTART IDENTITY;
