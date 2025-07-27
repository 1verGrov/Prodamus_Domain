import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.db import connection
from database.models import Subscription

@connection
async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int):
    result = await session.execute(
        select(Subscription).where(Subscription.user_telegram_id == telegram_id)
    )
    return result.scalars().first()

@connection
async def get_subscription_by_telegram_id(session: AsyncSession, telegram_id: int):
    result = await session.execute(
        select(Subscription).where(Subscription.user_telegram_id == telegram_id)
    )
    return result.scalars().first()

@connection
async def get_all_expired_users(session: AsyncSession):
    now = datetime.datetime.utcnow()

    result = await session.execute(
        select(Subscription).where(
            Subscription.paid_until < now
        )
    )
    return result.scalars().all()