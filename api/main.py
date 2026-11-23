from fastapi import FastAPI

from core.db import get_conn
from drafts.router import router as drafts_router
from pages.router import router as pages_router
from questions.router import router as questions_router
from review.router import router as review_router
from social.router import router as social_router

app = FastAPI(title="AI Atlas India content engine API")

# Each feature brings its own router; mounting them here is the only wiring main.py does.
app.include_router(questions_router)
app.include_router(drafts_router)
app.include_router(review_router)
app.include_router(pages_router)
app.include_router(social_router)


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
