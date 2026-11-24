"""llm(): send a prompt, get text back. Tries each model in a fallback list until one answers."""
import time

from openai import OpenAI, OpenAIError

from core.config import LLM_MODE
from core.llm.models import FALLBACK, FALLBACK_BEST, FALLBACK_DEV, FALLBACK_FINAL, PROVIDERS

MAX_TOKENS = 32_000  # room for the reply. "Thinking" models (gpt-oss, Nemotron) spend part of it reasoning before they
                     # write, and with the provider's small default the visible reply came back empty or cut off.
TIME_LIMIT = 270     # seconds for one whole llm() call. Vercel stops a request at 300 s, so we give up a little before.
RETRY_WAIT = 5       # seconds. "Busy" errors (503 overloaded, 429 rate limit) usually clear within a few seconds.


class CutOff(Exception):
    """The model answered, but the reply is empty or was cut off at the length limit."""


def _ask(provider, model, messages, json=False, timeout=60):
    """Send one chat request to one model and return its reply text."""
    p = PROVIDERS[provider]
    # max_retries=0: on an error, move straight to the next model instead of waiting and retrying.
    client = OpenAI(base_url=p["base_url"], api_key=p["api_key"], max_retries=0, timeout=timeout)
    # json=True asks for JSON mode: the provider makes the model reply with one valid JSON object, nothing else.
    extra = {"response_format": {"type": "json_object"}} if json else {}
    response = client.chat.completions.create(model=model, messages=messages, max_tokens=MAX_TOKENS, **extra)
    choice = response.choices[0]
    if choice.finish_reason == "length" or not choice.message.content:
        raise CutOff(f"reply empty or cut off (finish_reason={choice.finish_reason})")
    return choice.message.content


def llm(prompt, system=None, json=False, best=False, deadline=None):
    """Return the first successful answer. Goes down the list twice, pausing in between.
    json: reply must be one JSON object. best: use FALLBACK_BEST (slower, stronger models) for drafts and ranking.
    deadline: a time.monotonic() value after which no new model is tried (default: TIME_LIMIT from now).
    Raises RuntimeError (with every model's error) if all of them fail."""
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": prompt})
    deadline = deadline or time.monotonic() + TIME_LIMIT

    errors = []
    for attempt in range(2):
        if attempt:
            time.sleep(RETRY_WAIT)
        for provider, model in FALLBACK_BEST if best else FALLBACK:
            if not PROVIDERS[provider]["api_key"]:
                continue  # no key in .env, so skip this provider
            left = deadline - time.monotonic()
            if left < 15:
                errors.append("out of time")
                raise RuntimeError("All LLMs failed:\n" + "\n".join(errors))
            try:
                # A strong model on a long prompt can take 2 minutes; a quick task gets at most 60 s per model.
                return _ask(provider, model, messages, json, timeout=left if best else min(left, 60))
            except (OpenAIError, CutOff) as e:
                errors.append(f"{provider}/{model}: {str(e)[:200]}")
    raise RuntimeError("All LLMs failed:\n" + "\n".join(errors))


if __name__ == "__main__":
    # Check every model in every list once. From the api/ folder: .venv/Scripts/python -m core.llm.client
    print(f"Active list: LLM_MODE={LLM_MODE!r}")
    for name, chain in (("dev", FALLBACK_DEV), ("final", FALLBACK_FINAL), ("best", FALLBACK_BEST)):
        print(f"-- {name}")
        for provider, model in chain:
            if not PROVIDERS[provider]["api_key"]:
                print(f"SKIP {provider}/{model}: no key in .env")
                continue
            try:
                reply = _ask(provider, model, [{"role": "user", "content": 'Reply with the JSON {"ok": true}'}], json=True)
                print(f"OK   {provider}/{model}: {reply!r}")
            except (OpenAIError, CutOff) as e:
                print(f"FAIL {provider}/{model}: {str(e)[:100]}")
