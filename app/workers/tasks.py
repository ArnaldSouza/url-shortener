from contextlib import contextmanager
from collections.abc import Generator

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import ClickEvent, Link
from app.workers.celery_app import celery_app


@contextmanager
def _worker_session() -> Generator[Session, None, None]:
    """Provide a database session scoped to a single worker task.

    The Celery worker runs outside FastAPI, so it cannot use the request-scoped
    ``get_db`` dependency. It opens and closes its own session instead, rolling
    back on any error so a failed task never leaves a half-written transaction.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@celery_app.task(name="register_click")
def register_click(link_id: int, device_type: str = "unknown") -> None:
    """Record a click: insert a ClickEvent and bump the link's click_count.

    Both writes happen in one transaction, so the event log and the aggregate
    counter can never drift apart.
    """
    with _worker_session() as session:
        session.add(ClickEvent(link_id=link_id, device_type=device_type))
        session.execute(
            update(Link)
            .where(Link.id == link_id)
            .values(click_count=Link.click_count + 1)
        )
