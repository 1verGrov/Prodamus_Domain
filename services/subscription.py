import random
from aiogram import Bot
import time

from db_queries.queries_read import get_all_expired_users
from db_queries.queries_write import delete_from_subscriptions_by_user_id
from services.telegram_access import kick_user_from_channel_by_user_id


async def generate_subscription_id() -> int:
    # Берем последние 8 цифр Unix-времени (чтобы избежать слишком длинных чисел)
    timestamp_part = int(time.time()) % 10 ** 8
    # Добавляем 4 случайные цифры
    random_part = random.randint(1000, 9999)

    subscription_id = int(f"{timestamp_part}{random_part}")

    return subscription_id

async def check_and_expire_subscriptions(bot: Bot):
    expired_users = await get_all_expired_users()

    for user in expired_users:
        await kick_user_from_channel_by_user_id(bot, user.telegram_id)
        await delete_from_subscriptions_by_user_id(user.telegram_id)