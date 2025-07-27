from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from database.db import Base
import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    paid_until = Column(DateTime, nullable=True)