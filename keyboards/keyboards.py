from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

SUBSCRIPTION_BUTTONS = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="На 1 месяц", url="конструктор ссылки" ,callback_data="sub-1"),
        ],
        [
            InlineKeyboardButton(text="На 3 месяца", url="конструктор ссылки" ,callback_data="sub-3"),
        ],
        [
            InlineKeyboardButton(text="Связаться с администратором", url="https://t.me/Nartv74")
        ]
    ]
)