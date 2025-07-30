
from datetime import timedelta
from datetime import datetime, date as date_type
import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.db import connection
from database.models import Subscription, User, BotLog

@connection
async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int):
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalars().first()

@connection
async def get_subscription_by_telegram_id(session: AsyncSession, telegram_id: int):
    result = await session.execute(
        select(Subscription).where(Subscription.user_telegram_id == telegram_id)
    )
    return result.scalars().first()

@connection
async def get_subscription_by_subscription_id(session: AsyncSession, subscription_id: str):
    result = await session.execute(
        select(Subscription).where(Subscription.subscription_id == subscription_id)
    )
    return result.scalars().first()

@connection
async def get_user_by_phone_number(session: AsyncSession, phone_number: str) -> User | None:
    """Возвращает пользователя по номеру телефона или None, если не найден."""
    result = await session.execute(
        select(User).where(User.phone_number == phone_number)
    )
    return result.scalar_one_or_none()

@connection
async def get_all_expired_users(session: AsyncSession):
    now = datetime.utcnow()

    result = await session.execute(
        select(Subscription).where(
            Subscription.paid_until < now
        )
    )
    return result.scalars().all()


@connection
async def get_logs_last_n_days(session: AsyncSession, days: int) -> str:
    """
    Получает логи за последние N дней и возвращает их в виде форматированной строки
    с временем по московскому часовому поясу (МСК, UTC+3)

    :param session: AsyncSession
    :param days: Количество дней для выборки
    :return: Строка с отформатированными логами
    """
    try:
        # Рассчитываем дату N дней назад в UTC
        n_days_ago = datetime.utcnow() - timedelta(days=days)

        # Формируем запрос
        stmt = select(BotLog).where(BotLog.log_date >= n_days_ago).order_by(BotLog.log_date.desc())
        result = await session.execute(stmt)
        logs = result.scalars().all()

        # Если логи не найдены
        if not logs:
            return f"Логи за последние {days} дней не найдены"

        # Настройка московского времени
        msk_tz = pytz.timezone('Europe/Moscow')

        # Форматируем логи в строку
        log_lines = []
        for log in logs:
            # Конвертируем время UTC в МСК
            utc_time = log.log_date.replace(tzinfo=pytz.utc)
            msk_time = utc_time.astimezone(msk_tz)
            log_time = msk_time.strftime("%Y-%m-%d %H:%M:%S (МСК)")

            log_lines.append(
                f"[{log_time}] Пользователь: {log.username or 'None'} (ID: {log.user_telegram_id}), "
                f"Подписка ID: {log.sub_id}\n"
                f"Лог: {log.text}\n"
                f"{'-' * 50}"
            )

        # Добавляем заголовок с количеством логов
        header = f"Найдено {len(logs)} записей за последние {days} дней:\n\n"
        return header + "\n".join(log_lines)

    except Exception as e:
        return f"Ошибка при получении логов: {str(e)}"


@connection
async def get_logs_by_date(session: AsyncSession, target_date: date_type) -> str:
    """
    Получает логи за указанную дату (по МСК) и возвращает их в виде форматированной строки

    :param session: AsyncSession
    :param target_date: Дата для выборки (объект datetime.date)
    :return: Строка с отформатированными логами
    """
    try:
        # Устанавливаем временные зоны
        msk_tz = pytz.timezone('Europe/Moscow')
        utc_tz = pytz.utc

        # Определяем границы даты в МСК
        start_msk = msk_tz.localize(datetime.combine(target_date, datetime.min.time()))
        end_msk = msk_tz.localize(datetime.combine(target_date, datetime.max.time()))

        # Конвертируем границы в UTC для запроса к БД
        start_utc = start_msk.astimezone(utc_tz).replace(tzinfo=None)
        end_utc = end_msk.astimezone(utc_tz).replace(tzinfo=None)

        # Формируем запрос
        stmt = select(BotLog).where(
            (BotLog.log_date >= start_utc) &
            (BotLog.log_date <= end_utc)
        ).order_by(BotLog.log_date.desc())

        result = await session.execute(stmt)
        logs = result.scalars().all()

        # Если логи не найдены
        if not logs:
            return f"Логи за {target_date.strftime('%Y-%m-%d')} не найдены"

        # Форматируем логи в строку
        log_lines = []
        for log in logs:
            # Конвертируем время UTC в МСК
            utc_time = log.log_date.replace(tzinfo=utc_tz)
            msk_time = utc_time.astimezone(msk_tz)
            log_time = msk_time.strftime("%Y-%m-%d %H:%M:%S (МСК)")

            log_lines.append(
                f"[{log_time}] Пользователь: {log.username or 'None'} (ID: {log.user_telegram_id}), "
                f"Подписка ID: {log.sub_id}\n"
                f"Лог: {log.text}\n"
                f"{'-' * 50}"
            )

        # Добавляем заголовок с количеством логов
        header = f"Найдено {len(logs)} записей за {target_date.strftime('%Y-%m-%d')}:\n\n"
        return header + "\n".join(log_lines)

    except Exception as e:
        return f"Ошибка при получении логов: {str(e)}"
