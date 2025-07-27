import asyncio
import logging

from aiogram import Bot, Dispatcher
from handlers.public import router as start_router
from database.db import create_tables

from fastapi import FastAPI
from uvicorn import Config, Server

from config.config import PUBLIC_BOT_TOKEN
from api import prodamus_webhooks
from services.subscription import check_and_expire_subscriptions

# Инициализация бота
bot = Bot(token=PUBLIC_BOT_TOKEN)

# Telegram Bot
dp = Dispatcher()
dp.include_router(start_router)

# FastAPI App
app = FastAPI()
app.include_router(prodamus_webhooks.router)

# 🔁 Функция запуска FastAPI в фоне
async def start_fastapi() -> None:
    """Запуск FastAPI сервера"""
    config = Config(app=app, host="0.0.0.0", port=8001, loop="asyncio", log_level="info")
    server = Server(config)
    await server.serve()

# 🔁 Функция запуска Telegram-бота
async def start_telegram():
    await dp.start_polling(bot)

async def start_expire_checker(bot: Bot):
    """Фоновая проверка подписок (работает бесконечно)"""
    while True:
        try:
            await check_and_expire_subscriptions(bot=bot)
            await asyncio.sleep(24 * 60 * 60)  # каждые 24 часа
        except Exception as e:
            await asyncio.sleep(10 * 60)  # пауза при ошибке

# 🔁 Общий запуск
async def main():
    await create_tables()
    logging.basicConfig(level=logging.INFO)
    await asyncio.gather(
        start_fastapi(),
        start_telegram(),
        start_expire_checker(bot),
    )

if __name__ == "__main__":
    asyncio.run(main())
