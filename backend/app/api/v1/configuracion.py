from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.core.deps import get_current_admin_user
from app.crud.configuracion import get_all_config, set_config

router = APIRouter()


class ConfigSetRequest(BaseModel):
    key: str
    value: Optional[str] = None


class ConfigBulkSetRequest(BaseModel):
    items: dict[str, Optional[str]]


@router.get("/configuracion")
async def read_configuracion(db: AsyncSession = Depends(get_db)):
    """Get all configuration (public)."""
    config = await get_all_config(db)
    return config


@router.put("/configuracion")
async def update_configuracion(
    data: ConfigBulkSetRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    """Set multiple configuration keys (admin only)."""
    saved = {}
    for key, value in data.items.items():
        config = await set_config(db, key, value)
        saved[key] = config.value
    return saved
