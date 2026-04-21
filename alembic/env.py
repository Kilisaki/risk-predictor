# alembic/env.py
import sys
import os
import re
from pathlib import Path
from logging.config import fileConfig

# Определяем корень проекта
ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

# Добавляем пути
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))

# Загружаем .env ДО импорта моделей
from dotenv import load_dotenv
env_path = ROOT_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    print(f"⚠️  Warning: .env file not found at {env_path}")

from sqlalchemy import engine_from_config, pool
from alembic import context

# Импортируем модели
from backend.db.models import Base

config = context.config

def mask_password(url: str) -> str:
    """Безопасно маскирует пароль в URL базы данных."""
    if not url:
        return "None"
    # Маскируем пароль для разных типов БД
    pattern = r'(://[^:]+:)([^@]+)(@)'
    return re.sub(pattern, r'\1***\3', url)

# Получаем URL из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "❌ DATABASE_URL не найден! "
        "Убедитесь, что:\n"
        "1. Файл .env существует в корне проекта\n"
        "2. В нем есть строка DATABASE_URL=...\n"
        f"   Путь к .env: {env_path}"
    )

# Определяем окружение
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Логируем только в development
if ENVIRONMENT != "production":
    print(f"✅ Environment: {ENVIRONMENT}")
    print(f"✅ Database URL: {mask_password(DATABASE_URL)}")

# Устанавливаем URL в конфигурацию Alembic
config.set_main_option('sqlalchemy.url', DATABASE_URL)

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    if not configuration.get("sqlalchemy.url"):
        configuration["sqlalchemy.url"] = DATABASE_URL
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # Добавляем сравнение типов колонок (опционально)
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()