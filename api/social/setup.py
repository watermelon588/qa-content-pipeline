"""Run once after creating the Bluesky account: checks the login works and labels the account as a bot.
From api/:  .venv/Scripts/python -m social.setup"""
from social import bluesky

if __name__ == "__main__":
    if not bluesky.ready():
        raise SystemExit("Add BLUESKY_HANDLE and BLUESKY_APP_PASSWORD to api/.env first.")
    session = bluesky.login()
    bluesky.mark_as_bot(session)
    print(f"Logged in as {session['handle']}. The profile now carries the 'bot' self-label.")
