from aiogram import Bot

from config.config import CHANNEL_ID

async def kick_user_from_channel_by_user_id(bot: Bot, telegram_id):
    try:
        await bot.ban_chat_member(chat_id=CHANNEL_ID, user_id=telegram_id)
        await bot.unban_chat_member(chat_id=CHANNEL_ID, user_id=telegram_id)
    except Exception as e:
        print(f"Ошибка при удалении {telegram_id} из канала: {e}")