import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.config import ALEX_KLYAUZER_ID
from db_queries.subscription import get_user_by_telegram_id, create_new_subscription
from services.payment import generate_payment_link

import texts.messages_texts as tm
import keyboards.keyboards as kb


router = Router()

@router.message(F.text == "/start")
async def start_handler(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username

    user = await get_user_by_telegram_id(telegram_id=telegram_id)

    # если пользователя новый — создаём запись
    if not user:
        await message.answer_photo(
            photo='AgACAgIAAxkBAAMWaHrchaWhIZmSwdRSDsIF9vREjh8AAv73MRt2IdFL4q2W-pnEhhYBAAMCAAN4AAM2BA',
            reply_markup=kb.SUBSCRIPTION_BUTTONS
        )
        user = await add_new_user(telegram_id=telegram_id, username=username)


    # Проверка платежа от кнопки, либо надо реализовать ссылку как кнопку
    if user.status != "active":
        #Сделать проверку на предыдущие платежи []

@router.callback_query_handler(lambda c: c.data.contains("sub"))
async def confirm_url(callback_query: types.CallbackQuery):
    # Сделать delay на 30 минут
    # После проверку статуса оплаты, если не было то отмена иначе сообщение
    period = c.data.strip('-')[1]
