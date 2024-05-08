from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


async def get_main_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(*[
        InlineKeyboardButton(text="❔  Инструкция",
                             callback_data="help"),
        InlineKeyboardButton(text="📞  Обратная связь",
                             callback_data="tech_support"),
        InlineKeyboardButton(text="🔠  Узнать ID",
                             callback_data="getid")
    ])
    kb.adjust(1)
    return kb.as_markup()


async def get_support_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(*[
        InlineKeyboardButton(text="📞  Написать в техподдержку",
                             callback_data="tech_support"),
        InlineKeyboardButton(text="🔙  Назад",
                             callback_data="main_menu")
    ])
    kb.adjust(1)
    return kb.as_markup()


async def get_back_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(*[
        InlineKeyboardButton(text="🔙  Назад",
                             callback_data="main_menu")
    ])
    kb.adjust(1)
    return kb.as_markup()