from typing import Optional, List
from datetime import datetime
import uuid
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inmueble import Inmueble, InmuebleCreate, InmuebleUpdate, InmueblePropietarioIn
from app.models.copropiedad import Copropiedad, CopropiedadCreate
from app.models.persona import Persona, PersonaCreate
from app.crud.persona import get_persona, get_persona_by_cuit


async def get_inmueble(db: AsyncSession, inmueble_id: str) -> Optional[Inmueble]:
    """Get an inmueble by ID."""
    return await db.get(Inmueble, inmueble_id)


async def get_inmuebles(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    categoria: Optional[str] = None
) -> List[Inmueble]:
    """Get multiple inmuebles with optional filters."""
    statement = select(Inmueble)

    if estado is not None:
        statement = statement.where(Inmueble.estado == estado)
    if categoria is not None:
        statement = statement.where(Inmueble.categoria == categoria)

    statement = statement.offset(skip).limit(limit)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def create_inmueble(db: AsyncSession, inmueble_in: InmuebleCreate) -> Inmueble:
    """Create a new inmueble."""
    inmueble_id = str(uuid.uuid4())

    inmueble = Inmueble(
        id=inmueble_id,
        direccion=inmueble_in.direccion,
        categoria=inmueble_in.categoria,
        superficie=inmueble_in.superficie,
        habitaciones=inmueble_in.habitaciones,
        banos=inmueble_in.banos,
        dormitorios=inmueble_in.dormitorios,
        comodidades=inmueble_in.comodidades,
        descripcion=inmueble_in.descripcion,
        estado=inmueble_in.estado,
        created_at=datetime.utcnow(),
    )

    db.add(inmueble)
    await db.commit()
    await db.refresh(inmueble)
    return inmueble


async def create_inmueble_with_propietarios(
    db: AsyncSession,
    inmueble_in: InmuebleCreate,
    propietarios_in: List[InmueblePropietarioIn],
) -> Inmueble:
    """Create an inmueble and attach propietarios in ONE atomic transaction.

    Each entry in ``propietarios_in`` either references an existing persona
    by ``propietario_id``, or provides data to create a new one. Nothing is
    committed until every inmueble, persona and copropiedad row has been
    added to the session, so a failure anywhere rolls back everything.
    """
    inmueble_id = str(uuid.uuid4())
    inmueble = Inmueble(
        id=inmueble_id,
        direccion=inmueble_in.direccion,
        categoria=inmueble_in.categoria,
        superficie=inmueble_in.superficie,
        habitaciones=inmueble_in.habitaciones,
        banos=inmueble_in.banos,
        dormitorios=inmueble_in.dormitorios,
        comodidades=inmueble_in.comodidades,
        descripcion=inmueble_in.descripcion,
        estado=inmueble_in.estado,
        created_at=datetime.utcnow(),
    )
    db.add(inmueble)

    for item in propietarios_in:
        if item.propietario_id:
            persona = await get_persona(db, item.propietario_id)
            if not persona:
                raise ValueError(f"Propietario {item.propietario_id} no existe")
            propietario_id = persona.id
        else:
            if not item.nombre or not item.cuit:
                raise ValueError("Para crear un nuevo propietario, nombre y CUIT son obligatorios")
            # If a persona with that cuit already exists, reuse it.
            existing = await get_persona_by_cuit(db, item.cuit)
            if existing:
                propietario_id = existing.id
                # If currently inquilino, upgrade to ambos
                if existing.rol == "inquilino":
                    existing.rol = "ambos"
                    if item.iva:
                        existing.iva = item.iva
                    existing.updated_at = datetime.utcnow()
                    db.add(existing)
            else:
                persona = Persona(
                    id=str(uuid.uuid4()),
                    nombre=item.nombre,
                    cuit=item.cuit,
                    iva=item.iva,
                    telefono=item.telefono,
                    email=item.email,
                    direccion=item.direccion,
                    rol="propietario",
                    created_at=datetime.utcnow(),
                )
                db.add(persona)
                # Persist the new persona BEFORE building the copropiedad
                # that references it, otherwise SQLAlchemy may flush the
                # copropiedad insert first and hit the personas FK violation.
                await db.flush()
                propietario_id = persona.id

        copropiedad = Copropiedad(
            id=str(uuid.uuid4()),
            propietario_id=propietario_id,
            inmueble_id=inmueble_id,
            porcentaje_participacion=item.porcentaje_participacion,
            created_at=datetime.utcnow(),
        )
        db.add(copropiedad)

    # Single commit at the end makes the whole operation atomic.
    await db.commit()
    await db.refresh(inmueble)
    return inmueble


