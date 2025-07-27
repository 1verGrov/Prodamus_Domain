from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from api.prodamus_link_gen import generate_payment_link
from services.subscription import generate_subscription_id

#async def create_sub_buttons(user: dict):
def create_sub_buttons(user):

    SUBSCRIPTION_BUTTONS = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="На 1 месяц", url=generate_payment_link(
                    user.telegram_id,
                    "Подписка на канал 1 месяц",
                    50,
                    1,
                    generate_subscription_id(),
                    "Подписка на контент канала ...."
                ),callback_data="sub-1"),
            ],
            [
                InlineKeyboardButton(text="На 3 месяца", url=generate_payment_link(
                    user.telegram_id,
                    "Подписка на канал 3 месяц",
                    50,
                    1,
                    generate_subscription_id(),
                    "Подписка на контент канала ...."
                ) ,callback_data="sub-3"),
            ],
            [
                InlineKeyboardButton(text="Связаться с администратором", url="https://t.me/Nartv74")
            ]
        ]
    )

    return SUBSCRIPTION_BUTTONS