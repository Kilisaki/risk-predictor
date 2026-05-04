"""Health check endpoint."""
import httpx
from fastapi import APIRouter
from backend.db.session import SessionLocal
from backend.models.schemas import HealthCheckResponse
from sqlalchemy import text
router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint.
    Проверяет:
    - Подключение к PostgreSQL
    - Доступность ML сервиса
    """
    
    # 1. Проверка БД
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"
    finally:
        if 'db' in locals():
            db.close()
    
    # 2. Проверка ML сервиса
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://risk-ml:8001/health")
            ml_status = "ready" if response.status_code == 200 else f"error: status {response.status_code}"
    except httpx.ConnectError:
        ml_status = "unavailable: connection refused"
    except httpx.TimeoutException:
        ml_status = "unavailable: timeout"
    except Exception as e:
        ml_status = f"error: {str(e)[:50]}"
    
    # 3. Определяем общий статус
    is_healthy = db_status == "connected" and ml_status == "ready"
    print(f"Health Check - DB: {db_status}, ML Service: {ml_status}")
    return {
        "status": "ok" if is_healthy else "degraded",
        "database": db_status,
        "model_service": ml_status  # используем alias из схемы
    }