# Requisitos Funcionales

## Autenticacion y Seguridad

### FR-01: Login
- El sistema debe permitir el acceso mediante **email y contrasena**.
- La autenticacion se realiza mediante **JWT (JSON Web Token)**.

### FR-02: Gestion de Usuarios
- Solo el **Administrador** puede crear, modificar y eliminar usuarios del sistema.
- Cada usuario tiene un **rol** asignado: Administrador, Empleado o Contable.

### FR-03: Control de Acceso por Rol

| Funcionalidad | Admin | Empleado | Contable |
|---------------|-------|----------|----------|
| Visualizar datos | Si | Si | Si |
| Registrar cobros | Si | No | Si |
| Eliminar inmuebles | Si | No | No |
| Eliminar propietarios | Si | No | No |
| Eliminar inquilinos | Si | No | No |
| Eliminar contratos | Si | No | No |
| Eliminar cobros | Si | No | No |
| Modificar cobros | Si | No | No |
| Gestionar usuarios | Si | No | No |
| Gestionar inquilinos | Si | No | No |
| Ver propietarios desde tabla inmuebles | Si | No | No |
| Registrar cobro desde tabla inmuebles | Si | No | No |
| Ver historial de cobros desde tabla | Si | No | No |
| Editar contrato desde tabla inmuebles | Si | No | No |
| Generar contrato desde tabla inmuebles | Si | No | No |
| Crear inmueble desde tabla inmuebles | Si | No | No |

---

## Gestion de Inmuebles

### FR-04: CRUD de Inmuebles
- **Alta**: registrar un nuevo inmueble con sus datos (direccion, categoria, superficie, habitaciones, banos, dormitorios, comodidades, descripcion).
- **Baja**: eliminar inmueble (solo si cumple BR-03).
- **Edicion**: modificar datos del inmueble.
- **Listado**: ver todos los inmuebles con tag de estado.

### FR-05: Panel de Inmueble
- Al seleccionar un inmueble, mostrar:
  - Datos completos (direccion, superficie, habitaciones, banos, dormitorios, comodidades).
  - Tag de estado (alquilado/disponible).
  - Si esta alquilado: boton de cobros, contratos, historico de cobranzas, fecha de caducidad.

### FR-05a: Acciones de Administrador en Tabla de Inmuebles
- La tabla de inmuebles muestra **iconos de accion** exclusivos para el rol **Administrador**:
  - **Ver propietarios**: muestra modal con lista de propietarios y su porcentaje de participacion.
  - **Registrar cobro**: abre modal para crear un cobro (`POST /api/cobros`) vinculado al contrato del inmueble. Pre-carga fecha de hoy y monto base del contrato.
  - **Historial de cobros**: muestra modal con listado de cobros anteriores del contrato (`GET /api/cobros/contrato/{id}`).
  - **Editar contrato**: enlace a formulario de edicion del contrato vigente.
  - **Editar inmueble**: enlace a formulario de edicion del inmueble.
  - **Eliminar inmueble**: icono con confirmacion antes de eliminar.
- El usuario **Empleado** solo ve la tabla sin iconos de accion (solo lectura).

### FR-05b: Generar Contrato desde Tabla de Inmuebles
- Cuando un inmueble esta en estado **disponible**, se muestra un icono **"Generar Contrato"** en la fila.
- Al hacer click, se abre un modal con los siguientes campos:

#### Campos comunes (todos los inmuebles):
| Campo | Tipo | Obligatorio | Descripcion |
|-------|------|-------------|-------------|
| Fecha de inicio | date | si | Fecha de inicio del contrato |
| Fecha final | date | si | Fecha de finalizacion del contrato |

#### Campos para inmuebles urbanos (modalidad peso/indice o moneda extranjera):
| Campo | Tipo | Obligatorio | Descripcion |
|-------|------|-------------|-------------|
| Importe mensual de inicio | decimal | no | Monto base del alquiler en la moneda indicada |
| Moneda | select | no | Moneda del importe (ARS por defecto, USD) |
| Periodo de indexacion | select | no | Periodo de actualizacion del importe (ej: mensual, trimestral, anual) |
| Indice de indexacion | select | no | Indice utilizado para actualizacion (ej: ICL, IPC) |

#### Campos para inmuebles rurales (modalidad producto agropecuario):
| Campo | Tipo | Obligatorio | Descripcion |
|-------|------|-------------|-------------|
| Tipo de producto | select | si | Producto agropecuario (ej: soja, trigo, maiz) |
| Kilos | decimal | si | Cantidad de kilos del producto |
| Precio por kilo | decimal | si | Precio unitario del producto |

- La seleccion de campos se realiza automaticamente segun la **categoria** del inmueble (urbano/rural).
- Al confirmar, se crea un contrato con `modalidad_pago` segun corresponda:
  - **Urbano**: `pesos_indice` o `moneda_extranjera` (segun moneda elegida)
  - **Rural**: `producto_agropecuario`
- El inmueble cambia automaticamente de estado a **alquilado** al crearse el contrato.
- Solo el **Administrador** puede generar contratos desde la tabla.

---

## Gestion de Propietarios

### FR-06: CRUD de Propietarios
- **Alta**: registrar propietario con nombre, DNI/CUIT, contacto.
- **Baja**: eliminar propietario (solo si cumple BR-02).
- **Edicion**: modificar datos del propietario.
- **Listado**: ver todos los propietarios.

