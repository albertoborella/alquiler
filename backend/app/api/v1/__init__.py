from fastapi import APIRouter
from app.api.v1.configuracion import router as configuracion_router
from app.api.v1.auth import router as auth_router
from app.api.v1.personas import router as personas_router
from app.api.v1.inmuebles import router as inmuebles_router
from app.api.v1.contratos import router as contratos_router
from app.api.v1.cobros import router as cobros_router
from app.api.v1.comprobantes import router as comprobantes_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.informes import router as informes_router
from app.api.v1.notifications import router as notifications_router

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, tags=["authentication"])
api_router.include_router(personas_router, prefix="/personas", tags=["personas"])
api_router.include_router(inmuebles_router, prefix="/inmuebles", tags=["inmuebles"])
api_router.include_router(contratos_router, prefix="/contratos", tags=["contratos"])
api_router.include_router(cobros_router, prefix="/cobros", tags=["cobros"])
api_router.include_router(comprobantes_router, prefix="/comprobantes", tags=["comprobantes"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(configuracion_router, tags=["configuracion"])
api_router.include_router(informes_router, prefix="/informes", tags=["informes"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
