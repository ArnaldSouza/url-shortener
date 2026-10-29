from app.services.device import classify_device


def test_classify_none_returns_unknown() -> None:
    assert classify_device(None) == "unknown"


def test_classify_empty_returns_unknown() -> None:
    assert classify_device("") == "unknown"


def test_classify_mobile() -> None:
    ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"
    assert classify_device(ua) == "mobile"


def test_classify_desktop() -> None:
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    assert classify_device(ua) == "desktop"


def test_classify_bot() -> None:
    assert classify_device("curl/8.0.1") == "bot"


def test_bot_takes_precedence_over_mobile() -> None:
    # A bot UA that also mentions "mobile" must classify as bot, not mobile.
    assert classify_device("Googlebot-Mobile/2.1") == "bot"
