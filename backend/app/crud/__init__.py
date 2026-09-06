from app.crud.configuracion import get_config, get_all_config, set_config
from app.crud.user import (
    get_user,
    get_user_by_email,
    get_users,
    create_user,
    update_user,
    delete_user,
    authenticate_user,
)
from app.crud.persona import (
    get_persona,
    get_persona_by_cuit,
    get_personas,
    get_propietarios,
    get_inquilinos,
    create_persona,
    update_persona,
    delete_persona,
)
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
from app.crud.contrato import (
    get_contrato,
    get_contratos_by_inmueble,
    get_contratos_by_inquilino,
    get_contratos,
    create_contrato,
    update_contrato,
    delete_contrato,
)
from app.crud.cobro import (
    get_cobro,
    get_cobros_by_contrato,
    get_cobros,
    create_cobro,
    update_cobro,
    delete_cobro,
)
from app.crud.comprobante import (
    get_comprobante,
    get_comprobantes_by_cobro,
    get_comprobantes_by_propietario,
    get_comprobantes,
    create_comprobante,
    update_comprobante,
    delete_comprobante,
)

__all__ = [
    # User
    "get_user", "get_user_by_email", "get_users", "create_user", "update_user", "delete_user", "authenticate_user",
    # Persona
    "get_persona", "get_persona_by_cuit", "get_personas", "get_propietarios", "get_inquilinos",
    "create_persona", "update_persona", "delete_persona",
    # Inmueble
    "get_inmueble", "get_inmuebles", "create_inmueble", "update_inmueble", "delete_inmueble",
    "get_copropiedad_by_inmueble", "add_propietario_to_inmueble", "remove_propietario_from_inmueble",
    # Contrato
    "get_contrato", "get_contratos_by_inmueble", "get_contratos_by_inquilino", "get_contratos",
    "create_contrato", "update_contrato", "delete_contrato",
    # Cobro
    "get_cobro", "get_cobros_by_contrato", "get_cobros", "create_cobro", "update_cobro", "delete_cobro",
    # Comprobante
    "get_comprobante", "get_comprobantes_by_cobro", "get_comprobantes_by_propietario", "get_comprobantes",
    "create_comprobante", "update_comprobante", "delete_comprobante",
    # Configuracion
    "get_config", "get_all_config", "set_config",
]
