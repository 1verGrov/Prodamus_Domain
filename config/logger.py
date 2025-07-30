# logs.py
import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_logging():
    """Настройка логирования без перехвата stdout/stderr"""

    # Основной логгер приложения
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Формат логов
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Файловый вывод (всё с ротацией)
    file_handler = RotatingFileHandler(
        "app.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 2. Консольный вывод (дублирование в терминал)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Только INFO и выше в консоль
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Настройки для SQLAlchemy
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.orm").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

    # Для Uvicorn - оставляем его стандартные логи
    logging.getLogger("uvicorn").propagate = False
    logging.getLogger("uvicorn.access").propagate = False