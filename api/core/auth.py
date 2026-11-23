"""Password check for the /jobs/* endpoints."""
import hmac

from fastapi import Header, HTTPException

from core.config import CRON_SECRET


def require_secret(authorization: str = Header(default="")):
    """FastAPI dependency: let the request through only with `Authorization: Bearer <CRON_SECRET>`."""
    expected = f"Bearer {CRON_SECRET}"
    # compare_digest takes the same time however many characters match, so the secret can't be guessed
    # letter by letter. An empty CRON_SECRET must never open the door.
    if not CRON_SECRET or not hmac.compare_digest(authorization.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Unauthorized")
