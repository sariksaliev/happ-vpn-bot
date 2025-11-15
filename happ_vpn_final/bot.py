
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from happ_vpn_final.happ_vpn_final.config import BOT_TOKEN
from happ_vpn_final.happ_vpn_final.database.db_postgres import init_db
from happ_vpn_final.happ_vpn_final.services.vpn_keys import seed_keys_if_empty
from happ_vpn_final.happ_vpn_final.handlers import start, tariffs, keys, instructions
from happ_vpn_final.happ_vpn_final.handlers.admin_panel import router as admin_router

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан. Укажите его в .env")

    init_db()
    seed_keys_if_empty()

    bot = Bot(
        BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(tariffs.router)
    dp.include_router(keys.router)
    dp.include_router(instructions.router)
    dp.include_router(admin_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