async def update_inmueble(db: AsyncSession, inmueble_id: str, inmueble_in: InmuebleUpdate) -> Optional[Inmueble]:
    """Update an inmueble."""
    inmueble = await db.get(Inmueble, inmueble_id)
    if not inmueble:
        return None

    update_data = inmueble_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(inmueble, key, value)

    inmueble.updated_at = datetime.utcnow()
    db.add(inmueble)
    await db.commit()
    await db.refresh(inmueble)
    return inmueble


async def delete_inmueble(db: AsyncSession, inmueble_id: str) -> bool:
    """Delete an inmueble."""
    inmueble = await db.get(Inmueble, inmueble_id)
    if not inmueble:
        return False

    await db.delete(inmueble)
    await db.commit()
    return True


# Copropiedad functions
async def get_copropiedad_by_inmueble(db: AsyncSession, inmueble_id: str) -> List[Copropiedad]:
    """Get all copropiedad relationships for an inmueble."""
    statement = select(Copropiedad).where(Copropiedad.inmueble_id == inmueble_id)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def add_propietario_to_inmueble(
    db: AsyncSession,
    propietario_id: str,
    inmueble_id: str,
    porcentaje_participacion: float = 100.00
) -> Copropiedad:
    """Add a propietario to an inmueble (copropiedad)."""
    copropiedad_id = str(uuid.uuid4())

    copropiedad = Copropiedad(
        id=copropiedad_id,
        propietario_id=propietario_id,
        inmueble_id=inmueble_id,
        porcentaje_participacion=porcentaje_participacion,
        created_at=datetime.utcnow(),
    )

    db.add(copropiedad)
    await db.commit()
    await db.refresh(copropiedad)
    return copropiedad


async def replace_copropiedad(
    db: AsyncSession,
    inmueble_id: str,
    propietarios_in: List[dict],
) -> List[Copropiedad]:
    """Replace all copropiedad records for an inmueble in one atomic transaction.

    Deletes every existing copropiedad row for *inmueble_id* and creates new ones
    from *propietarios_in*.  Each dict must contain ``propietario_id`` and
    ``porcentaje_participacion``.
    """
    import traceback
    print(f"[replace_copropiedad] inmueble_id={inmueble_id}, propietarios_in={propietarios_in}")
    try:
        # 1. Delete existing
        statement = select(Copropiedad).where(Copropiedad.inmueble_id == inmueble_id)
        result = await db.execute(statement)
        existing = result.scalars().all()
        print(f"[replace_copropiedad] found {len(existing)} existing copropiedad records to delete")
        for cop in existing:
            await db.delete(cop)
        await db.flush()

        # 2. Create new
        created: List[Copropiedad] = []
        for item in propietarios_in:
            copropiedad = Copropiedad(
                id=str(uuid.uuid4()),
                propietario_id=item["propietario_id"],
                inmueble_id=inmueble_id,
                porcentaje_participacion=item["porcentaje_participacion"],
                created_at=datetime.utcnow(),
            )
            db.add(copropiedad)
            created.append(copropiedad)

        await db.commit()
        for cop in created:
            await db.refresh(cop)
        print(f"[replace_copropiedad] OK: created {len(created)} records")
        return created
    except Exception as e:
        print(f"[replace_copropiedad] EXCEPTION: {e}")
        traceback.print_exc()
        await db.rollback()
        raise


async def remove_propietario_from_inmueble(
    db: AsyncSession,
    propietario_id: str,
    inmueble_id: str
) -> bool:
    """Remove a propietario from an inmueble."""
    statement = select(Copropiedad).where(
        Copropiedad.propietario_id == propietario_id,
        Copropiedad.inmueble_id == inmueble_id
    )
    result = await db.execute(statement)
    copropiedad = result.scalars().first()

    if not copropiedad:
        return False

    await db.delete(copropiedad)
    await db.commit()
    return True
