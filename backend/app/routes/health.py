"""Health check route."""

from fastapi import APIRouter

from app.models.response_models import HealthResponse

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Simple liveness endpoint."""
    return HealthResponse(status="ok", service="backend")
