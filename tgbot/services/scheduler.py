import logging
from typing import Union

from aiogram import Bot
from aiogram.types import FSInputFile

from infrastructure.database.repo.requests import RequestsRepo


async def send_message_interval(
    chat_id: Union[int, str],
    bot: Bot,
    repo: RequestsRepo,
) -> bool:
    channel = await repo.channels.get_channel_with_posts(chat_id)
    channel_job = channel.channel_job

    if channel_job == len(channel.posts):
        channel_job = 1
        await repo.channels.update_channel_job(channel_id=chat_id, channel_job=channel_job)

    post = channel.posts[channel_job - 1]
    if post.images:
        await bot.send_photo(chat_id=chat_id, photo=post.images[0].image_id, caption=post.text)
    else:
        await bot.send_message(chat_id=chat_id, text=post.text)
    await repo.channels.update_channel_job(channel_id=chat_id, channel_job=channel_job + 1)
