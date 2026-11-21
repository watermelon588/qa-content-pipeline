"""Create the tables in Neon. From the api/ folder: .venv/Scripts/python -m db.init_db"""
from pathlib import Path

from core.db import get_conn

SCHEMA = Path(__file__).with_name("schema.sql").read_text()

if __name__ == "__main__":
    with get_conn() as conn:
        conn.execute(SCHEMA)
    print("Tables ready.")
