from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile

from happ_vpn_final.happ_vpn_final.config import MEDIA
from happ_vpn_final.happ_vpn_final.keyboards.main_menu import get_main_menu_keyboard

import os

router = Router()

# --- Новый текст приветствия ---
WELCOME_TEXT = (
    "<b>Почему выбирают Happ VPN?</b>\n"
    "⚡ Высокая скорость соединения\n"
    "🔒 Надёжное шифрование данных\n"
    "💻 Доступ на всех устройствах:\n\n"
    "🖥 iMac\n"
    "📱 iPhone\n"
    "🤖 Android\n"
    "💻 MacBook\n"
    "📺 Телевизор\n"
    "👨🏻‍💻 Компьютер\n"
    "🚗 Автомобиль\n\n"
    "и многое другое…"
)


@router.message(F.text.in_({"/start", "Главное меню", "/cancel"}))
async def cmd_start(message: Message):
    """
    Стартовое меню бота (главный экран Happ VPN Premium)
    """
    img_path = MEDIA.get("main_image")
    caption = WELCOME_TEXT

    try:
        if img_path and os.path.exists(img_path):
            await message.answer_photo(
                photo=FSInputFile(img_path),
                caption=caption,
                reply_markup=get_main_menu_keyboard(),
            )
        else:
            await message.answer(
                text=caption,
                reply_markup=get_main_menu_keyboard(),
            )

    except Exception as e:
        await message.answer(f"Ошибка при запуске: {e}")


@router.callback_query(F.data == "menu:main")
async def show_main_menu(callback: CallbackQuery):
    """
    Обработчик кнопки «Главное меню»
    """
    img_path = MEDIA.get("main_image")
    caption = WELCOME_TEXT

    try:
        if getattr(callback.message, "video", None):
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=FSInputFile(img_path),
                caption=caption,
                reply_markup=get_main_menu_keyboard(),
            )
        else:
            if img_path and os.path.exists(img_path):
                await callback.message.edit_media(
                    InputMediaPhoto(
                        media=FSInputFile(img_path),
                        caption=caption,
                        parse_mode="HTML",
                    ),
                    reply_markup=get_main_menu_keyboard(),
                )
            else:
                await callback.message.edit_caption(
                    caption=caption,
                    reply_markup=get_main_menu_keyboard(),
                )

    except Exception as e:
        await callback.message.answer(f"Ошибка при обновлении меню: {e}")

    await callback.answer()
