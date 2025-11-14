from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard():
    """
    Главное меню Happ VPN Premium
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Приобрести подписку 💳", callback_data="menu:buy")],
            [
                InlineKeyboardButton(text="Мои ключи 🔑", callback_data="menu:keys"),
                InlineKeyboardButton(text="Поддержка 🚨 ", url="https://t.me/happ_support"),
            ],
            [InlineKeyboardButton(text="Инструкция установки 📲", callback_data="menu:inst")],
        ]
    )
    return keyboard
