# projects/risk-predictor/infrastructure/docker/ml_service.Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код ml_service
COPY ml_service/ ./ml_service/

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "ml_service.main:app", "--host", "0.0.0.0", "--port", "8001"]