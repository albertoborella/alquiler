# Modelo de Datos — Alquiler

Esquema físico para base de datos relacional (PostgreSQL).

---

## Diagrama ER (simplificado)

```
propietarios ──N:M──▶ inmuebles  (tabla copropiedad)
inquilinos   ──1:N──▶ contratos
inmuebles    ──1:1──▶ contratos (activo)
contratos    ──1:N──▶ cobros
cobros       ──1:N──▶ comprobantes  (uno por propietario)
```

---

## Tablas

### users

```sql
CREATE TABLE users (
    id              VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255),
    role            VARCHAR(50) NOT NULL DEFAULT 'empleado',
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);
```

### propietarios

```sql
CREATE TABLE propietarios (
    id            VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    nombre        VARCHAR(255) NOT NULL,
    dni_cuit      VARCHAR(20)  NOT NULL UNIQUE,
    telefono      VARCHAR(50),
    email         VARCHAR(255),
    direccion     VARCHAR(500),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ
);
```

### inquilinos

```sql
CREATE TABLE inquilinos (
    id            VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    nombre        VARCHAR(255) NOT NULL,
    dni           VARCHAR(20)  NOT NULL UNIQUE,
    telefono      VARCHAR(50),
    email         VARCHAR(255),
    direccion     VARCHAR(500),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ
);
```

### inmuebles

```sql
CREATE TABLE inmuebles (
    id              VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    direccion       VARCHAR(500) NOT NULL,
    categoria       VARCHAR(10)  NOT NULL DEFAULT 'urbano',
    superficie      DECIMAL(10,2),
    habitaciones    INTEGER,
    banos           INTEGER,
    dormitorios     INTEGER,
    comodidades     TEXT,
    descripcion     TEXT,
    estado          VARCHAR(15)  NOT NULL DEFAULT 'disponible',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);
```

### copropiedad (Inmueble ↔ Propietario)

```sql
CREATE TABLE copropiedad (
    id                      VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    propietario_id          VARCHAR(36) NOT NULL REFERENCES propietarios(id) ON DELETE RESTRICT,
    inmueble_id             VARCHAR(36) NOT NULL REFERENCES inmuebles(id) ON DELETE RESTRICT,
    porcentaje_participacion DECIMAL(5,2) NOT NULL DEFAULT 100.00,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(propietario_id, inmueble_id)
);
```

**Constraint de participación total:** La suma de `porcentaje_participacion` de todos los
registros de `copropiedad` para un mismo `inmueble_id` debe ser 100.00. Se
valida en la capa de aplicación (no es trivial con CHECK en PostgreSQL).

### contratos

```sql
CREATE TABLE contratos (
    id                  VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    inmueble_id         VARCHAR(36) NOT NULL REFERENCES inmuebles(id) ON DELETE RESTRICT,
    inquilino_id        VARCHAR(36) NOT NULL REFERENCES inquilinos(id) ON DELETE RESTRICT,
    fecha_inicio        DATE        NOT NULL,
    fecha_fin           DATE        NOT NULL,
    fecha_maxima_pago   INTEGER     NOT NULL DEFAULT 10,
    modalidad_pago      VARCHAR(30) NOT NULL,
    frecuencia          VARCHAR(15) NOT NULL DEFAULT 'mensual',
    monto_base          DECIMAL(12,2),
    moneda              VARCHAR(3)  DEFAULT 'ARS',
    indice              VARCHAR(50),
    fuente_precio_agro  VARCHAR(255),
    activo              BOOLEAN     DEFAULT true,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ
);
```

**Nota:** Los propietarios se obtienen del inmueble a través de `copropiedad`.

**Constraint de contrato activo:** Solo puede existir un contrato activo por
inmueble (solapamiento de fechas). Se valida en la capa de aplicación.

### cobros

```sql
CREATE TABLE cobros (
    id                VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    contrato_id       VARCHAR(36)    NOT NULL REFERENCES contratos(id) ON DELETE RESTRICT,
    fecha_cobro       DATE           NOT NULL,
    monto             DECIMAL(12,2)  NOT NULL,
    moneda_original   VARCHAR(3),
    monto_original    DECIMAL(12,2),
    cotizacion        DECIMAL(10,4),
    fuente_precio     VARCHAR(255),
    precio_producto   DECIMAL(12,2),
    observaciones     TEXT,
    created_at        TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ
);
```

### comprobantes

```sql
CREATE TABLE comprobantes (
    id                        VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    cobro_id                  VARCHAR(36) NOT NULL REFERENCES cobros(id) ON DELETE RESTRICT,
    propietario_id            VARCHAR(36) NOT NULL REFERENCES propietarios(id) ON DELETE RESTRICT,
    tipo                      VARCHAR(15) NOT NULL DEFAULT 'comprobante',
    numero                    VARCHAR(50),
    descripcion               TEXT,
    monto_proporcional        DECIMAL(12,2) NOT NULL,
    porcentaje_participacion  DECIMAL(5,2) NOT NULL,
    created_at                TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### audit_log

```sql
CREATE TABLE audit_log (
    id          SERIAL PRIMARY KEY,
    user_id     VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    action      VARCHAR(50) NOT NULL,
    table_name  VARCHAR(100) NOT NULL,
    record_id   VARCHAR(36),
    old_values  JSONB,
    new_values  JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## Enums y Valores

| Campo | Valores permitidos |
| ----- | ------------------ |
| `users.role` | `admin`, `empleado`, `contable` |
| `inmuebles.categoria` | `urbano`, `rural` |
| `inmuebles.estado` | `disponible`, `alquilado` |
| `contratos.modalidad_pago` | `pesos_indice`, `moneda_extranjera`, `producto_agropecuario` |
| `contratos.frecuencia` | `mensual`, `trimestral`, `anual`, `vencimiento` |
| `comprobantes.tipo` | `expensas`, `honorarios`, `comprobante` |

---

## Notas de Implementación

- **Estado del inmueble** se almacena como columna persistente y se actualiza
  con triggers o lógica de aplicación cuando se crea/modifica un contrato.
- **Un solo contrato activo por inmueble** se valida en aplicación, no en
  schema, por la complejidad de constraints de solapamiento temporal en SQL.
- **`modalidad_pago`** usa columnas separadas (monto_base, moneda, indice, etc.)
  para mejor queryabilidad y tipado.
- **Copropiedad** usa tabla de unión N:M con participación porcentual. La suma
  de 100% se valida en aplicación.
- **Comprobantes por propietario:** Un solo cobro genera N comprobantes (uno
  por propietario). La suma de `monto_proporcional` de los comprobantes de un
  cobro debe ser igual al `monto`. Se valida en aplicación.
- **Propietarios del contrato** se obtienen del inmueble vía copropiedad, no
  directamente del contrato.
