from typing import Dict, List

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


async def get_main_keyboard(is_admin: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text="💬  Мои каналы",
                                    callback_data="my_channels")]

    if not is_admin:
        buttons.append(InlineKeyboardButton(text="📞  Обратная связь",
                                            callback_data="tech_support"))

    buttons.append(InlineKeyboardButton(text="🔠  Узнать ID",
                                        callback_data="getid"))
    kb.add(*buttons)
    kb.adjust(1)
    return kb.as_markup()


async def get_my_channels_keyboard(
        channels: List[Dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    buttons = []
    for channel in channels:
        for key, value in channel.items():
            buttons.append(InlineKeyboardButton(
                text=f"📢  {key}",
                callback_data=f"channel_*_{key}_*_prof_*_{value}"))

    buttons.append(InlineKeyboardButton(text="🔙  Назад",
                                        callback_data="main_menu"))
    kb.add(*buttons)
    kb.adjust(1)
    return kb.as_markup()


async def get_selected_channel_keyboard(
        channel: str,
        channel_id: int,
        bot_is_on: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if bot_is_on == "on":
        bot_is_on = "off"
        on_bot_emodji = "✅"
    else:
        bot_is_on = "on"
        on_bot_emodji = "☑️"

    kb.add(*[
        InlineKeyboardButton(
            text=f"{on_bot_emodji}  Включить бота",
            callback_data=f"channel_*_{channel}_*_{bot_is_on}_*_{channel_id}"),
        InlineKeyboardButton(
            text="📰  Посты для канала",
            callback_data="posts"),
        InlineKeyboardButton(
            text="⏰  Режим работы",
            callback_data=f"scheduling_{channel_id}"),
        InlineKeyboardButton(
            text="🔙  Назад",
            callback_data="my_channels")
    ])
    kb.adjust(1)
    return kb.as_markup()


async def get_posts_keyboard(channel_id: int,
                             channel: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(*[
        InlineKeyboardButton(
            text="📜  Показать все посты",
            callback_data="show_posts"),
        InlineKeyboardButton(
            text="📝  Добавить посты",
            callback_data="add_posts"),
        InlineKeyboardButton(
            text="🔙  Назад",
            callback_data=f"channel_*_{channel}_*_prof_*_{channel_id}")
    ])
    kb.adjust(1)
    return kb.as_markup()


async def get_all_posts_keyboard(channel_id: int,
                                 channel: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(*[
        InlineKeyboardButton(
            text="📝  Добавить посты",
            callback_data="add_posts"),
        InlineKeyboardButton(
            text="🔙  Назад",
            callback_data=f"channel_*_{channel}_*_prof_*_{channel_id}")
    ])
    kb.adjust(1)
    return kb.as_markup()


async def get_back_to_channel_keyboard(
        channel_id: int,
        channel_name: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(*[
        InlineKeyboardButton(
            text="🔙  Назад",
            callback_data=f"channel_*_{channel_name}_*_prof_*_{channel_id}")
    ])
    kb.adjust(1)
    return kb.as_markup()


async def get_back_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(*[
        InlineKeyboardButton(text="🔙  Назад", callback_data="main_menu")
    ])
    kb.adjust(1)
    return kb.as_markup()