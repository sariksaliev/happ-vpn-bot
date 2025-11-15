from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_instructions_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📱 iPhone", callback_data="inst:iphone"),
                InlineKeyboardButton(text="🤖 Android", callback_data="inst:android"),
            ],
            [
                InlineKeyboardButton(text="💻 Компьютер", callback_data="inst:pc"),
                InlineKeyboardButton(text="📺 Телевизор", callback_data="inst:tv"),
            ],
            [InlineKeyboardButton(text="⬅️ Главное меню", callback_data="menu:main")],
        ]
    )


def get_instruction_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к выбору устройства",
                    callback_data="menu:inst",
                )
            ],
            [InlineKeyboardButton(text="⬅️ Главное меню", callback_data="menu:main")],
        ]
    )
