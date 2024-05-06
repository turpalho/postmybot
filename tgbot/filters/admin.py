import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from tgbot.config import Config


class AdminFilter(BaseFilter):

    def __init__(self, is_admin: bool = True) -> None:
        self.is_admin = is_admin

    async def __call__(self, obj: Message, config: Config) -> bool:
        # if isinstance(obj, CallbackQuery):
        #     return (obj.message.chat.id in config.tg_bot.admin_ids) == self.is_admin
        # else:
        return (obj.chat.id in config.tg_bot.admin_ids) == self.is_admin
