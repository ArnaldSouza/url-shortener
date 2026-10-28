from app.workers.celery_app import celery_app


@celery_app.task
def ping() -> str:
    """A trivial task used to verify the Celery/Redis pipeline works."""
    return "pong"
