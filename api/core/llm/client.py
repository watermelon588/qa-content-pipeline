"""llm(): send a prompt, get text back. Tries each model in FALLBACK until one answers."""
import time

from openai import OpenAI, OpenAIError

from core.config import LLM_MODE
from core.llm.models import FALLBACK, FALLBACK_DEV, FALLBACK_FINAL, PROVIDERS


def _ask(provider, model, messages):
    """Send one chat request to one model and return its reply text."""
    p = PROVIDERS[provider]
    # max_retries=0: on an error, move straight to the next model instead of waiting and retrying.
    client = OpenAI(base_url=p["base_url"], api_key=p["api_key"], max_retries=0, timeout=60)
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content


RETRY_WAIT = 5  # seconds. "Busy" errors (503 overloaded, 429 rate limit) usually clear within a few seconds.


def llm(prompt, system=None):
    """Return the first successful answer. Goes down the list twice, pausing in between.
    Raises RuntimeError (with every model's error) if all of them fail both times."""
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": prompt})

    errors = []
    for attempt in range(2):
        if attempt:
            time.sleep(RETRY_WAIT)
        for provider, model in FALLBACK:
            if not PROVIDERS[provider]["api_key"]:
                continue  # no key in .env, so skip this provider
            try:
                return _ask(provider, model, messages)
            except OpenAIError as e:
                errors.append(f"{provider}/{model}: {e}")
    raise RuntimeError("All LLMs failed:\n" + "\n".join(errors))


if __name__ == "__main__":
    # Check every model in both lists once. From the api/ folder: .venv/Scripts/python -m core.llm.client
    print(f"Active list: LLM_MODE={LLM_MODE!r}")
    for name, chain in (("dev", FALLBACK_DEV), ("final", FALLBACK_FINAL)):
        print(f"-- {name}")
        for provider, model in chain:
            if not PROVIDERS[provider]["api_key"]:
                print(f"SKIP {provider}/{model}: no key in .env")
                continue
            try:
                reply = _ask(provider, model, [{"role": "user", "content": "Reply with just: hi"}])
                print(f"OK   {provider}/{model}: {reply!r}")
            except OpenAIError as e:
                print(f"FAIL {provider}/{model}: {str(e)[:100]}")
