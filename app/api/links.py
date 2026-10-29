from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import enforce_rate_limit
from app.models import Link
from app.schemas.link import LinkCreate, LinkResponse
from app.services.shortener import generate_short_code

router = APIRouter(prefix="/links", tags=["links"])

_MAX_RETRIES = 5


@router.post(
    "",
    response_model=LinkResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_rate_limit)],
)
def create_link(payload: LinkCreate, db: Session = Depends(get_db)) -> Link:
    """Create a short link for the given target URL.

    Retries on the rare event of a short-code collision, relying on the
    database unique constraint as the source of truth.
    """
    for _ in range(_MAX_RETRIES):
        link = Link(
            short_code=generate_short_code(),
            target_url=str(payload.target_url),
        )
        db.add(link)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            continue
        db.refresh(link)
        return link

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not generate a unique short code. Please try again.",
    )
