"""Prints DATABASE_URL with search_path=test added, so a local API using it reads and writes a separate 'test' schema
(its own copy of every table inside the same Neon database) and never touches the live tables.
Creating the schema (once): .venv/Scripts/python -c "import psycopg; from core.config import DATABASE_URL as u; psycopg.connect(u).execute('CREATE SCHEMA IF NOT EXISTS test').connection.commit()"
then run db/schema.sql with the printed address (see docs/HANDOFF.md, "Local test copy").
Use the pooled address's direct twin: the pooled one refuses startup options, so "-pooler" is removed."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # so `core` is importable from anywhere
from core.config import DATABASE_URL  # noqa: E402

url = DATABASE_URL.replace("-pooler", "")
print(url + ("&" if "?" in url else "?") + "options=-c%20search_path%3Dtest")
