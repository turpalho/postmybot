import logging
import re
from datetime import timedelta

from aiogram import F, Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold, hitalic

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.cron import CronTrigger

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.subadmin import SubAdminFilter
from tgbot.helpers.message_text import get_messages_text
from tgbot.helpers.utils import create_absolute_path
from tgbot.services.scheduler import send_message_interval
from tgbot.config import Config
from tgbot.misc.states import (AddPostState,
                               AddPostIntervalState,
                               TechSupporttState)
from tgbot.keyboards.admin import (get_back_keyboard,
                                   get_main_keyboard,
                                   get_my_channels_keyboard,
                                   get_selected_channel_keyboard,
                                   get_posts_keyboard,
                                   get_all_posts_keyboard,
                                   get_back_to_channel_keyboard)
from tgbot.handlers import admin_router

logger = logging.getLogger(__name__)

subadmin_router = Router()
subadmin_router.message.filter(SubAdminFilter())
subadmin_router.callback_query.filter(SubAdminFilter())
subadmin_router.include_router(admin_router)
subadmin_router.message.filter(F.chat.type == "private")
subadmin_router.callback_query.filter(F.message.chat.type == "private")


@subadmin_router.message(CommandStart())
@subadmin_router.callback_query(F.data == 'main_menu')
async def process_start_command(obj: Message | CallbackQuery,
                                config: Config,
                                state: FSMContext) -> None:
    await state.clear()

    if isinstance(obj, CallbackQuery):
        await obj.answer()
        await obj.message.edit_text(text=get_messages_text("MENU"),
                                    reply_markup=await get_main_keyboard())
    else:
        await obj.answer(text=get_messages_text("MENU"),
                         reply_markup=await get_main_keyboard())


@subadmin_router.callback_query(F.data == 'my_channels')
async def get_my_channels(call: CallbackQuery,
                          repo: RequestsRepo,
                          state: FSMContext) -> None:
    await call.answer()
    await state.clear()

    my_channels = []
    text_key = "NO_CHANNELS"
    channels = await repo.channels.get_all_channels(
                                        user_id=call.message.chat.id)
    if channels:
        text_key = "MY_CHANNELS"
        for channel in channels:
            my_channels.append({
                f"{channel.name}": f"{channel.channel_id}",
                })

    await call.message.edit_text(
        text=get_messages_text(text_key),
        reply_markup=await get_my_channels_keyboard(my_channels))


@subadmin_router.callback_query(F.data.startswith('channel_'))
async def get_selected_channel(call: CallbackQuery,
                               repo: RequestsRepo,
                               scheduler: AsyncIOScheduler,
                               state: FSMContext,
                               bot: Bot) -> None:
    call_data = call.data.split("_")
    channel_name = call_data[1]
    bot_is_on = call_data[2]
    channel_id = int(call_data[3])

    await state.set_data({
        "channel_id": channel_id,
        "channel": channel_name
    })

    if bot_is_on != "prof":
        channel = await repo.channels.get_channel_with_posts(channel_id)

        if len(channel.posts) <= 0:
            await call.answer(
                text="⚠️  Добавьте посты, чтобы включить бота на канале!",
                show_alert=True)
            return

        await call.answer()

        if bot_is_on == "on":

            await repo.channels.update_channel_job(channel_id=channel_id,
                                                   channel_job=1)

            total_seconds = channel.post_interval.total_seconds()
            days, hours = divmod(total_seconds, 24 * 3600)
            hours, remainder = divmod(hours, 3600)
            minutes, seconds = divmod(remainder, 60)

            job = scheduler.get_job(f'{channel_id}')
            if job:
                scheduler.remove_job(f'{channel_id}')
                logging.info(f"JOB REMOVED: {job}")

            trigger = CronTrigger(
                year="*",
                month="*",
                day=int(days) if days else "*",
                hour=int(hours) if hours else 0,
                minute=int(minutes) if minutes else 0,
                second=0
                )
            scheduler.add_job(send_message_interval,
                              trigger=trigger,
                              id=f'{channel_id}',
                              kwargs={
                                  "chat_id": channel_id,
                                  "bot": bot,
                                  "repo": repo,
                                  })
            logging.info("JOB ADDED")
        elif bot_is_on == "off":
            try:
                scheduler.remove_job(f'{channel_id}')
                logging.info("JOB REMOVED")
            except JobLookupError:
                logging.info(f"NO JOB BY THE ID OF {channel_id} WAS FOUND")

        await repo.channels.update_bot_status(channel_id, bot_is_on)
    else:
        await call.answer()
        bot_is_on = await repo.channels.get_bot_status(channel_id)

    await call.message.edit_text(
        text=get_messages_text("CHANNEL_INFO"),
        reply_markup=await get_selected_channel_keyboard(channel_name,
                                                         channel_id,
                                                         bot_is_on))


