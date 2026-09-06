# Guía de Migración: Propietarios + Inquilinos → Personas Unificada

## Resumen

Este documento describe cómo migrar una base de datos existente con tablas `propietarios` e `inquilinos` separadas hacia la nueva tabla unificada `personas`.

## Prerequisitos

- PostgreSQL ejecutándose con la base de datos del sistema
- Backup completo de la base de datos antes de ejecutar la migración
- Las tablas `propietarios`, `inquilinos`, `copropiedad`, `contratos` y `comprobantes` deben existir

## Paso 1: Backup

```bash
pg_dump -U usuario -d alquiler > backup_pre_migracion.sql
```

## Paso 2: Ejecutar migración

```bash
psql -U usuario -d alquiler -f db/migrate_personas.sql
```

### Qué hace la migración

1. **Crea la tabla `personas`** con los campos unificados
2. ** Migra propietarios** → personas con `rol='propietario'`
3. ** Migra inquilinos**:
   - Si el CUIT ya existe en personas (era propietario e inquilino) → actualiza a `rol='ambos'` y mergea el IVA
   - Si el CUIT no existe → inserta como `rol='inquilino'`
4. **Agrega columnas FK temporales** en `copropiedad`, `contratos`, `comprobantes`
5. **Actualiza las referencias FK** usando el CUIT como clave de mapeo
6. **Elimina las columnas FK viejas** y renombra las nuevas
7. **Elimina las tablas `propietarios` e `inquilinos`**
8. **Crea índices y triggers** para la nueva tabla

## Paso 3: Verificar

```sql
-- Verificar que la tabla personas tiene datos
SELECT COUNT(*) FROM personas;

-- Verificar distribución de roles
SELECT rol, COUNT(*) FROM personas GROUP BY rol;

-- Verificar que las foreign keys apuntan correctamente
SELECT c.id, p.nombre, p.cuit 
FROM copropiedad c 
JOIN personas p ON c.propietario_id = p.id;

SELECT co.id, p.nombre, p.cuit 
FROM contratos co 
JOIN personas p ON co.inquilino_id = p.id;
```

## Paso 4: Reiniciar backend

El backend ya está configurado para usar la nueva tabla. Reiniciá el servicio:

```bash
# Si usa docker/podman
podman-compose restart backend

# Si corre directamente
cd backend && uvicorn app.main:app --reload
```

## Troubleshooting

### Error: "relation 'personas' does not exist"
La migración no se ejecutó. Correr el paso 2.

### Error: "foreign key constraint fails"
Verificar que los CUIT en `propietarios` e `inquilinos` sean consistentes. Si hay duplicados por CUIT, la migración los maneja automáticamente (mergea a 'ambos').

### Error: "column 'dni_cuit' does not exist"
El backend viejo está corriendo contra el esquema nuevo. Reiniciar el backend.

## API Reference

### Endpoints nuevos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/personas/` | Listar todas (filtro ?rol=) |
| GET | `/api/personas/propietarios` | Solo propietarios (rol=propietario\|ambos) |
| GET | `/api/personas/inquilinos` | Solo inquilinos (rol=inquilino\|ambos) |
| GET | `/api/personas/{id}` | Obtener una persona |
| POST | `/api/personas/` | Crear persona |
| PUT | `/api/personas/{id}` | Actualizar persona |
| DELETE | `/api/personas/{id}` | Eliminar persona |

### Endpoints eliminados

| Método | Ruta | Reemplazo |
|--------|------|-----------|
| GET | `/api/propietarios/` | `/api/personas/propietarios` |
| POST | `/api/propietarios/` | `/api/personas/` (con rol=propietario) |
| GET | `/api/inquilinos/` | `/api/personas/inquilinos` |
| POST | `/api/inquilinos/` | `/api/personas/` (con rol=inquilino) |

### Campos de Persona

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| id | string (UUID) | auto | Identificador único |
| nombre | string | sí | Nombre completo |
| cuit | string | sí | CUIT (único) |
| iva | string | no | Condición IVA (Monotributo, Resp. inscripto, Exento) |
| telefono | string | no | Teléfono de contacto |
| email | string | no | Email de contacto |
| direccion | string | no | Dirección personal |
| rol | string | sí | propietario, inquilino, ambos |
| created_at | datetime | auto | Fecha de creación |
| updated_at | datetime | auto | Fecha de última modificación |
