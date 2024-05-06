import logging

from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.service_layer.users import get_or_create_user
from tgbot.helpers.message_text import get_messages_text
from tgbot.config import Config
from tgbot.filters.user import AddAdminFilter
from tgbot.misc.states import TechSupporttState
from tgbot.keyboards.user import (get_main_keyboard,
                                  get_back_keyboard,
                                  get_support_keyboard)

logger = logging.getLogger(__name__)

user_router = Router()
user_router.message.filter(F.chat.type == "private")
user_router.callback_query.filter(F.message.chat.type == "private")


@user_router.message(AddAdminFilter())
async def add_admin(message: Message,
                    config: Config,
                    repo: RequestsRepo,
                    state: FSMContext) -> None:
    await state.clear()

    if not message.from_user.id in config.tg_bot.admin_ids:
        config.tg_bot.admin_ids.append(message.from_user.id)

        if not config.tg_bot.subadmins_ids:
            config.tg_bot.subadmins_ids = []

        config.tg_bot.subadmins_ids.append(message.from_user.id)
        await repo.configs.update_admin_ids(config.tg_bot.admin_ids)
        await repo.configs.update_subadmin_ids(config.tg_bot.subadmins_ids)
        await message.answer(text=get_messages_text("ADD_ADMIN"))
    else:
        await message.answer(text=get_messages_text("EXISTED_ADMIN"))


@user_router.message(CommandStart())
@user_router.callback_query(F.data == 'main_menu')
async def process_start_command(obj: Message | CallbackQuery,
                                repo: RequestsRepo,
                                state: FSMContext) -> None:
    """
    Process the /start command

    Args:
        message: Message
        dialog_manager: DialogManager
        repo: RequestsRepo

    Steps:
        1. Check if the user is already registered in the database
        2. If the user is not registered, start the registration process
        3. If the user is registered, start the dialog manager with the start window
    """
    # 1. Check if the user is already registered in the database
    await state.clear()

    if isinstance(obj, CallbackQuery):
        await obj.message.edit_text(text=get_messages_text("MENU"),
                                    reply_markup=await get_main_keyboard())
    else:
        user, is_new = await get_or_create_user(
            obj.from_user.id,
            obj.from_user.username or str(obj.from_user.id),
            tg_first_name=obj.from_user.first_name,
            tg_last_name=obj.from_user.last_name,
            tg_username=obj.from_user.username,
            repository=repo,
        )

        if is_new:
            await obj.answer(text=get_messages_text("FIRST"),
                             reply_markup=await get_main_keyboard())
            return

        await obj.answer(text=get_messages_text("MENU"),
                         reply_markup=await get_main_keyboard())



@user_router.message(Command(commands=['help']))
@user_router.callback_query(F.data == 'help')
async def get_support(obj: Message | CallbackQuery,
                      state: FSMContext) -> None:
    await state.clear()
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        await obj.message.edit_text(text=get_messages_text("USER_HELP"),
                                    reply_markup=await get_support_keyboard())
    else:
        await obj.answer(text=get_messages_text("USER_HELP"),
                         reply_markup=await get_support_keyboard())


@user_router.callback_query(F.data == 'tech_support')
async def get_tech_support(call: CallbackQuery,
                           state: FSMContext) -> None:
    await call.answer()
    await state.clear()
    await state.set_state(TechSupporttState.waiting_send_techsup)
    await call.message.edit_text(text=get_messages_text("TECH_SUPPORT"),
                                 reply_markup=await get_back_keyboard())


@user_router.message(TechSupporttState.waiting_send_techsup)
async def sent_support_request(message: Message,
                               state: FSMContext,
                               config: Config,
                               bot: Bot) -> None:
    await state.clear()

    for admin_id in config.tg_bot.admin_ids:
        try:
            await bot.send_message(chat_id=admin_id,
                                   text=f'{message.chat.id}_{message.text}')
        except:
            logging.info(f'ЧАТ НЕ НАЙДЕН {admin_id}')

    await message.answer(text=get_messages_text('SUPPORT_REQUES_SENT'),
                         reply_markup=await get_back_keyboard())


@user_router.callback_query(F.data == 'getid')
async def get_my_id(call: CallbackQuery,
                          state: FSMContext) -> None:
    await call.answer()
    await state.clear()

    await call.message.answer(text=f"<code>{call.message.chat.id}</code>")
    await call.message.answer(
        text=get_messages_text("BACK_MENU"),
        reply_markup=await get_back_keyboard())