@subadmin_router.callback_query(F.data == 'posts')
async def get_my_posts(call: CallbackQuery,
                       repo: RequestsRepo,
                       state: FSMContext) -> None:
    await call.answer()
    state_data = await state.get_data()
    channel_id = state_data["channel_id"]
    channel = state_data["channel"]

    text = get_messages_text("NO_POSTS")
    await call.message.edit_text(text=text,
                                 reply_markup=await get_posts_keyboard(
                                     channel_id=channel_id,
                                     channel=channel))


@subadmin_router.callback_query(F.data == 'show_posts')
async def show_all_posts(call: CallbackQuery,
                       repo: RequestsRepo,
                       state: FSMContext) -> None:
    await call.answer()
    state_data = await state.get_data()
    channel_id = state_data["channel_id"]
    channel = state_data["channel"]

    text = get_messages_text("NO_POSTS")
    posts = await repo.posts.get_all_posts(user_id=call.message.chat.id)
    if posts:
        text = f"{get_messages_text('YOUR_POSTS')}\n"
        for post in posts:
            text += f"ID: {post.id}     Удалить пост: /delpost_{post.id}\n\n"
            await call.message.answer(
                text=f"ID: {post.id}\n\
                Удалить пост: /delpost_{post.id}\n\n{post.text}")

        await call.message.answer(
            text=text,
            reply_markup=await get_all_posts_keyboard(channel_id=channel_id,
                                                      channel=channel))
        return

    await call.message.edit_text(
        text=text,
        reply_markup=await get_all_posts_keyboard(channel_id=channel_id,
                                                  channel=channel))


@subadmin_router.callback_query(F.data == 'add_posts')
async def add_new_posts(call: CallbackQuery,
                        state: FSMContext) -> None:
    await call.answer()
    state_data = await state.get_data()
    channel_id = state_data["channel_id"]
    channel = state_data["channel"]

    await state.set_state(AddPostState.waiting_send_post)
    await call.message.edit_text(
        text=get_messages_text("ADD_POST"),
        reply_markup=await get_back_to_channel_keyboard(
            channel_id=channel_id,
            channel_name=channel))


@subadmin_router.message(AddPostState.waiting_send_post)
async def save_post(message: Message,
                    repo: RequestsRepo,
                    state: FSMContext,
                    bot: Bot) -> None:
    if not message.photo:
        await message.answer(text=get_messages_text("POST_ERROR"),
                             reply_markup=await get_back_keyboard())
        return
    state_data = await state.get_data()
    channel_id = state_data["channel_id"]
    channel = state_data["channel"]

    images_source_path = f"../../source/images/"
    absolute_path = create_absolute_path(file_path=images_source_path,
                                         file_name="image",
                                         file_format="jpg",
                                         add_time=True)
    post_text = message.caption
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, absolute_path)

    await repo.posts.add_post(text=post_text,
                              user_id=message.chat.id,
                              channel_id=channel_id,
                              image_urls=[absolute_path])
    await message.answer(
        text=get_messages_text("POST_ADDED"),
        reply_markup=await get_back_to_channel_keyboard(
            channel_id=channel_id,
            channel_name=channel))


@subadmin_router.message(F.text.startswith('/delpost_'))
async def delete_post(message: Message,
                      repo: RequestsRepo,
                      state: FSMContext) -> None:
    await state.clear()
    message_data = message.text.split("_")
    post_id = int(message_data[1])
    await repo.posts.delete_post(post_id=post_id)
    await message.answer(
        text=f"{get_messages_text('POST_DELETED')} {post_id}")


