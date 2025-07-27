from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
import datetime

from database.db import connection
from database.models import Subscription, User

@connection
async def insert_new_user(session: AsyncSession, telegram_id: int, username: str):

    new_user = User(
        telegram_id=telegram_id,
        username=username,
    )
    session.add(new_user)
    await session.commit()

@connection
async def delete_from_subscriptions_by_user_id(session: AsyncSession, telegram_id: int):
    stmt = delete(Subscription).where(Subscription.user_telegram_id == telegram_id)
    await session.execute(stmt)
    await session.commit()