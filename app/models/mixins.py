from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


def _now_with_tz_info() -> datetime:
    return datetime.now(tz=timezone.utc)


class IntegerIdMixin(object):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class UUIDIdMixin(object):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


class TimeStampedMixin(object):
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=_now_with_tz_info,
    )
