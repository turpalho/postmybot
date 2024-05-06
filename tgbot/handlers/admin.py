import logging
import re

from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.admin import AdminFilter
from tgbot.config import Config
from tgbot.helpers.message_text import get_messages_text

logger = logging.getLogger(__name__)

admin_router = Router()
admin_router.message.filter(AdminFilter())
admin_router.callback_query.filter(AdminFilter())
admin_router.message.filter(F.chat.type == "private")
admin_router.callback_query.filter(F.message.chat.type == "private")


@admin_router.message(Command(commands=["del_admin"]))
async def delete_admin(message: Message,
                       # repo: RequestsRepo,
                       config: Config) -> None:
    config.tg_bot.admin_ids.remove(message.from_user.id)
    config.tg_bot.subadmins_ids.remove(message.from_user.id)
    # await repo.update_admin_ids(config.tg_bot.admin_ids)

    text = "Администратор удален"
    await message.answer(text)


@admin_router.message(Command(commands=['add_subadmin']))
async def add_subadmin(message: Message,
                       config: Config,
                       repo: RequestsRepo,
                       state: FSMContext,
                       command: CommandObject) -> None:
    await state.clear()
    arguments = command.args
    pattern = re.compile(r"^[-\d][\d]+$")

    if not arguments or not pattern.match(arguments):
        await message.answer(text=get_messages_text("ERROR_ADD_SUBADMIN"))
        return

    sub_admin_id = int(arguments)

    if not config.tg_bot.subadmins_ids:
        config.tg_bot.subadmins_ids = []

    if not sub_admin_id in config.tg_bot.subadmins_ids:
        config.tg_bot.subadmins_ids.append(sub_admin_id)
        await repo.configs.update_subadmin_ids(config.tg_bot.subadmins_ids)
        await message.answer(text=get_messages_text("ADD_SUBADMIN"))
        return

    await message.answer(text=get_messages_text("EXISTED_SUBADMIN"))
    return


@admin_router.message(Command(commands=['help']))
async def get_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text=get_messages_text("ADMIN_HELP"))


@admin_router.message()
async def get_all_messages(message: Message, bot: Bot):
    if message.reply_to_message:
        reply_message_text = message.reply_to_message.text
        user_id = int(reply_message_text.split('_')[0])
        user_id_message = reply_message_text.split('_')[1]
        text = f'''Админ ответил на Ваше следующее сообщение:
{user_id_message}

Ответ Админа:
{message.text}

❕  Чтобы написать админу, перейдите в раздел "Обратная связь"!'''
        await bot.send_message(user_id, text)
