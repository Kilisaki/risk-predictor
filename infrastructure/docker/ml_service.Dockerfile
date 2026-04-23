FROM python:3.12-slim

WORKDIR /app

# Копируем ВСЮ папку requirements
COPY requirements/ ./requirements/

# Устанавливаем зависимости из ml.txt
RUN pip install --no-cache-dir -r requirements/ml.txt

# Копируем код ml_service
COPY ml_service/ ./ml_service/

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "ml_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
