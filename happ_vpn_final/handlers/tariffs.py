import os
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from happ_vpn_final.happ_vpn_final.keyboards.tariffs_menu import get_tariffs_keyboard
from happ_vpn_final.happ_vpn_final.database.db_postgres import (
    add_subscription,
    get_user_by_id,
    add_user,
)
from happ_vpn_final.happ_vpn_final.services.vpn_keys import seed_keys_if_empty, get_free_key
from happ_vpn_final.happ_vpn_final.services.yookassa_api import create_payment, get_payment_status
from happ_vpn_final.happ_vpn_final.config import MEDIA_DIR, MEDIA, ADMIN_CHAT_ID

router = Router()

# --- Тарифы ---
TARIFFS = {
    "1m": {"title": "1 месяц", "months": 1, "price": 189, "image": "1 месяц тариф.jpg"},
    "3m": {"title": "3 месяца", "months": 3, "price": 449, "image": "3 месяца тариф.jpg"},
    "6m": {"title": "6 месяцев", "months": 6, "price": 699, "image": "6 месяца тариф.jpg"},
    "12m": {"title": "12 месяцев", "months": 12, "price": 1499, "image": "12 месяца тариф.jpg"},
}


@router.callback_query(F.data == "menu:buy")
async def menu_buy(callback: CallbackQuery):
    img_path = MEDIA.get("tariffs_image")
    caption = "Выберите нужный тариф 👇"

    try:
        if img_path and os.path.exists(img_path):
            await callback.message.edit_media(
                InputMediaPhoto(media=FSInputFile(img_path), caption=caption),
                reply_markup=get_tariffs_keyboard(),
            )
        else:
            await callback.message.edit_caption(caption=caption, reply_markup=get_tariffs_keyboard())
    except Exception:
        await callback.message.answer("Ошибка при загрузке тарифов.")
    await callback.answer()


@router.callback_query(F.data.startswith("tariff:"))
async def show_tariff_details(callback: CallbackQuery):
    tariff_code = callback.data.split(":", 1)[1]
    tariff = TARIFFS.get(tariff_code)
    if not tariff:
        return await callback.answer("Неизвестный тариф.", show_alert=True)

    img_path = os.path.join(MEDIA_DIR, tariff["image"])
    caption = (
        f"<b>{tariff['title']}</b>\n"
        f"До 10 устройств.\n"
        f"Стоимость: <b>{tariff['price']}₽</b>."
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Приобрести", callback_data=f"buy:{tariff_code}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back:tariffs")]
    ])

    if os.path.exists(img_path):
        await callback.message.edit_media(InputMediaPhoto(media=FSInputFile(img_path), caption=caption), reply_markup=keyboard)
    else:
        await callback.message.edit_caption(caption=caption, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "back:tariffs")
async def back_to_tariffs(callback: CallbackQuery):
    await menu_buy(callback)


# ------------------  ОПЛАТА ЧЕРЕЗ ЮКАССА -------------------

@router.callback_query(F.data.startswith("buy:"))
async def start_payment(callback: CallbackQuery):
    tariff_code = callback.data.split(":", 1)[1]
    tariff = TARIFFS.get(tariff_code)
    if not tariff:
        return await callback.answer("Неизвестный тариф.", show_alert=True)

    amount = tariff["price"]
    description = f"Оплата тарифа {tariff['title']} Happ VPN"
    return_url = "https://t.me/Happ_ibot"  # после оплаты — в основной бот

    try:
        payment = create_payment(amount, description, return_url)
    except Exception as e:
        print(f"Ошибка ЮKassa: {e}")
        return await callback.answer("Ошибка при создании оплаты. Проверьте настройки ЮKassa.", show_alert=True)

    caption = (
        f"<b>{tariff['title']}</b>\n\n"
        f"💳 Стоимость: <b>{amount}₽</b>\n\n"
        "1️⃣ Нажмите кнопку ниже для оплаты.\n"
        "2️⃣ После успешной оплаты — вернитесь в бот, ключ появится автоматически."
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💳 Оплатить {amount}₽", url=payment['url'])],
        [InlineKeyboardButton(text="✅ Проверить оплату", callback_data=f"check:{payment['id']}:{tariff_code}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back:tariffs")]
    ])

    await callback.message.edit_caption(caption=caption, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("check:"))
async def check_payment_status(callback: CallbackQuery):
    _, payment_id, tariff_code = callback.data.split(":")
    status = get_payment_status(payment_id)

    if status == "succeeded":
        await confirm_payment(callback, tariff_code)
    elif status in ("pending", "waiting_for_capture"):
        await callback.answer("Платёж ещё не подтверждён. Попробуйте позже.", show_alert=True)
    else:
        await callback.answer("Платёж не прошёл или был отменён.", show_alert=True)


# ------------------  ВЫДАЧА КЛЮЧА -------------------

async def confirm_payment(callback: CallbackQuery, tariff_code: str):
    tariff = TARIFFS.get(tariff_code)
    if not tariff:
        return await callback.answer("Неизвестный тариф.", show_alert=True)

    user = callback.from_user
    if not get_user_by_id(user.id):
        add_user(user.id, user.username, user.first_name, user.last_name)

    seed_keys_if_empty()
    key = get_free_key(tariff_code, user.id)
    if not key:
        return await callback.message.answer("К сожалению, нет свободных ключей. Свяжитесь с поддержкой.")

    add_subscription(
        user.id, tariff_code, key,
        datetime.now(),
        datetime.now() + timedelta(days=tariff["months"] * 30)
    )

    # Отправляем админу уведомление
    if ADMIN_CHAT_ID:
        try:
            await callback.bot.send_message(
                ADMIN_CHAT_ID,
                f"💳 Новый платёж!\nПользователь: {user.full_name} (@{user.username or 'без username'})\n"
                f"Тариф: {tariff['title']}\nКлюч: <code>{key}</code>"
            )
        except Exception:
            pass

    caption = (
        f"🎉 <b>Поздравляем с покупкой Happ VPN!</b>\n\n"
        f"Ваш ключ: <code>{key}</code>\n\n"
        "Сохраните его — он останется активным на весь срок подписки."
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Инструкция установки", callback_data="menu:inst")],
        [InlineKeyboardButton(text="Перейти в Happ VPN бот 🔁", url="https://t.me/Happ_ibot")]
    ])

    await callback.message.delete()  # удалить все предыдущие
    await callback.message.answer_photo(
        photo=FSInputFile(MEDIA.get("success_image")),
        caption=caption,
        reply_markup=keyboard,
    )
    await callback.answer("Покупка подтверждена!")
