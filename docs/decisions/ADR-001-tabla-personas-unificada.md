# ADR-001: Tabla Personas Unificada

## Título

Unificar tablas `propietarios` e `inquilinos` en una sola tabla `personas` con campo de roles.

## Contexto

El sistema de alquileres tenía dos tablas separadas: `propietarios` (para dueños de inmuebles) y `inquilinos` (para arrendatarios). Esto generaba un problema de diseño: una misma persona podía ser propietaria de algunos inmuebles e inquilina de otros, y debía cargarse dos veces con datos duplicados.

Additionally, each table had slightly different fields:
- `propietarios`: `dni_cuit` (required), no `iva`
- `inquilinos`: `cuit` (optional), `iva` field

## Decisión

Crear una tabla unificada `personas` con un campo `rol` que indica si la persona es propietario, inquilino o ambos. El campo `dni_cuit` de propietarios y `cuit` de inquilinos se unifican como `cuit` (requerido, único).

### Esquema resultante

```sql
CREATE TABLE personas (
    id VARCHAR(36) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    cuit VARCHAR(20) UNIQUE NOT NULL,
    iva VARCHAR(50),
    telefono VARCHAR(50),
    email VARCHAR(255),
    direccion VARCHAR(500),
    rol VARCHAR(20) NOT NULL DEFAULT 'propietario',  -- propietario, inquilino, ambos
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Valores de `rol`

| Valor | Significado |
|-------|-------------|
| `propietario` | Solo es dueño de inmuebles |
| `inquilino` | Solo alquila inmuebles |
| `ambos` | Es propietario de algunos inmuebles e inquilino de otros |

## Alternativas descartadas

### 1. Tablas separadas con campo `persona_id` compartido
- Mantener `propietarios` e `inquilinos` pero agregar un `persona_id` común
- **Descartado**: Complejidad innecesaria, requiere joins cross-table para cualquier consulta

### 2. Tabla pivote `persona_tipo` con relación M:N
- Tabla `personas` + tabla `persona_roles` con los roles
- **Descartado**: Over-engineering para un caso de uso simple (3 valores posibles)

### 3. No hacer nada (duplicar personas)
- Mantener la carga duplicada
- **Descartado**: Mala experiencia de usuario, riesgo de inconsistencias

## Consecuencias

### Positivas
- **Carga única**: una persona se carga una sola vez con su rol
- **Consistencia**: no hay datos duplicados entre tablas
- **Simplificación**: una tabla, un CRUD, un formulario unificado
- **Flexibilidad**: una persona puede cambiar de rol sin recrear registros

### Negativas
- **Migración**: requiere migrar datos existentes y actualizar foreign keys
- **Complejidad del formulario**: el campo `rol` agrega un paso más al alta
- **Foreign keys**: `copropiedad`, `contratos` y `comprobantes` apuntan a la misma tabla

### Neutral
- Los endpoints `/api/propietarios/` y `/api/inquilinos/` se reemplazan por `/api/personas/propietarios` y `/api/personas/inquilinos`
- Las rutas del frontend `/propietarios` y `/inquilinos` redirigen a `/personas`

## Archivos afectados

### Base de datos
- `db/init.sql` - Esquema actualizado
- `db/migrate_personas.sql` - Script de migración para BD existente

### Backend
- `backend/app/models/persona.py` - Nuevo modelo unificado
- `backend/app/crud/persona.py` - CRUD unificado
- `backend/app/api/v1/personas.py` - API unificada
- `backend/app/models/copropiedad.py` - FK actualizada
- `backend/app/models/contrato.py` - FK actualizada
- `backend/app/models/comprobante.py` - FK actualizada
- `backend/app/models/inmueble.py` - Relación actualizada
- `backend/app/crud/inmueble.py` - Usa persona CRUD
- `backend/app/api/v1/inmuebles.py` - Imports actualizados
- `backend/app/api/v1/dashboard.py` - Queries actualizadas

### Frontend
- `frontend/src/lib/api.ts` - Tipos y métodos actualizados
- `frontend/src/lib/components/Sidebar.svelte` - Navegación unificada
- `frontend/src/routes/personas/+page.svelte` - Nueva página unificada
- `frontend/src/routes/propietarios/+page.svelte` - Redirect a /personas
- `frontend/src/routes/inquilinos/+page.svelte` - Redirect a /personas
- `frontend/src/routes/contratos/+page.svelte` - Tipos actualizados
- `frontend/src/routes/inmuebles/+page.svelte` - Tipos actualizados
- `frontend/src/routes/inmuebles/rural/+page.svelte` - Tipos actualizados
