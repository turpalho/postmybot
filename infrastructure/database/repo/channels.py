from typing import Optional
from datetime import timedelta

from sqlalchemy import select, update, ScalarResult
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models import Channel, Post
from infrastructure.database.repo.base import BaseRepo


class ChannelRepo(BaseRepo):
    model = Channel

    async def get_or_create_channel(
        self,
        channel_id: int,
        user_id: int,
        name: str = None,
        url: str = None,
        description: str = None,
        bot_is_on: str | None = "off",
    ):
        """
        Creates or updates a new channel in the database and returns the channel object.

        Args:
            channel_id (int): The unique identifier of the channel_id.
            user_id (int): The unique identifier of the user who added the bot to the channel
            name (str): The name of the channel.
            url (str): The telegram url of the channel.
            description (str): The description of the channel.

        Returns:
            Channel: The Channel object.
        """
        channel_values = {
            "channel_id": channel_id,
            "user_id": user_id,
            "name": name,
            "url": url,
            "description": description,
            "bot_is_on": bot_is_on
        }

        insert_stmt = (
            insert(self.model)
            .values(**channel_values)
            .on_conflict_do_update(
                index_elements=[Channel.channel_id],
                set_=dict(
                    name=name,
                ),
            )
            .returning(Channel)
        )

        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_all_channels(self,
                               user_id: int) -> ScalarResult[Channel]:
        stmt = select(Channel).where(
            Channel.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_channel(self, channel_id: int) -> Channel | None:
        stmt = select(Channel).where(Channel.channel_id == channel_id)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_channel_with_posts(self, channel_id: int) -> Channel | None:
        stmt = select(Channel)\
            .where(Channel.channel_id == channel_id)\
            .options(selectinload(Channel.posts)\
            .options(selectinload(Post.images)))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_bot_status(self,
                             channel_id: int) -> Channel.bot_is_on:
        stmt = select(Channel.bot_is_on).where(
            Channel.channel_id == channel_id)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def update_bot_status(self,
                                channel_id: int,
                                bot_is_on: str) -> None:
        stmt = update(Channel).where(
            Channel.channel_id == channel_id).values(bot_is_on=bot_is_on)
        await self.session.execute(stmt)
        await self.session.commit()
        return

    async def update_channel_job(self,
                                channel_id: int,
                                channel_job: int) -> None:
        stmt = update(Channel).where(
            Channel.channel_id == channel_id).values(channel_job=channel_job)
        await self.session.execute(stmt)
        await self.session.commit()
        return

    async def update_channel_post_interval(self,
                                           channel_id: int,
                                           interval_timedelta: timedelta) -> None:
        stmt = update(Channel).where(
            Channel.channel_id == channel_id).values(post_interval=interval_timedelta)
        await self.session.execute(stmt)
        await self.session.commit()
        return