### FR-07: Copropiedad
- Asignar uno o varios propietarios a un inmueble con porcentaje de participacion.
- La suma de participaciones debe ser 100%.
- Modificar participacion porcentual (incluso con contrato vigente, segun BR-04).

---

## Gestion de Inquilinos

### FR-08: CRUD de Inquilinos
- **Alta**: registrar inquilino con nombre, DNI, telefono, email, direccion.
- **Baja**: eliminar inquilino (solo si cumple BR-01).
- **Edicion**: modificar datos del inquilino.
- **Listado**: tabla con todos los inquilinos (nombre, DNI, telefono, email).
- Acceso desde el **Sidebar** en la seccion "Inquilinos".
- Solo el **Administrador** puede crear, editar y eliminar inquilinos.
- El usuario **Empleado** solo ve la tabla (solo lectura).
- El inquilino seleccionado se vincula al contrato al generar uno desde la tabla de inmuebles.

---

## Gestion de Contratos

### FR-09: CRUD de Contratos
- **Alta**: crear contrato con inmueble, propietarios(s), inquilino, fecha inicio, fecha fin, fecha maxima de pago, modalidad de pago, frecuencia.
- **Edicion**: modificar datos del contrato (modalidad de pago, fechas, etc.).
- **Listado**: ver contratos de un inmueble (cumplidos y vigentes).

### FR-10: Renovacion de Contratos
- Renovar contrato vencido con nueva fecha de inicio al terminar el vigente.
- Permitir renovacion anticipada (segun BR-06).

---

## Gestion de Cobros

### FR-11: Registro de Cobros
- Registrar cobro con: fecha de cobro, monto, moneda original (si aplica), cotizacion (si aplica), observaciones.
- Asociar cobro a un contrato especifico.
- Soportar cobros parciales y anticipados (segun BR-07).
- **Registro rapido desde tabla de inmuebles** (admin): icono "Cobrar" en la fila del inmueble abre modal pre-cargado con fecha actual y monto base del contrato.

### FR-12: Comprobantes
- Al registrar un cobro, generar **un comprobante por propietario** con monto proporcional a su participacion.

### FR-13: Historico de Cobros
- Ver listado de cobros realizados para un contrato especifico.
- Cada cobro muestra: fecha, monto, moneda, comprobantes generados.

---

## Dashboard y Consultas

### FR-14: Tabla Principal de Inmuebles
- Mostrar tabla con todos los inmuebles ordenados por propietario.
- Tag de estado con color distintivo (alquilado/no alquilado).
- Columna de morosidad con formato **Sí / No** (segun BR-08).

### FR-15: Consulta por Propietario
- Ver todos los inmuebles de un propietario especifico.
- Generar **informe mensual** de cobros por inmueble.

### FR-16: Consulta por Periodo
- Ver listado de inmuebles en alquiler.
- Ver cobros realizados durante un mes determinado.

### FR-17: Busqueda
- Busqueda por apellido de propietario (BR-10).
- Busqueda por apellido de inquilino (BR-10).
- Busqueda por direccion del inmueble (BR-10).

### FR-18: Filtros
- Filtro por estado: alquilado / disponible (BR-11).
- Filtro por categoria: urbano / rural (BR-11).

---

## Navegacion y UX

### FR-21: Scroll Infinito
- Todos los listados de inmuebles, propietarios, inquilinos y contratos utilizan **scroll infinito** en lugar de paginado.
- Los datos se cargan progresivamente a medida que el usuario hace scroll hacia abajo.
- Se muestra un indicador de carga mientras se obtienen nuevos registros.

### FR-23: Modo Claro / Oscuro
- El sistema ofrece un **toggle de tema** (sol/luna) en la barra de navegacion.
- El tema seleccionado se persiste en `localStorage` y se aplica al recargar.
- Si no hay tema guardado, respeta la preferencia del sistema operativo (`prefers-color-scheme`).
- Todos los componentes (tablas, modales, sidebar, navbar, formularios) soportan ambos modos.

---

## Exportacion

### FR-19: Informe PDF por Propietario
- Generar PDF con: inmueble, fecha de cobro, importe, fecha de vencimiento de contrato (BR-12).

---

## Primer Usuario

### FR-20: Script de Inicializacion
- Script en consola para crear el primer Administrador del sistema (segun BR-09).

---

## Diseno Responsivo

### FR-24: Layout Responsivo
- El sidebar se oculta en pantallas chicas (`< md`) y se muestra via hamburger menu.
- Las tablas usan scroll horizontal en mobile con columnas ocultas progresivamente (Inquilino, Monto, Vencimiento se ocultan en pantallas chicas).
- Los filtros y botones se apilan en mobile.
- Sidebar mas angosto (`w-44` / 11rem) para maximizar espacio de contenido.

---

## Testing

### FR-22: Test Unitarios del Backend
- Implementar **test unitarios** para todos los endpoints importantes del backend.
- Los tests deben cubrir:
  - CRUD de inmuebles, propietarios, inquilinos, contratos y cobros.
  - Endpoints de autenticacion y autorizacion.
  - Endpoints de busqueda y filtros.
  - Logica de negocio critica (calculo de morosidad, generacion de comprobantes).
- Cada test debe verificar tanto el caso exitoso como los casos de error.
