import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from happ_vpn_final.happ_vpn_final.config import MEDIA, INSTALLATION_TEXTS
from happ_vpn_final.happ_vpn_final.keyboards.instructions_menu import (
    get_instructions_keyboard,
    get_instruction_back_keyboard,
)
from happ_vpn_final.happ_vpn_final.keyboards.main_menu import get_main_menu_keyboard

router = Router()

VIDEO_FILE_IDS = {
    "iphone": "BAACAgIAAxkDAANZaRL5oTTe-tepRuTFM11FVHo7Xe8AApZ8AAJGcZlI2q_ekYJ6Um42BA",
    "android": "BAACAgIAAxkDAANaaRL6A3V-TeK9ck-UlFpGg_TTB7sAAp18AAJGcZlInvk5R_KUPPM2BA",
    "pc": "BAACAgIAAxkDAANbaRL6PA0IP4X89dZ2RKyupY3CjcgAAqF8AAJGcZlIfceY9_zW4VU2BA",
    "tv": "BAACAgIAAxkDAANcaRL6iFyjFH5zyZo5STGVXVYOJB0AAqV8AAJGcZlIvFrtA0D0IJI2BA",
}


@router.callback_query(F.data == "menu:inst")
async def show_instructions_menu(callback: CallbackQuery):
    """Открывает выбор устройства. Предыдущее сообщение удаляется."""
    await callback.message.delete()
    await callback.message.answer_photo(
        photo=FSInputFile(MEDIA.get("instruction_image")),
        caption="📚 Выберите устройство, для которого нужна инструкция:",
        reply_markup=get_instructions_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("inst:"))
async def show_instruction(callback: CallbackQuery):
    """Отправляет инструкцию и делает её одноразовой."""
    device = callback.data.split(":")[1]
    caption = INSTALLATION_TEXTS.get(device, "Инструкция недоступна.")

    await callback.message.delete()
    await callback.message.answer_video(
        video=VIDEO_FILE_IDS.get(device),
        caption=caption,
        parse_mode="HTML",
        reply_markup=get_instruction_back_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:main")
async def back_to_main_from_instruction(callback: CallbackQuery):
    """Удаляет инструкцию и возвращает главное меню."""
    from happ_vpn_final.happ_vpn_final.handlers.start import WELCOME_TEXT
    await callback.message.delete()
    await callback.message.answer(
        text=WELCOME_TEXT,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()
