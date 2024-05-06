import logging
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from tgbot.config import Config


class SubAdminFilter(BaseFilter):

    def __init__(self, is_subadmin: bool = True) -> None:
        self.is_subadmin = is_subadmin

    async def __call__(self, obj: Message | CallbackQuery, config: Config) -> bool:
        if isinstance(obj, CallbackQuery):
            return config.tg_bot.subadmins_ids and (obj.message.chat.id in config.tg_bot.subadmins_ids) == self.is_subadmin
        else:
            return config.tg_bot.subadmins_ids and (obj.chat.id in config.tg_bot.subadmins_ids) == self.is_subadmin
