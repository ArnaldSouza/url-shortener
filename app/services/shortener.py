import secrets
import string
from typing import Final

_ALPHABET: Final = string.ascii_letters + string.digits
_DEFAULT_LENGTH: Final = 7


def generate_short_code(length: int = _DEFAULT_LENGTH) -> str:
    """Generate a random base62 short code.

    Uses the ``secrets`` module to make codes unpredictable, which prevents
    guessing valid short codes. Collisions are possible but unlikely; the
    caller must enforce uniqueness (the database has a unique constraint).
    """
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))
