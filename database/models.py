from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from database.db import Base
import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    phone_number = Column(String, nullable=True)

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, nullable=False)
    user_telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    paid_until = Column(DateTime, nullable=True)
    order_id = Column(String, nullable=False)

class BotLog(Base):
    __tablename__ = 'bot_logs'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    user_telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    sub_id = Column(Integer, ForeignKey('subscriptions.id'), nullable=False)
    log_date = Column(DateTime, default=datetime.datetime.utcnow)
    text = Column(String)