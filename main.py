import asyncio
import logging
from config.logger import setup_logging
from aiogram import Dispatcher
from handlers import public, admin
from database.db import create_tables
from fastapi import FastAPI
from uvicorn import Config, Server
from bot_instance import bot, ad_bot, on_startup
from api import prodamus_webhooks
from services.subscription import check_and_expire_subscriptions

app = FastAPI()
app.include_router(prodamus_webhooks.router)


async def start_fastapi():
    config = Config(app=app, host="0.0.0.0", port=8001, loop="asyncio")
    await Server(config).serve()


async def start_bots():
    # Инициализация диспетчеров
    dp_public = Dispatcher()
    dp_admin = Dispatcher()

    # Подключение роутеров
    dp_public.include_router(public.router)
    dp_admin.include_router(admin.router)

    # Запуск ботов
    await asyncio.gather(
        dp_public.start_polling(bot),
        dp_admin.start_polling(ad_bot)
    )


async def main():
    setup_logging()
    await create_tables()
    await on_startup()  # Установка команд ботов

    await asyncio.gather(
        start_fastapi(),
        start_bots(),
        check_and_expire_subscriptions(bot)  # Фоновая проверка подписок
    )

if __name__ == "__main__":
    asyncio.run(main())