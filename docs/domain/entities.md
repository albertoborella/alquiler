# Entidades — Alquiler

## Inmueble

| Atributo | Tipo | Obligatorio | Descripción |
| -------- | ---- | ----------- | ----------- |
| `id` | VARCHAR(36) | sí | Identificador único (UUID como texto) |
| `direccion` | string | sí | Dirección o ubicación del inmueble |
| `categoria` | enum | sí | `urbano` \| `rural` |
| `superficie` | decimal | no | Superficie; unidad según categoría (**m²** urbano / **ha** rural) |
| `habitaciones` | int | no | Cantidad de habitaciones (solo urbano) |
| `banos` | int | no | Cantidad de baños (solo urbano) |
| `dormitorios` | int | no | Cantidad de dormitorios (solo urbano) |
| `comodidades` | text | no | Lista de comodidades (solo urbano) |
| `descripcion` | text | no | Descripción libre del inmueble |
| `estado` | enum | sí | `disponible` \| `alquilado` (almacenado, se actualiza con triggers) |

---

## Propietario

| Atributo | Tipo | Obligatorio | Descripción |
| -------- | ---- | ----------- | ----------- |
| `id` | VARCHAR(36) | sí | Identificador único (UUID como texto) |
| `nombre` | string | sí | Nombre completo o razón social |
| `dni_cuit` | string | sí | DNI, CUIT o equivalente |
| `telefono` | string | no | Teléfono de contacto |
| `email` | string | no | Correo electrónico de contacto |
| `direccion` | string | no | Dirección personal |

---

## Copropiedad (Inmueble ↔ Propietario)

| Atributo | Tipo | Obligatorio | Descripción |
| -------- | ---- | ----------- | ----------- |
| `id` | VARCHAR(36) | sí | Identificador único (UUID como texto) |
| `inmueble_id` | FK → Inmueble | sí | Inmueble |
| `propietario_id` | FK → Propietario | sí | Copropietario |
| `porcentaje_participacion` | decimal(5,2) | sí | Porcentaje de participación (ej: 50.00) |

**Regla de integridad:** La suma de `porcentaje_participacion` de todos los propietarios
de un inmueble debe ser exactamente 100.00. Se valida en la capa de aplicación.

**Restricción UNIQUE:** Un propietario no puede tener dos registros de
participación en el mismo inmueble.

**Asignación al crear:** Al dar de alta un inmueble se pueden asignar sus
propietarios y porcentajes en la misma operación (existentes o creados al vuelo),
de forma atómica en el backend.

---

## Inquilino

| Atributo | Tipo | Obligatorio | Descripción |
| -------- | ---- | ----------- | ----------- |
| `id` | VARCHAR(36) | sí | Identificador único (UUID como texto) |
| `nombre` | string | sí | Nombre completo |
| `cuit` | string | sí* | CUIT (obligatorio en la app; nullable en DB para empezar limpio) |
| `iva` | enum | no | `Monotributo` \| `Resp. inscripto` \| `Exento` |
| `telefono` | string | no | Teléfono de contacto |
| `email` | string | no | Correo electrónico de contacto |
| `direccion` | string | no | Dirección personal |

---

## Contrato

| Atributo | Tipo | Obligatorio | Descripcion |
| -------- | ---- | ----------- | ----------- |
| `id` | VARCHAR(36) | si | Identificador unico (UUID como texto) |
| `inmueble_id` | FK -> Inmueble | si | Inmueble alquilado |
| `inquilino_id` | FK -> Inquilino | si | Quien alquila |
| `fecha_inicio` | date | si | Fecha de inicio del contrato |
| `fecha_fin` | date | si | Fecha de finalizacion del contrato |
| `fecha_maxima_pago` | int | si | Dia del mes como limite de pago (ej: 10) |
| `modalidad_pago` | enum | si | `pesos_indice` \| `moneda_extranjera` \| `producto_agropecuario` |
| `frecuencia` | enum | si | `mensual` \| `trimestral` \| `anual` \| `vencimiento` |
| `monto_base` | decimal | no | Monto base del alquiler (urbano) |
| `moneda` | string | no | Moneda (default: ARS) |
| `indice` | string | no | Indice de actualizacion (ej: ICL, IPC) |
| `periodo_indexacion` | string | no | Periodo de actualizacion (ej: mensual, trimestral, anual) |
| `tipo_producto` | string | no | Tipo de producto agropecuario (rural) |
| `kilos` | decimal | no | Cantidad de kilos del producto (rural) |
| `precio_kilo` | decimal | no | Precio unitario por kilo (rural) |
| `fuente_precio_agro` | string | no | Fuente del precio para pagos agropecuarios |
| `activo` | boolean | si | Si el contrato esta vigente |

**Nota:** El contrato obtiene los propietarios del inmueble a traves de la tabla `copropiedad`.

**Modalidades de pago segun categoria:**
- **Urbano** (`pesos_indice` / `moneda_extranjera`): usa `monto_base`, `moneda`, `indice`, `periodo_indexacion`.
- **Rural** (`producto_agropecuario`): usa `tipo_producto`, `kilos`, `precio_kilo`.

---

## Cobro

| Atributo | Tipo | Obligatorio | Descripción |
| -------- | ---- | ----------- | ----------- |
| `id` | VARCHAR(36) | sí | Identificador único (UUID como texto) |
| `contrato_id` | FK → Contrato | sí | Contrato al que pertenece |
| `fecha_cobro` | date | sí | Fecha en que se efectuó el cobro |
| `monto` | decimal | sí | Monto total cobrado en pesos |
| `moneda_original` | string | no | Divisa original si fue pago en moneda extranjera |
| `monto_original` | decimal | no | Monto en la moneda original |
| `cotizacion` | decimal | no | Tipo de cambio utilizado |
| `fuente_precio` | string | no | Fuente del precio para pagos agropecuarios |
| `precio_producto` | decimal | no | Precio unitario del producto al momento del cobro |
| `observaciones` | text | no | Notas adicionales |

**Nota:** Un cobro genera **N comprobantes** (uno por propietario del inmueble).

---

## Comprobante

Documento que respalda un cobro para un propietario específico.

| Atributo | Tipo | Obligatorio | Descripción |
| -------- | ---- | ----------- | ----------- |
| `id` | VARCHAR(36) | sí | Identificador único (UUID como texto) |
| `cobro_id` | FK → Cobro | sí | Cobro al que respalda |
| `propietario_id` | FK → Propietario | sí | Propietario al que se factura/comproba |
| `tipo` | enum | sí | `expensas` \| `honorarios` \| `comprobante` |
| `numero` | string | no | Número del documento (ej: A-0001-00012345 o 00001234) |
| `descripcion` | text | no | Concepto o descripción |
| `monto_proporcional` | decimal | sí | Monto que le corresponde según su participación |
| `porcentaje_participacion` | decimal | sí | Porcentaje usado para el cálculo |
| `created_at` | timestamp | sí | Fecha de registro |

**Regla de negocio:** La suma de `monto_proporcional` de todos los comprobantes
de un mismo cobro debe ser igual al `monto` del cobro.

**Tipos de comprobante:**

| Tipo | Ejemplo de número | Uso |
| ---- | ----------------- | --- |
| `expensas` | A-0001-00012345 | Factura de expensas |
| `honorarios` | B-0001-00012345 | Factura de honorarios |
| `comprobante` | 00001234 | Comprobante secuencial |
