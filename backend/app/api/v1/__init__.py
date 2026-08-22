from fastapi import APIRouter
from app.api.v1.auth import router as auth_router

api_router = APIRouter()

# Include auth router
api_router.include_router(auth_router, tags=["authentication"])


@api_router.get("/health")
async def health_check():
    """API health check endpoint."""
    return {"status": "healthy", "message": "API is running"}
