from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .users import User
    from .images import Image
    from .channels import Channel


class Post(Base, TimestampMixin):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(BigInteger,
                                    primary_key=True,
                                    index=True)
    text: Mapped[Optional[str]]
    user_id: Mapped[int] = mapped_column(BigInteger,
                                         ForeignKey("users.user_id",
                                                    ondelete='CASCADE'),
                                         nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger,
                                            ForeignKey("channels.channel_id",
                                                       ondelete='CASCADE'),
                                            nullable=False)

    user: Mapped["User"] = relationship(back_populates="posts")
    channel: Mapped["Channel"] = relationship(back_populates="posts")
    images: Mapped[list["Image"]] = relationship(back_populates="post")

    __mapper_args__ = {'eager_defaults': True}

    def __repr__(self) -> str:
        return f"Post: #{self.id}"
