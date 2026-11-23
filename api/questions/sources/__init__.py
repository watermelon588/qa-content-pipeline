"""Every question source, by name. To add one (Search Console, YouTube, Bluesky): write a file with a
fetch() that returns [{"text", "source_url"}], import it here and add one line to SOURCES."""
from questions.sources import hackernews, stackexchange

SOURCES = {
    "stackexchange": stackexchange.fetch,
    "hackernews": hackernews.fetch,
}
