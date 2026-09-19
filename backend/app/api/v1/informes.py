from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date

from app.db.session import get_db
from app.models.cobro import Cobro
from app.models.contrato import Contrato
from app.models.inmueble import Inmueble
from app.models.copropiedad import Copropiedad
from app.models.persona import Persona
from app.models.configuracion import Configuracion
from app.core.deps import get_current_active_user

router = APIRouter()


@router.get("/propietarios")
async def informe_propietarios(
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicio del período"),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin del período"),
    propietario_id: Optional[str] = Query(None, description="Filtrar por propietario específico"),
    inmueble_id: Optional[str] = Query(None, description="Filtrar por inmueble (vista mensual)"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Informe de propietarios con descuento de costo de administración.

    Sin inmueble_id: agrupa por propietario (vista general).
    Con inmueble_id: agrupa por mes con columnas por propietario (vista pivot).
    """
    # 1. Obtener porcentajes de admin desde configuración
    config_result = await db.execute(select(Configuracion))
    config_map = {c.key: c.value for c in config_result.scalars().all()}
    costo_admin_urbano = float(config_map.get("costo_admin_urbano", "5"))
    costo_admin_rural = float(config_map.get("costo_admin_rural", "3"))

    # 2. Obtener todos los cobros con sus contratos e inmuebles
    stmt = (
        select(Cobro, Contrato, Inmueble)
        .join(Contrato, Cobro.contrato_id == Contrato.id)
        .join(Inmueble, Contrato.inmueble_id == Inmueble.id)
    )
    if fecha_inicio:
        stmt = stmt.where(Cobro.fecha_cobro >= fecha_inicio)
    if fecha_fin:
        stmt = stmt.where(Cobro.fecha_cobro <= fecha_fin)
    if inmueble_id:
        stmt = stmt.where(Inmueble.id == inmueble_id)

    result = await db.execute(stmt)
    cobros_data = result.all()

    # 3. Obtener copropiedades (propietarios por inmueble)
    copro_stmt = select(Copropiedad)
    copro_result = await db.execute(copro_stmt)
    copropiedades = copro_result.scalars().all()

    # Mapear inmueble -> propietarios con su porcentaje
    inmueble_prop_map = {}
    propietario_ids = set()
    for c in copropiedades:
        if c.inmueble_id not in inmueble_prop_map:
            inmueble_prop_map[c.inmueble_id] = []
        inmueble_prop_map[c.inmueble_id].append({
            "propietario_id": c.propietario_id,
            "porcentaje": c.porcentaje_participacion
        })
        propietario_ids.add(c.propietario_id)

    # 4. Obtener datos de propietarios
    if propietario_ids:
        prop_stmt = select(Persona).where(Persona.id.in_(propietario_ids))
        prop_result = await db.execute(prop_stmt)
        prop_map = {p.id: p for p in prop_result.scalars().all()}
    else:
        prop_map = {}

    # ── MODO PIVOT: filtrado por inmueble ──────────────────
    if inmueble_id:
        return _build_pivot_informe(
            cobros_data, inmueble_prop_map, prop_map,
            inmueble_id, costo_admin_urbano, costo_admin_rural
        )

    # ── MODO GENERAL: agrupado por propietario ─────────────
    return _build_general_informe(
        cobros_data, inmueble_prop_map, prop_map,
        propietario_id, costo_admin_urbano, costo_admin_rural
    )


def _build_pivot_informe(
    cobros_data, inmueble_prop_map, prop_map,
    inmueble_id, costo_admin_urbano, costo_admin_rural
):
    """Vista pivot: filas = meses, columnas = propietarios + admin + total."""
    propietarios = inmueble_prop_map.get(inmueble_id, [])
    prop_order = [p["propietario_id"] for p in propietarios]
    prop_pct = {p["propietario_id"]: p["porcentaje"] for p in propietarios}

    # Construir lista de propietarios con datos
    prop_columns = []
    for prop_id in prop_order:
        prop_data = prop_map.get(prop_id)
        prop_columns.append({
            "propietario_id": prop_id,
            "nombre": prop_data.nombre if prop_data else "Sin propietario",
            "cuit": prop_data.cuit if prop_data else "",
            "porcentaje": prop_pct[prop_id],
        })

    # Agrupar por mes (YYYY-MM)
    meses = {}
    for cobro, contrato, inmueble in cobros_data:
        es_rural = inmueble.categoria == "rural"
        porcentaje_admin = costo_admin_rural if es_rural else costo_admin_urbano
        costo_admin_total = cobro.monto * (porcentaje_admin / 100)
        mes_key = cobro.fecha_cobro.strftime("%Y-%m")
        mes_label = cobro.fecha_cobro.strftime("%m/%Y")

        if mes_key not in meses:
            meses[mes_key] = {
                "mes_key": mes_key,
                "mes_label": mes_label,
                "prop_montos": {pid: {"bruto": 0, "admin": 0, "neto": 0} for pid in prop_order},
                "total_admin": 0,
                "total_bruto": 0,
                "total_neto": 0,
            }

        for prop_id in prop_order:
            factor = prop_pct[prop_id] / 100
            bruto = cobro.monto * factor
            admin = costo_admin_total * factor
            neto = bruto - admin

            meses[mes_key]["prop_montos"][prop_id]["bruto"] += bruto
            meses[mes_key]["prop_montos"][prop_id]["admin"] += admin
            meses[mes_key]["prop_montos"][prop_id]["neto"] += neto
            meses[mes_key]["total_bruto"] += bruto
            meses[mes_key]["total_admin"] += admin
            meses[mes_key]["total_neto"] += neto

    # Ordenar meses cronológicamente y redondear
    filas = sorted(meses.values(), key=lambda m: m["mes_key"])
    for fila in filas:
        for pid in prop_order:
            fila["prop_montos"][pid]["bruto"] = round(fila["prop_montos"][pid]["bruto"], 2)
            fila["prop_montos"][pid]["admin"] = round(fila["prop_montos"][pid]["admin"], 2)
            fila["prop_montos"][pid]["neto"] = round(fila["prop_montos"][pid]["neto"], 2)
        fila["total_bruto"] = round(fila["total_bruto"], 2)
        fila["total_admin"] = round(fila["total_admin"], 2)
        fila["total_neto"] = round(fila["total_neto"], 2)

    # Totales del período
    totales = {
        "prop_montos": {pid: {"bruto": 0, "admin": 0, "neto": 0} for pid in prop_order},
        "total_bruto": 0,
        "total_admin": 0,
        "total_neto": 0,
    }
    for fila in filas:
        for pid in prop_order:
            totales["prop_montos"][pid]["bruto"] += fila["prop_montos"][pid]["bruto"]
            totales["prop_montos"][pid]["admin"] += fila["prop_montos"][pid]["admin"]
            totales["prop_montos"][pid]["neto"] += fila["prop_montos"][pid]["neto"]
        totales["total_bruto"] += fila["total_bruto"]
        totales["total_admin"] += fila["total_admin"]
        totales["total_neto"] += fila["total_neto"]

    # Redondear totales
    for pid in prop_order:
        totales["prop_montos"][pid]["bruto"] = round(totales["prop_montos"][pid]["bruto"], 2)
        totales["prop_montos"][pid]["admin"] = round(totales["prop_montos"][pid]["admin"], 2)
        totales["prop_montos"][pid]["neto"] = round(totales["prop_montos"][pid]["neto"], 2)
    totales["total_bruto"] = round(totales["total_bruto"], 2)
    totales["total_admin"] = round(totales["total_admin"], 2)
    totales["total_neto"] = round(totales["total_neto"], 2)

    return {
        "mode": "pivot",
        "costo_admin_urbano": costo_admin_urbano,
        "costo_admin_rural": costo_admin_rural,
        "propietarios": prop_columns,
        "meses": filas,
        "totales": totales,
    }


def _build_general_informe(
    cobros_data, inmueble_prop_map, prop_map,
    propietario_id, costo_admin_urbano, costo_admin_rural
):
    """Vista general: agrupado por propietario."""
    informe = {}
    for cobro, contrato, inmueble in cobros_data:
        es_rural = inmueble.categoria == "rural"
        porcentaje_admin = costo_admin_rural if es_rural else costo_admin_urbano
        costo_admin = cobro.monto * (porcentaje_admin / 100)
        monto_neto = cobro.monto - costo_admin

        propietarios = inmueble_prop_map.get(inmueble.id, [])
        if not propietarios:
            propietarios = [{"propietario_id": "sin_propietario", "porcentaje": 100}]

        for prop_info in propietarios:
            prop_id = prop_info["propietario_id"]
            porcentaje = prop_info["porcentaje"]
            factor = porcentaje / 100

            if prop_id not in informe:
                prop_data = prop_map.get(prop_id)
                informe[prop_id] = {
                    "propietario_id": prop_id,
                    "propietario_nombre": prop_data.nombre if prop_data else "Sin propietario",
                    "propietario_cuit": prop_data.cuit if prop_data else "",
                    "cobros": [],
                    "total_bruto": 0,
                    "total_admin": 0,
                    "total_neto": 0,
                }

            informe[prop_id]["cobros"].append({
                "id": cobro.id,
                "fecha_cobro": cobro.fecha_cobro.isoformat(),
                "monto_bruto": round(cobro.monto * factor, 2),
                "porcentaje_participacion": porcentaje,
                "porcentaje_admin": porcentaje_admin,
                "costo_admin": round(costo_admin * factor, 2),
                "monto_neto": round(monto_neto * factor, 2),
                "inmueble_direccion": inmueble.direccion,
                "inmueble_tipo": inmueble.categoria,
                "observaciones": cobro.observaciones,
            })
            informe[prop_id]["total_bruto"] += cobro.monto * factor
            informe[prop_id]["total_admin"] += costo_admin * factor
            informe[prop_id]["total_neto"] += monto_neto * factor

    for prop_id in informe:
        informe[prop_id]["total_bruto"] = round(informe[prop_id]["total_bruto"], 2)
        informe[prop_id]["total_admin"] = round(informe[prop_id]["total_admin"], 2)
        informe[prop_id]["total_neto"] = round(informe[prop_id]["total_neto"], 2)

    if propietario_id:
        informe = {k: v for k, v in informe.items() if k == propietario_id}

    return {
        "mode": "general",
        "costo_admin_urbano": costo_admin_urbano,
        "costo_admin_rural": costo_admin_rural,
        "propietarios": list(informe.values()),
    }
