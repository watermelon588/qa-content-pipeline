"""Who may review, and the personal code that proves it.
Each expert has a short code (like K7QM-4XRT) that we send them once, separately from the review email. A review
link is assigned to one expert when it is sent, and it opens only with that expert's code. So a forwarded email is
useless without the code, the same link can't be used by both experts, and every decision is recorded under a name.

The codes live only in the EXPERT_CODES environment variable (api/.env locally, the Vercel project settings live),
never in the repo. Format: EXPERT_CODES=sanath:K7QM4XRT,prince:9WPD3HJA"""
import hmac
import secrets

from core.config import EXPERT_CODES

# The name shown on each answer the expert approves. Only names they agreed to have shown.
EXPERTS = {
    "sanath": "Sanath W, Senior DevOps Engineer",
    "prince": "Prince Patel",
}

ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # no 0/O or 1/I/L, so a code read aloud or typed can't be misread
CODE_LENGTH = 8                                 # 31^8 is about 850 billion codes; with a 1 s wait per wrong try,
                                                # guessing one takes thousands of years even at many tries a second


def clean(code):
    """What the expert typed, minus spaces and dashes, in capitals: 'k7qm-4xrt ' and 'K7QM4XRT' are the same code."""
    return "".join(ch for ch in str(code).upper() if ch.isalnum())


def codes(setting=EXPERT_CODES):
    """{"sanath": "K7QM4XRT", ...} from the setting. Unknown names and empty codes are ignored, so a half-filled
    setting can never let an empty code in."""
    found = {}
    for part in setting.split(","):
        name, _, code = part.partition(":")
        name, code = name.strip(), clean(code)
        if name in EXPERTS and code:
            found[name] = code
    return found


def who(code, setting=EXPERT_CODES):
    """The expert this code belongs to ("sanath"), or None. Compares in constant time, so the response time doesn't
    reveal how many characters of a guess were right."""
    typed = clean(code).encode()
    match = None
    for name, real in codes(setting).items():
        if typed and hmac.compare_digest(typed, real.encode()):
            match = name
    return match


def new_code():
    """A fresh code. Run once per expert: .venv/Scripts/python -c "from review.experts import new_code; print(new_code())" """
    return "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))
