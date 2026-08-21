# Entidades — Alquiler

## Inmueble

| Atributo | Tipo | Obligatorio | Descripción |
| -------- | ---- | ----------- | ----------- |
| `id` | UUID | sí | Identificador único |
| `tipo` | enum | sí | `urbano` \| `rural` |
| `direccion` | string | sí | Dirección o ubicación del inmueble |
| `descripcion` | text | no | Descripción libre del inmueble |
| `caracteristicas` | text | no | Detalles relevantes (superficie, ambientes, etc.) |
| `estado` | enum | sí | `disponible` \| `alquilado` (calculado, no almacenado) |

**Nota:** El `estado` se calcula a partir de los contratos asociados, no se
almacena como campo persistente.

---

## Propietario

| Atributo | Tipo | Obligatorio | Descripción |
| -------- | ---- | ----------- | ----------- |
| `id` | UUID | sí | Identificador único |
| `nombre` | string | sí | Nombre completo o razón social |
| `documento` | string | sí | DNI, CUIT o equivalente |
| `telefono` | string | no | Teléfono de contacto |
| `email` | string | no | Correo electrónico de contacto |
| `direccion` | string | no | Dirección personal |

---

## Copropiedad (Inmueble ↔ Propietario)

| Atributo | Tipo | Obligatorio | Descripción |
| -------- | ---- | ----------- | ----------- |
| `id` | UUID | sí | Identificador único |
| `inmueble_id` | FK → Inmueble | sí | Inmueble |
| `propietario_id` | FK → Propietario | sí | Copropietario |
| `participacion` | decimal(5,2) | sí | Porcentaje de participación (ej: 50.00) |

**Regla de integridad:** La suma de `participacion` de todos los propietarios
de un inmueble debe ser exactamente 100.00. Se valida en la capa de aplicación.

**Restricción UNIQUE:** Un propietario no puede tener dos registros de
participación en el mismo inmueble.

---

## Inquilino

| Atributo | Tipo | Obligatorio | Descripción |
| -------- | ---- | ----------- | ----------- |
| `id` | UUID | sí | Identificador único |
| `nombre` | string | sí | Nombre completo |
| `documento` | string | sí | DNI o equivalente |
| `telefono` | string | no | Teléfono de contacto |
| `email` | string | no | Correo electrónico de contacto |
| `direccion` | string | no | Dirección personal |

---

## Contrato

| Atributo | Tipo | Obligatorio | Descripción |
| -------- | ---- | ----------- | ----------- |
| `id` | UUID | sí | Identificador único |
| `inmueble_id` | FK → Inmueble | sí | Inmueble alquilado |
| `inquilino_id` | FK → Inquilino | sí | Quién alquila |
| `fecha_inicio` | date | sí | Fecha de inicio del contrato |
| `fecha_fin` | date | sí | Fecha de finalización del contrato |
| `fecha_max_pago` | int | sí | Día del mes como límite de pago (ej: 10) |
| `frecuencia` | enum | sí | `mensual` \| `trimestral` \| `anual` \| `vencimiento` |
| `modalidad_pago` | JSON | sí | Ver ModalidadPago abajo |

**Nota:** El contrato NO referencia directamente a propietarios. Los
propietarios se obtienen del inmueble a través de la tabla `copropiedad`.

---

## ModalidadPago (JSON embebido en Contrato)

El tipo de modalidad se identifica por el campo `tipo`:

### Tipo A — Pesos con Índice

```json
{
  "tipo": "pesos_indice",
  "monto_base": 150000,
  "indice": "ICL"
}
```

### Tipo B — Moneda Extranjera

```json
{
  "tipo": "moneda_extranjera",
  "moneda": "USD",
  "monto_original": 500
}
```

### Tipo C — Producto Agropecuario

```json
{
  "tipo": "producto_agropecuario",
  "producto": "soja",
  "cantidad": 200,
  "unidad": "kg/ha",
  "fuente_precio": "Bolsa de Cereales de Rosario"
}
```

---

## Cobro

| Atributo | Tipo | Obligatorio | Descripción |
| -------- | ---- | ----------- | ----------- |
| `id` | UUID | sí | Identificador único |
| `contrato_id` | FK → Contrato | sí | Contrato al que pertenece |
| `fecha_cobro` | date | sí | Fecha en que se efectuó el cobro |
| `monto_cobrado` | decimal | sí | Monto total cobrado en pesos |
| `moneda_original` | string | no | Divisa original si fue pago en moneda extranjera |
| `monto_original` | decimal | no | Monto en la moneda original |
| `cotizacion_aplicada` | decimal | no | Tipo de cambio utilizado |
| `fuente_precio` | string | no | Fuente del precio para pagos agropecuarios |
| `precio_producto` | decimal | no | Precio unitario del producto al momento del cobro |

**Nota:** Un cobro genera **N comprobantes** (uno por propietario del inmueble).

---

## Comprobante

Documento que respalda un cobro para un propietario específico.

| Atributo | Tipo | Obligatorio | Descripción |
| -------- | ---- | ----------- | ----------- |
| `id` | UUID | sí | Identificador único |
| `cobro_id` | FK → Cobro | sí | Cobro al que respalda |
| `propietario_id` | FK → Propietario | sí | Propietario al que se factura/comproba |
| `tipo` | enum | sí | `factura` \| `comprobante` |
| `numero` | string | sí | Número del documento (ej: A-0001-00012345 o 00001234) |
| `monto_proporcional` | decimal | sí | Monto que le corresponde según su participación |
| `participacion_aplicada` | decimal | sí | Porcentaje usado para el cálculo |
| `descripcion` | string | no | Concepto o descripción |
| `created_at` | timestamp | sí | Fecha de registro |

**Regla de negocio:** La suma de `monto_proporcional` de todos los comprobantes
de un mismo cobro debe ser igual al `monto_cobrado` del cobro.

**Tipos de comprobante:**

| Tipo | Ejemplo de número | Uso |
| ---- | ----------------- | --- |
| `factura` | A-0001-00012345 | Factura fiscal (A, B, C, etc.) |
| `comprobante` | 00001234 | Comprobante secuencial sin valor fiscal |
