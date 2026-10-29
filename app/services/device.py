from typing import Final

_BOT_MARKERS: Final = ("bot", "crawler", "spider", "curl", "wget", "python")
_MOBILE_MARKERS: Final = ("mobile", "android", "iphone", "ipad")


def classify_device(user_agent: str | None) -> str:
    """Classify a user agent into a coarse, non-identifying device category.

    Returns one of ``"bot"``, ``"mobile"``, ``"desktop"`` or ``"unknown"``.
    The raw user agent is inspected and discarded, never stored, which keeps
    click analytics free of personal data.
    """
    if not user_agent:
        return "unknown"
    ua = user_agent.lower()
    if any(marker in ua for marker in _BOT_MARKERS):
        return "bot"
    if any(marker in ua for marker in _MOBILE_MARKERS):
        return "mobile"
    return "desktop"
