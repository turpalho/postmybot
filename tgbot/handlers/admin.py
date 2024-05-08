import logging
import re

from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold, hitalic

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.keyboards.admin import get_back_keyboard
from tgbot.filters.admin import AdminFilter, AdminReply
from tgbot.config import Config
from tgbot.helpers.message_text import get_messages_text

logger = logging.getLogger(__name__)

admin_router = Router()
admin_router.message.filter(AdminFilter())
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


@admin_router.message(Command(commands=["subadmins"]))
async def get_all_subadmins(message: Message,
                            config: Config) -> None:
    subadmins = config.tg_bot.subadmins_ids
    text = "Суб-администраторы:\n"
    for subadmin in subadmins:
        text += f"{subadmin}\n"
    await message.answer(text)


@admin_router.message(Command(commands=['add_subadmin']))
async def add_subadmin(message: Message,
                       config: Config,
                       repo: RequestsRepo,
                       bot: Bot,
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
        await bot.send_message(sub_admin_id,
                               get_messages_text("YOU_SUBADMIN"),
                               reply_markup=await get_back_keyboard())
        return

    await message.answer(text=get_messages_text("EXISTED_SUBADMIN"))
    return


@admin_router.message(Command(commands=["del_subadmin"]))
async def delete_admin(message: Message,
                       config: Config,
                       repo: RequestsRepo,
                       bot: Bot,
                       state: FSMContext,
                       command: CommandObject) -> None:
    await state.clear()
    arguments = command.args
    pattern = re.compile(r"^[-\d][\d]+$")

    if not arguments or not pattern.match(arguments):
        await message.answer(text=get_messages_text("ERROR_REMOVE_SUBADMIN"))
        return

    sub_admin_id = int(arguments)

    if not sub_admin_id in config.tg_bot.subadmins_ids:
        await message.answer(
            f"⚠️  Суб-администратора с таким ID: {sub_admin_id} не существует!")
        return

    config.tg_bot.subadmins_ids.remove(sub_admin_id)
    await repo.configs.update_subadmin_ids(config.tg_bot.subadmins_ids)
    await message.answer(
        f"✅  Суб-администратор с ID: {sub_admin_id} удален!")


@admin_router.message(Command(commands=['help']))
async def get_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text=get_messages_text("ADMIN_HELP"))


@admin_router.message(F.text, AdminReply())
async def get_reply_messages(message: Message, bot: Bot):
    try:
        reply_message_text = message.reply_to_message.text
        matches = re.match(r'^New issue: #id([-\d]\d+)', reply_message_text)

        if matches:
            numbers = matches.group(1)
            user_message = reply_message_text[len(matches.group(0)):].strip()[13:].strip()
            user_id = int(numbers)

        text = f'''Админ ответил на Ваше следующее сообщение:
    {hitalic(user_message)}

Ответ Админа:
    {hitalic(message.text)}


❕  Чтобы написать админу, перейдите в раздел "Обратная связь"!'''

        await bot.send_message(user_id, text)
    except:
        await bot.send_message(message.chat.id,
                               "❌  Возникла ошибка при отправке сообщения!")