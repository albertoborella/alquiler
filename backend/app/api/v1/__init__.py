from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.propietarios import router as propietarios_router
from app.api.v1.inquilinos import router as inquilinos_router
from app.api.v1.inmuebles import router as inmuebles_router
from app.api.v1.contratos import router as contratos_router
from app.api.v1.cobros import router as cobros_router
from app.api.v1.comprobantes import router as comprobantes_router
from app.api.v1.dashboard import router as dashboard_router

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, tags=["authentication"])
api_router.include_router(propietarios_router, prefix="/propietarios", tags=["propietarios"])
api_router.include_router(inquilinos_router, prefix="/inquilinos", tags=["inquilinos"])
api_router.include_router(inmuebles_router, prefix="/inmuebles", tags=["inmuebles"])
api_router.include_router(contratos_router, prefix="/contratos", tags=["contratos"])
api_router.include_router(cobros_router, prefix="/cobros", tags=["cobros"])
api_router.include_router(comprobantes_router, prefix="/comprobantes", tags=["comprobantes"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
