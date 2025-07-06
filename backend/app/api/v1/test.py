from fastapi import APIRouter
from pydantic import BaseModel
from ...core.config import settings

router = APIRouter(tags=["test"])

class TestResponse(BaseModel):
    status: str
    api_prefix: str
    openai_configured: bool
    environment: str

@router.get("/test", response_model=TestResponse)
async def test_endpoint() -> TestResponse:
    """Test endpoint to verify deployment configuration"""
    return TestResponse(
        status="ok",
        api_prefix=settings.API_PREFIX,
        openai_configured=bool(settings.OPENAI_API_KEY),
        environment=settings.ENVIRONMENT
    )

@router.get("/test/routes")
async def test_routes():
    """List all available routes for debugging"""
    return {
        "available_endpoints": [
            "/v1/test",
            "/v1/test/routes", 
            "/v1/compare",
            "/v1/explain",
            "/v1/health",
            "/v1/strategies"
        ],
        "note": "These endpoints should be accessible via the deployed app"
    }
