import os
import asyncio
from aiogram import Dispatcher
from aiohttp import web
from bot import bot, router
from database import init_db
from web_app import setup_routes

async def on_startup():
    """Действия при запуске бота"""
    print("🤖 Бот Ghost FluX Casino запущен!")
    await init_db()

async def start_bot():
    """Запуск бота"""
    dp = Dispatcher()
    dp.include_router(router)
    
    await on_startup()
    await dp.start_polling(bot)

async def start_web_app():
    """Запуск веб-приложения для Mini App"""
    app = web.Application()
    setup_routes(app)
    return app

if __name__ == "__main__":
    # Если запускается на Railway (с портом)
    if "PORT" in os.environ:
        # Запускаем веб-сервер для Mini App
        app = asyncio.run(start_web_app())
        web.run_app(app, port=int(os.environ["PORT"]))
    else:
        # Локальный запуск бота
        asyncio.run(start_bot())