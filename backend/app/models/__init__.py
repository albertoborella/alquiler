from app.models.user import User, UserCreate, UserUpdate, UserPublic
from app.models.propietario import Propietario, PropietarioCreate, PropietarioUpdate, PropietarioPublic
from app.models.inquilino import Inquilino, InquilinoCreate, InquilinoUpdate, InquilinoPublic
from app.models.inmueble import Inmueble, InmuebleCreate, InmuebleUpdate, InmueblePublic
from app.models.copropiedad import Copropiedad, CopropiedadCreate, CopropiedadPublic
from app.models.contrato import Contrato, ContratoCreate, ContratoUpdate, ContratoPublic
from app.models.cobro import Cobro, CobroCreate, CobroUpdate, CobroPublic
from app.models.comprobante import Comprobante, ComprobanteCreate, ComprobanteUpdate, ComprobantePublic
from app.models.audit import AuditLog, AuditLogCreate, AuditLogPublic

__all__ = [
    # User
    "User", "UserCreate", "UserUpdate", "UserPublic",
    # Propietario
    "Propietario", "PropietarioCreate", "PropietarioUpdate", "PropietarioPublic",
    # Inquilino
    "Inquilino", "InquilinoCreate", "InquilinoUpdate", "InquilinoPublic",
    # Inmueble
    "Inmueble", "InmuebleCreate", "InmuebleUpdate", "InmueblePublic",
    # Copropiedad
    "Copropiedad", "CopropiedadCreate", "CopropiedadPublic",
    # Contrato
    "Contrato", "ContratoCreate", "ContratoUpdate", "ContratoPublic",
    # Cobro
    "Cobro", "CobroCreate", "CobroUpdate", "CobroPublic",
    # Comprobante
    "Comprobante", "ComprobanteCreate", "ComprobanteUpdate", "ComprobantePublic",
    # Audit
    "AuditLog", "AuditLogCreate", "AuditLogPublic",
]
