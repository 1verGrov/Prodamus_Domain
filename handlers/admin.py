from datetime import datetime
from bot_instance import ad_bot

from aiogram.types import Message
from aiogram import Router, F, types
import locale

from config.config import ADMIN_USERS_IDS
from db_queries.queries_read import get_logs_last_n_days, get_logs_by_date, get_user_by_telegram_id

router = Router()
#locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8') для линукса
locale.setlocale(locale.LC_TIME, 'russian')

async def new_subscriber_message(telegram_id: int, sub_type: str):
    if str(telegram_id) in ADMIN_USERS_IDS.split(','):
        user = await get_user_by_telegram_id(telegram_id)
        # Отправляем админское сообщение
        await ad_bot.send_message(
            chat_id=telegram_id,
            text=f"🛠 Админ: новая подписка {sub_type} для пользователя @{user.username}"
        )

@router.message(F.text == "/last5days")
async def admin_logs_5_days(message: Message):
    if str(message.from_user.id) in ADMIN_USERS_IDS.split(','):
        text = await get_logs_last_n_days(5)
        await message.answer(text=text)
    else:
        await message.answer(text="У вас нет прав доступа для этого")

@router.message(F.text == "/last10days")
async def admin_logs_10_days(message: Message):
    if str(message.from_user.id) in ADMIN_USERS_IDS.split(','):
        text = await get_logs_last_n_days(10)
        await message.answer(text=text)
    else:
        await message.answer(text="У вас нет прав доступа для этого")

@router.message(F.text == "/last30days")
async def admin_logs_30_days(message: Message):
    if str(message.from_user.id) in ADMIN_USERS_IDS.split(','):
        text = await get_logs_last_n_days(30)
        await message.answer(text=text)

    else:
        await message.answer(text="У вас нет прав доступа для этого")

# search_YEAR_DAY_MOUNTH
@router.message(F.text.startswith("/search "))
async def search_logs_by_date(message: Message):
    if str(message.from_user.id) not in ADMIN_USERS_IDS.split(','):
        return await message.answer("Доступ запрещён")

    try:
        date_str = message.text.split()[1]  # Формат: /search YYYY-MM-DD
        year, month, day = map(int, date_str.split('-'))
        target_date = datetime.date(year, month, day)
        text = await get_logs_by_date(target_date)
        await message.answer(text=text)
    except ValueError:
        await message.answer("Неправильный формат даты. Используйте: /search ГГГГ-ММ-ДД")