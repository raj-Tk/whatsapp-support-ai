import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CategoryThreshold(Base):
    __tablename__ = "category_thresholds"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    category: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, default=0.70, nullable=False)
    automation_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
