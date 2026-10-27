from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class LinkCreate(BaseModel):
    """Payload for creating a short link."""

    target_url: HttpUrl


class LinkResponse(BaseModel):
    """Public representation of a short link."""

    model_config = ConfigDict(from_attributes=True)

    short_code: str
    target_url: str
    click_count: int
    created_at: datetime
