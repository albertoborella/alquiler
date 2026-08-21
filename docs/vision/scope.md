# Alcance del Proyecto

## Qué se incluye (In Scope)

### Gestión de Inmuebles
- Alta, baja y edición de inmuebles.
- Categoría: **urbano** o **rural** (campos rurales para alquiler).
- Tag de estado: **alquilado** o **disponible**.
- Datos del inmueble: dirección, descripción, características relevantes.

### Gestión de Propietarios
- Registro de propietarios de inmuebles.
- Un propietario puede tener **uno o varios** inmuebles.

### Gestión de Inquilinos
- Registro de inquilinos.
- Un inquilino puede alquilar **uno o varios** inmuebles (contratos independientes).

### Gestión de Contratos
- Creación de contrato con: inmueble, propietario, inquilino, fecha de inicio, fecha de fin.
- **Fecha máxima de pago** por contrato (configurable, ej: primeros 10 días de cada mes).
- **Modalidad de pago** por contrato (ver abajo).
- Cada contrato tiene una lista de cobros asociados.

### Modalidades de Pago

El sistema soporta múltiples modalidades de cobro, configurables por contrato:

| Modalidad | Descripción | Ejemplo |
| --------- | ----------- | ------- |
| **Pesos con índice** | Monto en pesos que se indexa según un índice configurable | IPC, ICL, costo construcción |
| **Moneda extranjera** | Pago en divisa (USD, EUR, etc.), convertido a pesos al tipo de cambio del día. Se preserva el monto original en moneda extranjera | Pago en USD → se guarda monto USD + cotización + monto en pesos |
| **Producto agropecuario** | Pago en pesos con referencia al precio de un producto agrícola o ganadero, con fuente de precio configurable | xx kg de soja/ha (precio Bolsa de Cereales de Rosario), xx kg de novillo/ha (precio mercado X) |

### Frecuencia de Cobro

La frecuencia es configurable por contrato:

- **Mensual** — cobro todos los meses.
- **Trimestral** — cobro cada 3 meses.
- **Anual** — cobro una vez al año.
- **Al vencimiento / renovación** — cobro al finalizar el contrato o al renovarlo.

### Cobros
- Registro de cada cobro con: fecha de cobro, monto cobrado, moneda original (si aplica), cotización aplicada (si aplica).
- Historial de cobros por contrato.
- Cada cobro queda trazable: se sabe en qué moneda se pagó, a qué cotización se convirtió, y el monto final en pesos.

### Consulta y Visualización
- Listado de inmuebles con tag de estado.
- Vista detallada de inmueble alquilado: propietario, inquilino, fechas del contrato, fecha máxima de pago, modalidad de cobro.

### Fuente de Precio de Referencia (Producto Agropecuario)
- Cada contrato con modalidad agropecuria indica la **fuente del precio de referencia** (ej: Bolsa de Cereales de Rosario, mercado ganadero X).
- La fuente es un campo de texto libre, no se fetchea automáticamente.

---

## Qué NO se incluye (Out of Scope — por ahora)

- **Portal de propietarios**: los propietarios no acceden al sistema; es solo consulta futura.
- **Pagos online**: los cobros se registran manualmente, no se procesan pagos.
- **Facturación / impuestos**: el sistema no genera facturas ni calcula impuestos.
- **Notificaciones push / email**: no hay alertas automáticas por ahora.
- **Múltiples sucursales**: se asume una única inmobiliaria.
- **Mobile app**: por ahora solo interfaz web.
- **Reportes y gráficos**: análisis estadístico queda para una fase futura.
- **Índices automáticos**: la indexación se registra manualmente, no se fetcha de APIs oficiales.
- **Cotizaciones automáticas**: las cotizaciones de moneda extranjera se cargan manualmente por el operador.
