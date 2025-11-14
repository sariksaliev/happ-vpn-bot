from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from happ_vpn_final.happ_vpn_final.database.db_postgres import get_user_keys
from happ_vpn_final.happ_vpn_final.keyboards.instructions_menu import get_instruction_back_keyboard

router = Router()


def copy_button(url: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Копировать", callback_data=f"copy:{url}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu:main")]
        ]
    )


@router.callback_query(F.data == "menu:keys")
async def show_user_keys(callback: CallbackQuery):
    user_id = callback.from_user.id
    keys = get_user_keys(user_id)

    if not keys:
        await callback.message.answer(
            "🔑 У вас пока нет активных ключей.",
            reply_markup=get_instruction_back_keyboard()
        )
        return await callback.answer()

    # удаляем старое сообщение
    try:
        await callback.message.delete()
    except:
        pass

    # отправляем каждый ключ отдельным сообщением
    for key_value, tariff_code, date_end in keys:

        text = (
            f"<b>Тариф:</b> {tariff_code}\n"
            f"<b>Действует до:</b> {date_end.strftime('%d.%m.%Y')}\n\n"
            f"<code>{key_value}</code>"
        )

        await callback.message.answer(
            text,
            reply_markup=copy_button(key_value),
            parse_mode="HTML"
        )

    await callback.answer()


# обработчик кнопки "копировать"
@router.callback_query(F.data.startswith("copy:"))
async def copy_key(callback: CallbackQuery):
    key = callback.data.split("copy:")[1]
    await callback.answer("Скопировано ✔️", show_alert=True)
