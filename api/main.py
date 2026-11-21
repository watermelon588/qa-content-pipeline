from fastapi import FastAPI

from core.db import get_conn

app = FastAPI(title="AI Atlas India content engine API")


@app.get("/health")
def health():
    """Shows the API is up and whether it can reach the database."""
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1")
        db = "ok"
    except Exception as e:
        db = f"error: {type(e).__name__}"  # only the error type, so no connection details leak
    return {"ok": True, "db": db}
