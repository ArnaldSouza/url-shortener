from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ClickEvent(Base):
    """A single click on a short link, stored for analytics.

    Deliberately privacy-preserving: no IP address and no raw user agent are
    stored. Only a coarse device category is kept, which cannot identify a user.
    """

    __tablename__ = "click_events"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
    )
    link_id: Mapped[int] = mapped_column(
        ForeignKey("links.id", ondelete="CASCADE"), index=True
    )
    device_type: Mapped[str] = mapped_column(String(16), server_default="unknown")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
