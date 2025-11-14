from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_tariffs_keyboard():
    """
    Меню выбора тарифа
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1 - Месяц", callback_data="tariff:1m"),
                InlineKeyboardButton(text="3 - Месяца", callback_data="tariff:3m"),
            ],
            [
                InlineKeyboardButton(text="6 - Месяцев", callback_data="tariff:6m"),
                InlineKeyboardButton(text="12 - Месяцев", callback_data="tariff:12m"),
            ],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu:main")],
        ]
    )
    return keyboard


def get_back_to_tariffs_keyboard():
    """
    Кнопка «Назад к тарифам» для раздела Мои ключи.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад к тарифам", callback_data="back:tariffs")]
        ]
    )