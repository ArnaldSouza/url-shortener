from fastapi import HTTPException, Request, status

from app.services.rate_limit import is_rate_limited


def enforce_rate_limit(request: Request) -> None:
    """FastAPI dependency that blocks requests exceeding the rate limit.

    Identifies the client by IP address. Raises HTTP 429 when the limit is hit.
    """
    client_ip = request.client.host if request.client else "unknown"
    if is_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
        )
