# Alcance del Proyecto

## Usuarios y Roles

El sistema es de uso exclusivo del **personal de la inmobiliaria** (usuarios cerrados, no públicos).

| Rol | Permisos |
|-----|----------|
| **Administrador** | Acceso total a todo el sistema y todas sus funcionalidades. |
| **Empleado** | Visualización de datos. **NO puede** registrar cobros ni eliminar inmuebles, propietarios, cobros ni contratos. |
| **Contable** | Visualización + registro de cobranzas. |

### Autenticación
- Login sencillo: **email + contraseña**.
- Seguridad implementada con **JWT**.

---

## Pantalla Principal (Dashboard)

- Tabla con **todos los inmuebles**, ordenados por propietario.
- Cada inmueble tiene un **tag de estado**:
  - 🟢 **Alquilado** (color distintivo)
  - 🔴 **No alquilado** (color distintivo)
- Desde aquí se puede:
  - Ver **todos los inmuebles de un propietario** específico (cuando tiene más de uno).
  - Acceder al **panel de cada inmueble**.

---

## Patrón de Navegación: Scroll Infinito

Todos los listados del sistema (inmuebles, propietarios, inquilinos, contratos) utilizan **scroll infinito** en lugar de paginado tradicional. Los datos se cargan progresivamente a medida que el usuario hace scroll hacia abajo.

---

## Panel de Inmueble

Al seleccionar un inmueble, se muestra:

### Datos del inmueble
- Dirección
- Superficie
- Habitaciones
- Baños
- Dormitorios
- Comodidades
- Categoría (urbano/rural)
- Descripción

### Si el inmueble está alquilado
- **Botón de cobros**: permite ingresar la cobranza del alquiler.
- **Contratos**: posibilidad de cargar y ver contratos de alquiler (cumplidos y vigentes).
- **Histórico de cobranzas** del contrato vigente.
- **Fecha de caducidad** del contrato.

---

## Funcionalidades de Consulta

### Por propietario
- Ver todos los inmuebles de un determinado propietario.
- **Informe mensual**: cobros de cada inmueble de su propiedad, desglosados por mes.

### Por período
- Listado de **todos los inmuebles en alquiler**.
- **Cobros realizados** durante un mes determinado.

### Control de morosidad
- Si un inmueble alquilado **no tiene registrado el cobro** y la **fecha máxima de cobro fue superada**: se muestra un **tag de Morosidad**.

---

## Gestión de Entidades (CRUD)

### Gestión de Inmuebles
- Alta, baja, edición y listado de inmuebles.
- Categoría: **urbano** o **rural** (campos rurales para alquiler).
- Tag de estado: **alquilado** o **disponible**.
- Datos del inmueble: dirección, descripción, características relevantes.
- Un inmueble puede tener **uno o varios propietarios** (copropiedad).

### Gestión de Propietarios
- Alta, baja, edición y listado de propietarios.
- Datos del propietario: nombre, DNI/CUIT, contacto.
- Un propietario puede tener **uno o varios** inmuebles.

### Gestión de Inquilinos
- Alta, baja, edición y listado de inquilinos.
- Datos del inquilino: nombre, DNI, contacto.
- Un inquilino puede alquilar **uno o varios** inmuebles (contratos independientes).

### Gestión de Contratos
- Creación de contrato con: inmueble, propietario, inquilino, fecha de inicio, fecha de fin.
- **Fecha máxima de pago** por contrato (configurable, ej: primeros 10 días de cada mes).
- **Modalidad de pago** por contrato (ver abajo).
- Cada contrato tiene una lista de cobros asociados.

---

## Modalidades de Pago

El sistema soporta múltiples modalidades de cobro, configurables por contrato:

| Modalidad | Descripción | Ejemplo |
| --------- | ----------- | ------- |
| **Pesos con índice** | Monto en pesos que se indexa según un índice configurable | IPC, ICL, costo construcción |
| **Moneda extranjera** | Pago en divisa (USD, EUR, etc.), convertido a pesos al tipo de cambio del día. Se preserva el monto original en moneda extranjera | Pago en USD → se guarda monto USD + cotización + monto en pesos |
| **Producto agropecuario** | Pago en pesos con referencia al precio de un producto agrícola o ganadero, con fuente de precio configurable | xx kg de soja/ha (precio Bolsa de Cereales de Rosario), xx kg de novillo/ha (precio mercado X) |

---

## Frecuencia de Cobro

La frecuencia es configurable por contrato:

- **Mensual** — cobro todos los meses.
- **Trimestral** — cobro cada 3 meses.
- **Anual** — cobro una vez al año.
- **Al vencimiento / renovación** — cobro al finalizar el contrato o al renovarlo.

---

## Cobros

- Registro de cada cobro con: fecha de cobro, monto cobrado, moneda original (si aplica), cotización aplicada (si aplica).
- Historial de cobros por contrato.
- Cada cobro queda trazable: se sabe en qué moneda se pagó, a qué cotización se convirtió, y el monto final en pesos.

---

## Fuente de Precio de Referencia (Producto Agropecuario)

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
- **Índices automáticos**: la indexación se registra manualmente, no se fetcha de APIs oficiales.
- **Cotizaciones automáticas**: las cotizaciones de moneda extranjera se cargan manualmente por el operador.
