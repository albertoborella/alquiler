from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date

from app.db.session import get_db
from app.models.inmueble import Inmueble
from app.models.copropiedad import Copropiedad
from app.models.propietario import Propietario
from app.models.contrato import Contrato
from app.models.inquilino import Inquilino
from app.models.cobro import Cobro
from app.core.deps import get_current_active_user

router = APIRouter()


@router.get("/inmuebles")
async def get_dashboard_inmuebles(
    skip: int = 0,
    limit: int = 200,
    estado: Optional[str] = Query(None, description="Filter: alquilado, disponible"),
    categoria: Optional[str] = Query(None, description="Filter: urbano, rural"),
    propietario: Optional[str] = Query(None, description="Filter by propietario name (contains)"),
    inmueble: Optional[str] = Query(None, description="Filter by inmueble address (contains)"),
    morosos: Optional[bool] = Query(None, description="Filter only morosos (overdue)"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Dashboard endpoint: returns all inmuebles with enriched data:
    - propietario(s) via copropiedad
    - contrato activo + inquilino (if alquilado)
    - morosidad flag (overdue payments)
    """

    # 1. Fetch all inmuebles with optional base filters
    stmt = select(Inmueble)
    if estado:
        stmt = stmt.where(Inmueble.estado == estado)
    if categoria:
        stmt = stmt.where(Inmueble.categoria == categoria)
    if inmueble:
        stmt = stmt.where(Inmueble.direccion.ilike(f"%{inmueble}%"))
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    inmuebles = list(result.scalars().all())

    if not inmuebles:
        return []

    inmueble_ids = [i.id for i in inmuebles]

    # 2. Fetch copropiedad + propietarios for all inmuebles
    coprop_stmt = (
        select(Copropiedad)
        .where(Copropiedad.inmueble_id.in_(inmueble_ids))
    )
    coprop_result = await db.execute(coprop_stmt)
    copropiedades = list(coprop_result.scalars().all())

    propietario_ids = list(set(c.propietario_id for c in copropiedades))
    prop_map: dict = {}
    if propietario_ids:
        prop_stmt = select(Propietario).where(Propietario.id.in_(propietario_ids))
        prop_result = await db.execute(prop_stmt)
        for p in prop_result.scalars().all():
            prop_map[p.id] = p

    # Build inmueble -> propietarios mapping
    inm_prop_map: dict = {}
    for c in copropiedades:
        inm_prop_map.setdefault(c.inmueble_id, []).append(
            {
                "id": c.propietario_id,
                "nombre": prop_map[c.propietario_id].nombre if c.propietario_id in prop_map else "Desconocido",
                "dni_cuit": prop_map[c.propietario_id].dni_cuit if c.propietario_id in propietario_ids else "",
                "porcentaje_participacion": c.porcentaje_participacion,
            }
        )

    # 3. Fetch active contratos for all inmuebles
    contrato_stmt = (
        select(Contrato)
        .where(Contrato.inmueble_id.in_(inmueble_ids), Contrato.activo == True)
    )
    contrato_result = await db.execute(contrato_stmt)
    contratos = list(contrato_result.scalars().all())

    inquilino_ids = list(set(c.inquilino_id for c in contratos))
    inq_map: dict = {}
    if inquilino_ids:
        inq_stmt = select(Inquilino).where(Inquilino.id.in_(inquilino_ids))
        inq_result = await db.execute(inq_stmt)
        for iq in inq_result.scalars().all():
            inq_map[iq.id] = iq

    contrato_map: dict = {}
    for c in contratos:
        contrato_map[c.inmueble_id] = c

    # 4. Fetch cobros for active contracts to determine morosidad
    contrato_ids = [c.id for c in contratos]
    moroso_set: set = set()

    if contrato_ids:
        cobro_stmt = select(Cobro).where(Cobro.contrato_id.in_(contrato_ids))
        cobro_result = await db.execute(cobro_stmt)
        cobros = list(cobro_result.scalars().all())

        today = date.today()
        for contrato in contratos:
            # An inmueble is moroso if the contract is overdue (fecha_fin < today)
            # or if there are expected cobros missing
            if contrato.fecha_fin < today:
                moroso_set.add(contrato.inmueble_id)
            else:
                # Check if payment is overdue based on fecha_maxima_pago
                cobros_for_contrato = [cb for cb in cobros if cb.contrato_id == contrato.id]
                # Simple heuristic: if contract started more than 30 days ago and no cobros exist
                days_active = (today - contrato.fecha_inicio).days
                if days_active > 30 and len(cobros_for_contrato) == 0:
                    moroso_set.add(contrato.inmueble_id)

    # 5. Filter by propietario name (post-fetch filter)
    if propietario:
        prop_lower = propietario.lower()
        inmuebles = [
            i for i in inmuebles
            if any(prop_lower in p["nombre"].lower() for p in inm_prop_map.get(i.id, []))
        ]

    # 6. Filter by morosos (post-fetch filter)
    if morosos is True:
        inmuebles = [i for i in inmuebles if i.id in moroso_set]
    elif morosos is False:
        inmuebles = [i for i in inmuebles if i.id not in moroso_set]

    # 7. Build response
    response = []
    for inmueble in inmuebles:
        contrato = contrato_map.get(inmueble.id)
        contrato_data = None
        inquilino_data = None

        if contrato:
            inq = inq_map.get(contrato.inquilino_id)
            inquilino_data = (
                {
                    "id": inq.id,
                    "nombre": inq.nombre,
                    "dni": inq.dni,
                    "telefono": inq.telefono,
                    "email": inq.email,
                }
                if inq
                else None
            )
            contrato_data = {
                "id": contrato.id,
                "fecha_inicio": str(contrato.fecha_inicio),
                "fecha_fin": str(contrato.fecha_fin),
                "fecha_maxima_pago": contrato.fecha_maxima_pago,
                "modalidad_pago": contrato.modalidad_pago,
                "frecuencia": contrato.frecuencia,
                "monto_base": contrato.monto_base,
                "moneda": contrato.moneda,
            }

        response.append(
            {
                "id": inmueble.id,
                "direccion": inmueble.direccion,
                "categoria": inmueble.categoria,
                "superficie": inmueble.superficie,
                "habitaciones": inmueble.habitaciones,
                "banos": inmueble.banos,
                "dormitorios": inmueble.dormitorios,
                "comodidades": inmueble.comodidades,
                "descripcion": inmueble.descripcion,
                "estado": inmueble.estado,
                "created_at": str(inmueble.created_at) if inmueble.created_at else None,
                "propietarios": inm_prop_map.get(inmueble.id, []),
                "contrato": contrato_data,
                "inquilino": inquilino_data,
                "moroso": inmueble.id in moroso_set,
            }
        )

    return response