@subadmin_router.callback_query(F.data.startswith('scheduling_'))
async def get_scheduling(call: CallbackQuery,
                         repo: RequestsRepo,
                         state: FSMContext) -> None:
    await call.answer()
    call_data = call.data.split("_")
    channel_id = int(call_data[1])

    channel = await repo.channels.get_channel(channel_id=channel_id)

    total_seconds = channel.post_interval.total_seconds()
    days, hours = divmod(total_seconds, 24 * 3600)
    hours, remainder = divmod(hours, 3600)
    minutes, _ = divmod(remainder, 60)
    current_interval_text = get_messages_text('CHANNEL_CUR_INTERVAL')

    text = f"""{current_interval_text}
Через каждые {hbold(int(days))} дней
В {hbold(int(hours)
   if hours >= 10
   else f'0{int(hours)}')}:{
   hbold(int(minutes)
   if minutes >= 10
   else f'0{int(minutes)}')}\n
{hitalic(f'''Чтобы задать новый интервал, пришлите в таком формате:
    день часы:минуты
Пример:
    3 12:30
Получается, что через каждые 3 дня в 12:30 будет выкладываться пост.''')}"""

    await state.set_state(
        AddPostIntervalState.waiting_send_interval_timedelta)
    await call.message.edit_text(
        text=text,
        reply_markup=await get_back_to_channel_keyboard(
            channel_id=channel_id,
            channel_name=channel.name))


@subadmin_router.message(AddPostIntervalState.waiting_send_interval_timedelta)
async def save_post(message: Message,
                    repo: RequestsRepo,
                    bot: Bot,
                    scheduler: AsyncIOScheduler,
                    state: FSMContext) -> None:
    state_data = await state.get_data()
    channel_id = int(state_data["channel_id"])
    channel = state_data["channel"]

    pattern = re.compile(r"^\d{1}\s\d{2}:\d{2}$")
    if not pattern.match(message.text):
        await message.answer(
            text=get_messages_text("INTERVAL_ADD_ERROR"),
            reply_markup=await get_back_to_channel_keyboard(
                channel_id=channel_id,
                channel_name=channel))
        return

    message_data = message.text.split()
    days = float(message_data[0])
    hours = float(message_data[1].split(":")[0])
    minutes = float(message_data[1].split(":")[1])
    interval_timedelta = timedelta(days=days, hours=hours, minutes=minutes)

    await repo.channels.update_channel_post_interval(
        channel_id=channel_id,
        interval_timedelta=interval_timedelta)

    job = scheduler.get_job(f'{channel_id}')
    if job:
        scheduler.remove_job(f'{channel_id}')
        logging.info(f"JOB REMOVED: {job}")

    trigger = CronTrigger(
        year="*",
        month="*",
        day=int(days) if days else "*",
        hour=int(hours) if hours else 0,
        minute=int(minutes) if minutes else 0,
        second=0
        )
    scheduler.add_job(send_message_interval,
                    trigger=trigger,
                    id=f'{channel_id}',
                    kwargs={
                        "chat_id": channel_id,
                        "bot": bot,
                        "repo": repo,
                        })
    logging.info("JOB ADDED")

    await message.answer(
        text=get_messages_text("INTERVAL_ADDED"),
        reply_markup=await get_back_to_channel_keyboard(
            channel_id=channel_id,
            channel_name=channel))


@subadmin_router.callback_query(F.data == 'tech_support')
async def get_tech_support(call: CallbackQuery,
                           state: FSMContext) -> None:
    await call.answer()
    await state.clear()
    await state.set_state(TechSupporttState.waiting_send_techsup)
    await call.message.edit_text(text=get_messages_text("TECH_SUPPORT"),
                                 reply_markup=await get_back_keyboard())


@subadmin_router.message(TechSupporttState.waiting_send_techsup)
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


@subadmin_router.callback_query(F.data == 'getid')
async def get_my_id(call: CallbackQuery,
                          state: FSMContext) -> None:
    await call.answer()
    await state.clear()

    await call.message.answer(text=f"<code>{call.message.chat.id}</code>")
    await call.message.answer(
        text=get_messages_text("BACK_MENU"),
        reply_markup=await get_back_keyboard())
