from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.models.inmueble import InmuebleCreate, InmuebleUpdate, InmueblePublic
from app.models.copropiedad import CopropiedadCreate, CopropiedadPublic
from app.crud.inmueble import (
    get_inmueble,
    get_inmuebles,
    create_inmueble,
    update_inmueble,
    delete_inmueble,
    get_copropiedad_by_inmueble,
    add_propietario_to_inmueble,
    remove_propietario_from_inmueble,
)
from app.core.deps import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[InmueblePublic])
async def list_inmuebles(
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = Query(None, description="Filter by estado: alquilado, disponible"),
    categoria: Optional[str] = Query(None, description="Filter by categoria: urbano, rural"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all inmuebles with optional filters."""
    return await get_inmuebles(db, skip=skip, limit=limit, estado=estado, categoria=categoria)


@router.get("/{inmueble_id}", response_model=InmueblePublic)
async def read_inmueble(
    inmueble_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get an inmueble by ID."""
    inmueble = await get_inmueble(db, inmueble_id)
    if not inmueble:
        raise HTTPException(status_code=404, detail="Inmueble not found")
    return inmueble


@router.post("/", response_model=InmueblePublic, status_code=status.HTTP_201_CREATED)
async def create_new_inmueble(
    inmueble_in: InmuebleCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new inmueble."""
    return await create_inmueble(db, inmueble_in)


@router.put("/{inmueble_id}", response_model=InmueblePublic)
async def update_existing_inmueble(
    inmueble_id: str,
    inmueble_in: InmuebleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update an inmueble."""
    inmueble = await get_inmueble(db, inmueble_id)
    if not inmueble:
        raise HTTPException(status_code=404, detail="Inmueble not found")
    return await update_inmueble(db, inmueble_id, inmueble_in)


@router.delete("/{inmueble_id}")
async def delete_existing_inmueble(
    inmueble_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Delete an inmueble."""
    inmueble = await get_inmueble(db, inmueble_id)
    if not inmueble:
        raise HTTPException(status_code=404, detail="Inmueble not found")
    await delete_inmueble(db, inmueble_id)
    return {"message": "Inmueble deleted successfully"}


# Copropiedad endpoints
@router.get("/{inmueble_id}/propietarios", response_model=List[CopropiedadPublic])
async def list_propietarios_by_inmueble(
    inmueble_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all propietarios for an inmueble."""
    inmueble = await get_inmueble(db, inmueble_id)
    if not inmueble:
        raise HTTPException(status_code=404, detail="Inmueble not found")
    return await get_copropiedad_by_inmueble(db, inmueble_id)


@router.post("/{inmueble_id}/propietarios", response_model=CopropiedadPublic, status_code=status.HTTP_201_CREATED)
async def add_propietario(
    inmueble_id: str,
    copropiedad_in: CopropiedadCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Add a propietario to an inmueble."""
    inmueble = await get_inmueble(db, inmueble_id)
    if not inmueble:
        raise HTTPException(status_code=404, detail="Inmueble not found")
    return await add_propietario_to_inmueble(
        db,
        propietario_id=copropiedad_in.propietario_id,
        inmueble_id=inmueble_id,
        porcentaje_participacion=copropiedad_in.porcentaje_participacion
    )


@router.delete("/{inmueble_id}/propietarios/{propietario_id}")
async def remove_propietario(
    inmueble_id: str,
    propietario_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Remove a propietario from an inmueble."""
    removed = await remove_propietario_from_inmueble(db, propietario_id, inmueble_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Copropiedad relationship not found")
    return {"message": "Propietario removed from inmueble successfully"}
