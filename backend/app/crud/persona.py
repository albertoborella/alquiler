from typing import Optional, List
from datetime import datetime
import uuid
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.persona import Persona, PersonaCreate, PersonaUpdate


async def get_persona(db: AsyncSession, persona_id: str) -> Optional[Persona]:
    """Get a persona by ID."""
    return await db.get(Persona, persona_id)


async def get_persona_by_cuit(db: AsyncSession, cuit: str) -> Optional[Persona]:
    """Get a persona by CUIT."""
    statement = select(Persona).where(Persona.cuit == cuit)
    result = await db.execute(statement)
    return result.scalars().first()


async def get_personas(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    rol: Optional[str] = None
) -> List[Persona]:
    """Get multiple personas with optional rol filter."""
    statement = select(Persona)

    if rol is not None:
        if rol == "propietario":
            # Show both pure propietarios and those who are ambos
            statement = statement.where(Persona.rol.in_(["propietario", "ambos"]))
        elif rol == "inquilino":
            # Show both pure inquilinos and those who are ambos
            statement = statement.where(Persona.rol.in_(["inquilino", "ambos"]))
        else:
            statement = statement.where(Persona.rol == rol)

    statement = statement.offset(skip).limit(limit)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def get_propietarios(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Persona]:
    """Get all propietarios (rol in ['propietario', 'ambos'])."""
    return await get_personas(db, skip=skip, limit=limit, rol="propietario")


async def get_inquilinos(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Persona]:
    """Get all inquilinos (rol in ['inquilino', 'ambos'])."""
    return await get_personas(db, skip=skip, limit=limit, rol="inquilino")


async def create_persona(db: AsyncSession, persona_in: PersonaCreate) -> Persona:
    """Create a new persona."""
    persona_id = str(uuid.uuid4())

    persona = Persona(
        id=persona_id,
        nombre=persona_in.nombre,
        cuit=persona_in.cuit,
        iva=persona_in.iva,
        telefono=persona_in.telefono,
        email=persona_in.email,
        direccion=persona_in.direccion,
        rol=persona_in.rol,
        created_at=datetime.utcnow(),
    )

    db.add(persona)
    await db.commit()
    await db.refresh(persona)
    return persona


async def update_persona(db: AsyncSession, persona_id: str, persona_in: PersonaUpdate) -> Optional[Persona]:
    """Update a persona."""
    persona = await db.get(Persona, persona_id)
    if not persona:
        return None

    update_data = persona_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(persona, key, value)

    persona.updated_at = datetime.utcnow()
    db.add(persona)
    await db.commit()
    await db.refresh(persona)
    return persona


async def delete_persona(db: AsyncSession, persona_id: str) -> bool:
    """Delete a persona."""
    persona = await db.get(Persona, persona_id)
    if not persona:
        return False

    await db.delete(persona)
    await db.commit()
    return True
