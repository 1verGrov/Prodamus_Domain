from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
import datetime

from database.db import connection
from database.models import Subscription, User, BotLog

@connection
async def insert_new_user(session: AsyncSession, telegram_id: int, username: str):

    new_user = User(
        telegram_id=telegram_id,
        username=username,
        phone_number=''
    )
    session.add(new_user)
    await session.commit()
    return new_user

@connection
async def insert_phone_number_to_user(session: AsyncSession, telegram_id: int, phone_number: str):
    user = await session.execute(
        select(User).where(User.telegram_id == telegram_id))
    user = user.scalar_one_or_none()
    user.phone_number = phone_number
    await session.commit()

@connection
async def update_subscribtion_date(session: AsyncSession, telegram_id: int, date):
    sub = await session.execute(
        select(Subscription).where(Subscription.user_telegram_id == telegram_id))
    sub = sub.scalar_one_or_none()
    sub.paid_until = date
    await session.commit()

@connection
async def delete_from_subscriptions_by_user_id(session: AsyncSession, telegram_id: int):
    stmt = delete(Subscription).where(Subscription.user_telegram_id == telegram_id)
    await session.execute(stmt)
    await session.commit()

@connection
async def insert_new_subscription(session: AsyncSession, telegram_id: int, paid_until, subscription_id, order_id):

    new_sub = Subscription(
        user_telegram_id=telegram_id,
        paid_until=paid_until,
        subscription_id=subscription_id,
        order_id = order_id
    )
    session.add(new_sub)
    await session.commit()

@connection
async def insert_new_log(
        session: AsyncSession,
        telegram_id: int,
        username: str,
        sub_id: int,
        text: str
):
    new_log = BotLog(
        user_telegram_id=telegram_id,
        username=username,
        sub_id=sub_id,
        text=text,
        log_date=datetime.datetime.now().utcnow(),
    )

    session.add(new_log)
    await session.commit()