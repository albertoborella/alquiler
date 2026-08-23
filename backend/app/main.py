from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
import uuid
from datetime import datetime

from app.core.config import settings
from app.api.v1 import api_router
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash


async def seed_admin_user():
    """Create default admin user if none exists."""
    async with AsyncSessionLocal() as db:
        from sqlmodel import select
        result = await db.execute(select(User).where(User.role == "admin"))
        if result.scalars().first():
            return  # Admin already exists
        
        admin = User(
            id=str(uuid.uuid4()),
            email="admin@alquiler.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Administrador",
            role="admin",
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.add(admin)
        await db.commit()
        print(f"✅ Admin user created: admin@alquiler.com / admin123")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup: DB tables managed by init.sql — no create_all
    # Seed admin user
    await seed_admin_user()
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
)

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
