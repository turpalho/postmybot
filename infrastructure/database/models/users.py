from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .channels import Channel
    from .posts import Post


class User(Base, TimestampMixin):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger,
                                         primary_key=True,
                                         index=True)
    username: Mapped[Optional[str]]
    tg_first_name: Mapped[Optional[str]]
    tg_last_name: Mapped[Optional[str]]
    tg_username: Mapped[Optional[str]]

    channels: Mapped[list["Channel"]] = relationship(back_populates="user")
    posts: Mapped[list["Post"]] = relationship(back_populates="user")

    __mapper_args__ = {'eager_defaults': True}

    def __repr__(self) -> str:
        return f"User: #{self.user_id}"
