from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, String


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 Base declarative class."""
    pass


class TimestampMixin:
    """Provides created_at and updated_at tracking for all entities."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


def generate_uuid() -> str:
    """Generates a UUID4 string representation."""
    return str(uuid.uuid4())
