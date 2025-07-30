from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from api.prodamus_link_gen import generate_payment_link, generate_cancel_link


async def create_sub_buttons(user):
    one_mounth_url = await generate_payment_link(
                    user.telegram_id,
                    "Подписка на канал 1 месяц",
                    990,
                    1,
                    "Подписка на контент канала anishamilk_blog")

    three_mounth_url = await generate_payment_link(
                    user.telegram_id,
                    "Подписка на канал 3 месяц",
                    2590,
                    1,
                    "Подписка на контент канала anishamilk_blog")

    SUBSCRIPTION_BUTTONS = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1 месяц - 990 руб", url= one_mounth_url),
            ],
            [
                InlineKeyboardButton(text="3 месяца - 2590 руб", url=three_mounth_url),
            ],
            [
                InlineKeyboardButton(text="Связаться с администратором", url="https://t.me/Nartv74")
            ]
        ]
    )
    return SUBSCRIPTION_BUTTONS

async def inventation_buttons(invite_link):
    subscribtion_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Присоединиться", url=f"{invite_link}")
            ]
        ]
    )
    return subscribtion_kb


async def create_unsub_buttons(telegram_id):

    CANCEL_BUTTONS = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отписаться", callback_data="confirm_unsub")]  # ← Указан text= и url=
        ]
    )

    return CANCEL_BUTTONS