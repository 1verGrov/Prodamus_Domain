import asyncio
from aiogram import Router, F, types
from aiogram.types import Message
from bot_instance import bot
from zoneinfo import ZoneInfo
import locale
from aiogram.types import CallbackQuery

import db_queries.queries_read as db_qr
import db_queries.queries_write as db_qw
from db_queries.queries_read import get_subscription_by_telegram_id
from api.prodamus_link_gen import generate_cancel_link
import texts.messages_texts as tm
import keyboards.keyboards as kb

from config.config import CHANNEL_ID


router = Router()
#locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8') для линукса
locale.setlocale(locale.LC_TIME, 'russian')

async def check_chat_location(message: Message):
    location = message.chat.location
    return CHANNEL_ID == location

async def ask_about_sub(message: Message):
    if await check_chat_location(message):
        return
    # Сделать delay на 31 минут = (31 * 60)
    await asyncio.sleep(31 * 60)
    # После проверку статуса подписки
    telegram_id = message.from_user.id

    sub = await db_qr.get_subscription_by_telegram_id(telegram_id=telegram_id)

    if not sub:
        user = await db_qr.get_user_by_telegram_id(telegram_id=telegram_id)
        print(user)
        await message.answer(
            text=tm.LINK_LIVE_EXPIRED,
            reply_markup=await kb.create_sub_buttons(user))


async def send_channel_invite(telegram_id: int):
    try:
        # Проверяем, есть ли активная подписка с уже созданным инвайтом
        if await get_subscription_by_telegram_id(telegram_id):

            # создаём одноразовую ссылку с лимитом 1
            invite_link = await bot.create_chat_invite_link(
                chat_id=CHANNEL_ID,
                member_limit=1,
                creates_join_request=False,
                name=f"invite_for_{telegram_id}"
            )

            await bot.send_message(
                telegram_id,
                f"Благодарю за оплату подписки! Присоединяйся к закрытому каналу!",
                reply_markup=await kb.inventation_buttons(invite_link.invite_link)
            )

    except Exception as e:
        await bot.send_message(
            telegram_id,
            f"Оплата прошла, но не получилось создать ссылку: {e}"
        )


@router.message(F.text == "/start")
async def start_handler(message: Message):
    if await check_chat_location(message):
        return

    telegram_id = message.from_user.id
    username = message.from_user.username
    #if await get_subscription_by_telegram_id(telegram_id):
        #return

    user = await db_qr.get_user_by_telegram_id(telegram_id=telegram_id)
    # если пользователя новый — создаём запись
    if not user:
        user = await db_qw.insert_new_user(telegram_id=telegram_id, username=username)
    print("public 4")
    await message.answer_photo(
        photo='AgACAgIAAxkBAAMWaHrchaWhIZmSwdRSDsIF9vREjh8AAv73MRt2IdFL4q2W-pnEhhYBAAMCAAN4AAM2BA',
        caption=tm.START_MESSAGE,
        reply_markup=await kb.create_sub_buttons(user)
    )

    await ask_about_sub(message)

@router.message(F.text == "/check_subscription")
async def check_subscription_handler(message: Message):
    if await check_chat_location(message):
        return

    telegram_id = message.from_user.id

    sub = await get_subscription_by_telegram_id(telegram_id)

    if sub:
        paid_until_utc = sub.paid_until.replace(tzinfo=ZoneInfo('UTC'))
        paid_until_msk = paid_until_utc.astimezone(ZoneInfo('Europe/Moscow'))
        formatted_time = paid_until_msk.strftime("%d %B %Y, %H:%M") + " (МСК)"
        await message.answer(text=tm.CHECK_SUBSCRIBTION_EXIST + f" {formatted_time}")
    else:
        user = await db_qr.get_user_by_telegram_id(telegram_id=telegram_id)
        await message.answer(text=tm.CHECK_SUBSCRIBTION_NOT_EXIST,
                             reply_markup=await kb.create_sub_buttons(user))

@router.message(F.text == "/unsubscribe")
async def unsubscribe_handler(message: Message):
    if await check_chat_location(message):
        return

    await message.answer(
        text="Вы уверены, что хотите отменить подписку?",
        reply_markup=await kb.create_unsub_buttons(message.from_user.id)
    )

@router.callback_query(lambda c: c.data == "confirm_unsub")
async def process_unsub(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        result = await generate_cancel_link(user_id)  # Вызываем API Prodamus
        print(result)
        if result["raw_response"] == 'success':
            await callback.message.edit_text("✅ Подписка успешно отменена")
        else:
            await callback.message.edit_text(f"❌ Ошибка: {result.get('message')}")
    except Exception as e:
        await callback.message.edit_text(f"⚠️ Ошибка сервера: {str(e)}")