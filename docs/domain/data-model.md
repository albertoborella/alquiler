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

### propietarios

```sql
CREATE TABLE propietarios (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre        VARCHAR(200) NOT NULL,
    documento     VARCHAR(20)  NOT NULL UNIQUE,
    telefono      VARCHAR(30),
    email         VARCHAR(200),
    direccion     VARCHAR(300),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);
```

### inquilinos

```sql
CREATE TABLE inquilinos (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre        VARCHAR(200) NOT NULL,
    documento     VARCHAR(20)  NOT NULL UNIQUE,
    telefono      VARCHAR(30),
    email         VARCHAR(200),
    direccion     VARCHAR(300),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);
```

### inmuebles

```sql
CREATE TABLE inmuebles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo            VARCHAR(10)  NOT NULL CHECK (tipo IN ('urbano', 'rural')),
    direccion       VARCHAR(300) NOT NULL,
    descripcion     TEXT,
    caracteristicas TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);
```

### copropiedad (Inmueble ↔ Propietario)

```sql
CREATE TABLE copropiedad (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inmueble_id     UUID           NOT NULL REFERENCES inmuebles(id) ON DELETE CASCADE,
    propietario_id  UUID           NOT NULL REFERENCES propietarios(id),
    participacion   DECIMAL(5,2)   NOT NULL CHECK (participacion > 0 AND participacion <= 100),
    created_at      TIMESTAMPTZ    NOT NULL DEFAULT now(),

    UNIQUE (inmueble_id, propietario_id)
);

CREATE INDEX idx_copropiedad_inmueble    ON copropiedad(inmueble_id);
CREATE INDEX idx_copropiedad_propietario ON copropiedad(propietario_id);
```

**Constraint de participación total:** La suma de `participacion` de todos los
registros de `copropiedad` para un mismo `inmueble_id` debe ser 100.00. Se
valida en la capa de aplicación (no es trivial con CHECK en PostgreSQL).

### contratos

```sql
CREATE TABLE contratos (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inmueble_id       UUID        NOT NULL REFERENCES inmuebles(id),
    inquilino_id      UUID        NOT NULL REFERENCES inquilinos(id),
    fecha_inicio      DATE        NOT NULL,
    fecha_fin         DATE        NOT NULL,
    fecha_max_pago    INT         NOT NULL CHECK (fecha_max_pago BETWEEN 1 AND 31),
    frecuencia        VARCHAR(15) NOT NULL CHECK (frecuencia IN ('mensual', 'trimestral', 'anual', 'vencimiento')),
    modalidad_pago    JSONB       NOT NULL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),

    CHECK (fecha_fin > fecha_inicio)
);

CREATE INDEX idx_contratos_inmueble   ON contratos(inmueble_id);
CREATE INDEX idx_contratos_inquilino  ON contratos(inquilino_id);
```

**Nota:** Se eliminó `propietario_id` del contrato. Los propietarios se
obtienen del inmueble a través de `copropiedad`.

**Constraint de contrato activo:** Solo puede existir un contrato activo por
inmueble (solapamiento de fechas). Se valida en la capa de aplicación.

### cobros

```sql
CREATE TABLE cobros (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contrato_id           UUID           NOT NULL REFERENCES contratos(id),
    fecha_cobro           DATE           NOT NULL,
    monto_cobrado         DECIMAL(15,2)  NOT NULL,
    moneda_original       VARCHAR(5),
    monto_original        DECIMAL(15,2),
    cotizacion_aplicada   DECIMAL(15,4),
    fuente_precio         VARCHAR(200),
    precio_producto       DECIMAL(15,2),
    created_at            TIMESTAMPTZ    NOT NULL DEFAULT now()
);

CREATE INDEX idx_cobros_contrato ON cobros(contrato_id);
CREATE INDEX idx_cobros_fecha    ON cobros(fecha_cobro);
```

**Nota:** Se eliminó `comprobante_id` del cobro. Ahora la relación es
inversa: cada comprobante referencia a su cobro.

### comprobantes

```sql
CREATE TABLE comprobantes (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cobro_id                UUID           NOT NULL REFERENCES cobros(id),
    propietario_id          UUID           NOT NULL REFERENCES propietarios(id),
    tipo                    VARCHAR(15)    NOT NULL CHECK (tipo IN ('factura', 'comprobante')),
    numero                  VARCHAR(30)    NOT NULL,
    monto_proporcional      DECIMAL(15,2)  NOT NULL,
    participacion_aplicada  DECIMAL(5,2)   NOT NULL,
    descripcion             TEXT,
    created_at              TIMESTAMPTZ    NOT NULL DEFAULT now()
);

CREATE INDEX idx_comprobantes_cobro       ON comprobantes(cobro_id);
CREATE INDEX idx_comprobantes_propietario ON comprobantes(propietario_id);
CREATE INDEX idx_comprobantes_tipo        ON comprobantes(tipo);
```

---

## Enums y Valores

| Campo | Valores permitidos |
| ----- | ------------------ |
| `inmuebles.tipo` | `urbano`, `rural` |
| `contratos.frecuencia` | `mensual`, `trimestral`, `anual`, `vencimiento` |
| `contratos.modalidad_pago.tipo` | `pesos_indice`, `moneda_extranjera`, `producto_agropecuario` |
| `comprobantes.tipo` | `factura`, `comprobante` |

---

## Notas de Implementación

- **Estado del inmueble** no se almacena: se calcula consultando `contratos`
  donde `fecha_inicio <= hoy <= fecha_fin`.
- **Un solo contrato activo por inmueble** se valida en aplicación, no en
  schema, por la complejidad de constraints de solapamiento temporal en SQL.
- **`modalidad_pago`** es JSONB para flexibilidad: cada tipo tiene su estructura
  interna, validada en la capa de aplicación.
- **Copropiedad** usa tabla de unión N:M con participación porcentual. La suma
  de 100% se valida en aplicación.
- **Comprobantes por propietario:** Un solo cobro genera N comprobantes (uno
  por propietario). La suma de `monto_proporcional` de los comprobantes de un
  cobro debe ser igual al `monto_cobrado`. Se valida en aplicación.
- **Unicidad de número de comprobante:** El par `(tipo, numero)` podría ser
  UNIQUE si los números son secuenciales por tipo. Depende de la regla de
  negocio (facturas y comprobantes tienen numeraciones independientes).
