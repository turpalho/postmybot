import logging

from aiogram import Router, F, Bot
from aiogram.types import Message, ChatMemberUpdated, CallbackQuery
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION
)

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.config import Config

logger = logging.getLogger(__name__)

chat_router = Router()
chat_router.message.filter(
    F.chat.type.in_(["group", "supergroup", "channel"]))
chat_router.my_chat_member.filter(
    F.chat.type.in_(["group", "supergroup", "channel"]))


@chat_router.message(F.text == "/id")
async def ask_id(message: Message) -> None:
    await message.answer(f"<code>{str(message.chat.id)}</code>")


@chat_router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=JOIN_TRANSITION
    )
)
async def join_to_chat(event: ChatMemberUpdated,
                       config: Config,
                       repo: RequestsRepo,
                       bot: Bot):
    if not event.from_user.id in config.tg_bot.admin_ids:
        await bot.leave_chat(event.chat.id)

    await repo.channels.get_or_create_channel(channel_id=event.chat.id,
                                              user_id=event.from_user.id,
                                              name=event.chat.username,
                                              url=f"t.me/{event.chat.username}",
                                              description=event.chat.description)
    await bot.send_message(chat_id=event.from_user.id,
                           text=f"Бот добавлен в группу с ID {event.chat.id}.")
    return