# Modelo de Dominio — Alquiler

## Conceptos Principales

El dominio de **Alquiler** gira en torno a la relación entre un **inmueble**,
sus **propietarios** (pueden ser varios, con distintas participaciones), un
**inquilino** y un **contrato** que formaliza la operación de alquiler con una
**modalidad de pago** específica.

```
Propietario ──N:M──▶ Inmueble  (con participación por propietario)
Inquilino   ──1:N──▶ Contrato
Inmueble    ──1:1──▶ Contrato (activo)
Contrato    ──1:N──▶ Cobro
Contrato    ──1:1──▶ ModalidadPago
Cobro       ──1:N──▶ Comprobante  (uno por propietario, monto proporcional)
```

## Entidades y Relaciones

### Inmueble
Un bien físico que se puede alquiler. Puede ser urbano o rural.

- Tiene **uno o varios propietarios** (relación N:M con participación por propietario).
- Tiene un **tag de estado**: alquilado o disponible.
- Si está alquilado, tiene un **contrato activo** con sus datos asociados.

### Propietario
Persona física o jurídica dueña de uno o varios inmuebles.

- Puede tener **múltiples inmuebles**.
- Puede ser **copropietario** de un inmueble junto con otros (sociedad, hermanos, etc.).
- Cada propietario tiene una **participación** porcentual en cada inmueble que posee.
- No interactúa con el sistema directamente (solo consulta futura).

### Copropiedad (tabla de unión Inmueble ↔ Propietario)
Relación N:M que registra qué propietarios poseen un inmueble y con qué
porcentaje de participación.

- **Inmueble**: el bien.
- **Propietario**: el copropietario.
- **Participación**: porcentaje que le corresponde (ej: 50%, 33.33%).
- La suma de participaciones de un inmueble debe ser 100%.

### Inquilino
Persona que alquila uno o varios inmuebles.

- Puede tener **múltiples contratos** (uno por inmueble alquilado).
- Cada contrato es independiente.

### Contrato
Acuerdo formal entre propietarios e inquilino para alquilar un inmueble.

- **Inmueble**: el bien alquilado (1:1 — un inmueble tiene un contrato activo a la vez).
- **Inquilino**: quien alquila.
- **Fecha de inicio** y **fecha de fin** del período de alquiler.
- **Fecha máxima de pago**: día límite para cada período de cobro (configurable por contrato).
- **Modalidad de pago**: cómo se cobra (pesos+índice, moneda extranjera, producto agropecuario).
- **Frecuencia de cobro**: mensual, trimestral, anual o al vencimiento/renovación.

**Nota:** El contrato no referencia a un único propietario. Los propietarios
se obtienen del inmueble a través de la tabla de copropiedad.

### ModalidadPago
Configuración del método de cobro de un contrato. Es un valor atómico
que puede ser uno de tres tipos:

**Tipo A — Pesos con índice:**
- Monto base en pesos.
- Índice de ajuste (IPC, ICL, costo construcción, etc.).

**Tipo B — Moneda extranjera:**
- Moneda (USD, EUR, etc.).
- Se preserva el monto original en esa moneda.
- Al registrarse el cobro, se ingresa la cotización del día y se calcula el monto en pesos.

**Tipo C — Producto agropecuario:**
- Cantidad por unidad de superficie (ej: 200 kg soja/ha).
- Producto (soja, novillo, etc.).
- Unidad de referencia (ha, etc.).
- **Fuente del precio**: de dónde se toma el precio de referencia (Bolsa de Cereales de Rosario, mercado ganadero X, etc.).

### Cobro
Registro de un pago efectivo recibido por un contrato.

- **Contrato**: al que pertenece.
- **Fecha de cobro**: cuándo se cobró.
- **Monto cobrado**: cuánto se cobró en pesos (monto total del período).
- **Moneda original** (opcional): si el pago fue en moneda extranjera, la divisa utilizada.
- **Monto original** (opcional): monto en la moneda original.
- **Cotización aplicada** (opcional): tipo de cambio utilizado para la conversión.
- **Fuente de precio** (opcional): para pagos agropecuarios, el precio de referencia utilizado.
- **Comprobantes**: genera uno o varios comprobantes, uno por cada propietario.

### Comprobante
Documento que respalda un cobro para un propietario específico. Cuando hay
un solo propietario, se genera un comprobante por el monto total. Cuando hay
varios propietarios (copropiedad), se genera **un comprobante por propietario**
con el monto proporcional a su participación.

- **Cobro**: al que pertenece.
- **Propietario**: a quién se le factura o comproba.
- **Tipo**: factura o comprobante simple.
- **Número**: número del documento.
- **Monto proporcional**: monto que le corresponde a este propietario según su participación.
- **Participación aplicada**: porcentaje que se usó para calcular el monto.

**Ejemplo:** Cobro de $100.000, propietario A (60%) y propietario B (40%):
- Comprobante A: factura A-0001 por $60.000
- Comprobante B: comprobante 00001 por $40.000

---

## Estados del Inmueble

```
 ┌─────────────┐    contrato creado    ┌─────────────┐
 │ Disponible  │ ────────────────────▶ │  Alquilado  │
 │             │ ◀──────────────────── │             │
 └─────────────┘    contrato finalizado└─────────────┘
```

El tag del inmueble se deriva del estado de sus contratos:
- Si tiene un contrato con fecha de inicio ≤ hoy ≤ fecha de fin → **alquilado**.
- En cualquier otro caso → **disponible**.
