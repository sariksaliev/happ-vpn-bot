from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from happ_vpn_final.happ_vpn_final.database.db_postgres import (
    add_many_keys,
    delete_keys_by_tariff,
    count_users,
    count_subscriptions,
    sum_payments,
    stats_last_24h,
    count_free_keys,    # считаем остатки ключей
)

ADMIN_ID = 1100371327
router = Router()


# ---------------------- КЛАВИАТУРЫ ----------------------

def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ключи", callback_data="admin:add_menu")],
        [InlineKeyboardButton(text="🗑 Удалить ключи", callback_data="admin:delete_menu")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats")],
    ])


def get_add_keys_tariff_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 месяц", callback_data="admin:add_keys:1m")],
        [InlineKeyboardButton(text="3 месяца", callback_data="admin:add_keys:3m")],
        [InlineKeyboardButton(text="6 месяцев", callback_data="admin:add_keys:6m")],
        [InlineKeyboardButton(text="12 месяцев", callback_data="admin:add_keys:12m")],
    ])


def get_delete_keys_tariff_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Удалить 1 месяц", callback_data="admin:del_keys:1m")],
        [InlineKeyboardButton(text="Удалить 3 месяца", callback_data="admin:del_keys:3m")],
        [InlineKeyboardButton(text="Удалить 6 месяцев", callback_data="admin:del_keys:6m")],
        [InlineKeyboardButton(text="Удалить 12 месяцев", callback_data="admin:del_keys:12m")],
    ])


# ---------------------- АДМИН ПАНЕЛЬ ----------------------

@router.message(F.text == "/admin")
async def admin_home(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("Нет доступа ❌")

    keys_1m = count_free_keys("1m")
    keys_3m = count_free_keys("3m")
    keys_6m = count_free_keys("6m")
    keys_12m = count_free_keys("12m")

    text = (
        "👑 <b>Админ-панель</b>\n\n"
        "🔑 <b>Остаток ключей:</b>\n"
        f"1 месяц: <b>{keys_1m}</b>\n"
        f"3 месяца: <b>{keys_3m}</b>\n"
        f"6 месяцев: <b>{keys_6m}</b>\n"
        f"12 месяцев: <b>{keys_12m}</b>\n"
    )

    await message.answer(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")


# ---------------------- МЕНЮ ДОБАВЛЕНИЯ ----------------------

@router.callback_query(F.data == "admin:add_menu")
async def admin_add_menu(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("Нет доступа", show_alert=True)

    await callback.message.answer(
        "Выберите тариф, для которого хотите добавить ключи:",
        reply_markup=get_add_keys_tariff_keyboard()
    )
    await callback.answer()


# ---------------------- ДОБАВЛЕНИЕ КЛЮЧЕЙ ПО ТАРИФУ ----------------------

@router.callback_query(F.data.startswith("admin:add_keys:"))
async def admin_add_keys(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("Нет доступа", show_alert=True)

    tariff_code = callback.data.split(":")[2]

    router.temp_tariff = tariff_code

    await callback.message.answer(
        f"Отправьте ключи для тарифа <b>{tariff_code}</b>.\n"
        "Каждый ключ — с новой строки:",
        parse_mode="HTML",
    )
    await callback.answer()

    # Ждём следующее сообщение — там будут сами ключи
    router.message.register(save_keys)


async def save_keys(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    tariff_code = router.temp_tariff
    keys = [k.strip() for k in message.text.split("\n") if k.strip()]

    add_many_keys(keys, tariff_code)

    await message.answer(
        f"Добавлено ключей: <b>{len(keys)}</b> 🔑\n"
        f"Тариф: <b>{tariff_code}</b>",
        parse_mode="HTML",
    )


# ---------------------- МЕНЮ УДАЛЕНИЯ ----------------------

@router.callback_query(F.data == "admin:delete_menu")
async def admin_delete_menu(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("Нет доступа", show_alert=True)

    await callback.message.answer(
        "Выберите тариф, откуда удалить ВСЕ ключи:",
        reply_markup=get_delete_keys_tariff_keyboard()
    )
    await callback.answer()


# ---------------------- УДАЛЕНИЕ КЛЮЧЕЙ ПО ТАРИФУ ----------------------

@router.callback_query(F.data.startswith("admin:del_keys:"))
async def admin_delete_keys(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("Нет доступа", show_alert=True)

    tariff_code = callback.data.split(":")[2]

    delete_keys_by_tariff(tariff_code)

    await callback.message.answer(
        f"Все ключи тарифа <b>{tariff_code}</b> удалены ❌",
        parse_mode="HTML",
    )
    await callback.answer()


# ---------------------- СТАТИСТИКА ----------------------

@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("Нет доступа", show_alert=True)

    users = count_users()
    subs = count_subscriptions()
    income = sum_payments()
    last_users, last_subs, last_income = stats_last_24h()

    text = (
        "📊 <b>Статистика</b>\n\n"
        "За всё время:\n"
        f"👥 Пользователей: <b>{users}</b>\n"
        f"🛒 Покупок: <b>{subs}</b>\n"
        f"💰 Доход: <b>{income} ₽</b>\n\n"
        "За 24 часа:\n"
        f"👥 Новые пользователи: <b>{last_users}</b>\n"
        f"🛒 Новые покупки: <b>{last_subs}</b>\n"
        f"💰 Доход: <b>{last_income} ₽</b>"
    )

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()
