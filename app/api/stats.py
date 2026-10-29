from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.stats import get_most_clicked

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/most-clicked")
def most_clicked(db: Session = Depends(get_db)) -> dict:
    """Return the most-clicked link (cached in Redis for a short interval)."""
    result = get_most_clicked(db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No links found."
        )
    return result
