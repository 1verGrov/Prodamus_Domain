import asyncio
from aiogram import Router, F, types
from aiogram.types import Message

import db_queries.queries_read as db_qr
import db_queries.queries_write as db_qw
import texts.messages_texts as tm
import keyboards.keyboards as kb


router = Router()

@router.message(F.text == "/start")
async def start_handler(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username

    user = await db_qr.get_user_by_telegram_id(telegram_id=telegram_id)

    # если пользователя новый — создаём запись
    if not user:
        user = await db_qw.insert_new_user(telegram_id=telegram_id, username=username)

    await message.answer_photo(
        photo='AgACAgIAAxkBAAMWaHrchaWhIZmSwdRSDsIF9vREjh8AAv73MRt2IdFL4q2W-pnEhhYBAAMCAAN4AAM2BA',
        text=tm.START_MESSAGE,
        reply_markup=kb.create_sub_buttons(user)
    )


@router.callback_query(lambda c: c.data and "sub" in c.data)
async def confirm_url(callback_query: types.CallbackQuery):
    # Сделать delay на 31 минут = (31 * 60)
    await asyncio.sleep(2 * 60)
    # После проверку статуса подписки
    telegram_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    bot = callback_query.bot

    sub = await db_qr.get_subscription_by_telegram_id(telegram_id=telegram_id)

    if not sub:
        user = await db_qr.get_user_by_telegram_id(telegram_id=telegram_id)
        await bot.send_message(
            chat_id=chat_id,
            text=tm.LINK_LIVE_EXPIRED,
            reply_markup=kb.create_sub_buttons(user))
