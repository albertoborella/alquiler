from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.configuracion import Configuracion


async def get_config(db: AsyncSession, key: str) -> Configuracion | None:
    result = await db.execute(select(Configuracion).where(Configuracion.key == key))
    return result.scalar_one_or_none()


async def get_all_config(db: AsyncSession) -> dict[str, str | None]:
    result = await db.execute(select(Configuracion))
    rows = result.scalars().all()
    return {row.key: row.value for row in rows}


async def set_config(db: AsyncSession, key: str, value: str | None) -> Configuracion:
    existing = await get_config(db, key)
    if existing:
        existing.value = value
        db.add(existing)
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        config = Configuracion(key=key, value=value)
        db.add(config)
        await db.commit()
        await db.refresh(config)
        return config
