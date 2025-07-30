import random
from aiogram import Bot
import time

from db_queries.queries_read import get_all_expired_users, get_user_by_telegram_id, get_subscription_by_telegram_id
from db_queries.queries_write import delete_from_subscriptions_by_user_id, insert_new_subscription, insert_new_log
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
        await kick_user_from_channel_by_user_id(bot, user.user_telegram_id)
        await delete_from_subscriptions_by_user_id(user.user_telegram_id)

async def activate_subscription(telegram_id, paid_until, subscription_id, order_id):
    await insert_new_subscription(telegram_id, paid_until, subscription_id, order_id)

async def log_subscribtion (json_data, telegram_id, sub_id):
    text_data = str(json_data)
    user = await get_user_by_telegram_id(telegram_id)
    sub = await get_subscription_by_telegram_id(telegram_id)
    await insert_new_log(
        telegram_id=telegram_id,
        username=user.username,
        sub_id=sub.id,
        text=text_data,
    )
