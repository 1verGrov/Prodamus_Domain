from aiogram import Bot
from config.config import PUBLIC_BOT_TOKEN, ADMINE_BOT_TOKEN
from aiogram.types import BotCommand

bot = Bot(token=PUBLIC_BOT_TOKEN)
ad_bot = Bot(token=ADMINE_BOT_TOKEN)

async def set_commands():
    # Команды для публичного бота
    commands = [
        BotCommand(command='start', description='Запуск бота'),
        BotCommand(command='unsubscribe', description='Отписаться'),
        BotCommand(command='check_subscription', description='Проверить подписку'),
    ]

    # Команды для админского бота
    admin_commands = [
        BotCommand(command='last5days', description='Логи за 5 дней'),
        BotCommand(command='last10days', description='Логи за 10 дней'),
        BotCommand(command='last30days', description='Логи за 30 дней'),
        BotCommand(command='search', description='Поиск по дате (YYYY-MM-DD)'),
    ]

    await ad_bot.set_my_commands(admin_commands)
    await bot.set_my_commands(commands)

async def on_startup():
    await set_commands()