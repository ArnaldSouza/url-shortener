from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Link
from app.services.device import classify_device
from app.workers.tasks import register_click

router = APIRouter(tags=["redirect"])


@router.get("/{short_code}")
def redirect_to_target(
    short_code: str, request: Request, db: Session = Depends(get_db)
) -> RedirectResponse:
    """Redirect a short code to its target URL and queue a click for analytics.

    The click is recorded asynchronously via Celery, so counting never blocks
    the redirect response.
    """
    link = db.scalar(select(Link).where(Link.short_code == short_code))
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Short code not found."
        )

    device_type = classify_device(request.headers.get("user-agent"))
    register_click.delay(link.id, device_type)

    return RedirectResponse(
        url=link.target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
