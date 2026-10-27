import string

from app.services.shortener import generate_short_code


def test_generate_short_code_default_length() -> None:
    assert len(generate_short_code()) == 7


def test_generate_short_code_custom_length() -> None:
    assert len(generate_short_code(10)) == 10


def test_generate_short_code_uses_base62_alphabet() -> None:
    allowed = set(string.ascii_letters + string.digits)
    code = generate_short_code()
    assert set(code).issubset(allowed)


def test_generate_short_code_is_random() -> None:
    codes = {generate_short_code() for _ in range(100)}
    assert len(codes) > 90  # overwhelmingly unique; no hard guarantee
