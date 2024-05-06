from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Config(Base, TimestampMixin):
    __tablename__ = 'config'

    id: Mapped[int] = mapped_column(primary_key=True)
    admins_ids: Mapped[str]
    subadmins_ids: Mapped[Optional[str]] = mapped_column(default=None)

    __mapper_args__ = {'eager_defaults': True}

    def __repr__(self) -> str:
        return f"Config: #{self.admins_ids}"