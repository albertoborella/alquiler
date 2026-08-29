from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import APIKeyHeader
from pathlib import Path
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup: DB tables managed by init.sql — no create_all
    # Admin users are created via: python backend/scripts/createsuperuser.py
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="Alquiler API",
    description="API para sistema de gestión de alquileres",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    # Swagger UI: show API key input for X-Access-Token
    swagger_ui_init_oauth=None,
)

# API key scheme for Swagger UI — lets users paste the access_token
app.openapi_schema = None  # Force rebuild on first request


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Add API key security scheme
    schema["components"]["securitySchemes"] = {
        "X-Access-Token": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Access-Token",
            "description": "Access token from POST /api/login. Paste the access_token value.",
        }
    }
    # Apply globally so all endpoints use it
    schema["security"] = [{"X-Access-Token": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
uploads_dir = Path("uploads/images")
uploads_dir.mkdir(parents=True, exist_ok=True)

# Mount static files for images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include API router
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Alquiler API",
        "version": "0.1.0",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
