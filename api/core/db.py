"""Database connection (Neon Postgres)."""
import psycopg

from core.config import DATABASE_URL


def get_conn():
    """Open a connection. Use `with get_conn() as conn:` so it commits and closes on its own."""
    return psycopg.connect(DATABASE_URL)
