# Используем официальный образ PostgreSQL
FROM postgres:16-alpine

# Устанавливаем переменные окружения
ENV POSTGRES_USER=myuser \
    POSTGRES_PASSWORD=mypassword \
    POSTGRES_DB=mydb \
    POSTGRES_INITDB_ARGS="--encoding=UTF-8 --locale=ru_RU.UTF-8"

# Копируем скрипты инициализации
COPY ./init-scripts /docker-entrypoint-initdb.d/

# Копируем пользовательскую конфигурацию PostgreSQL
COPY ./postgresql.conf /etc/postgresql/postgresql.conf

# Изменяем порт (опционально)
EXPOSE 5432

# Запускаем PostgreSQL с пользовательским конфигом
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]