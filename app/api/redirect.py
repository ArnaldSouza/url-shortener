from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Link

router = APIRouter(tags=["redirect"])


@router.get("/{short_code}")
def redirect_to_target(
    short_code: str, db: Session = Depends(get_db)
) -> RedirectResponse:
    """Redirect a short code to its target URL."""
    link = db.scalar(select(Link).where(Link.short_code == short_code))
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Short code not found."
        )
    return RedirectResponse(
        url=link.target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
