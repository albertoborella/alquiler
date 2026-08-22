# Reglas de Negocio

## BR-01: Eliminación de Inquilinos
- No se puede eliminar un inquilino que tenga **contrato activo**.
- No se puede eliminar un inquilino que haya **alquilado algún inmueble alguna vez** (para preservar registros históricos).

## BR-02: Eliminación de Propietarios
- No se puede eliminar un propietario que tenga **inmuebles en la inmobiliaria**, independientemente de si tiene contrato activo o no.

## BR-03: Eliminación de Inmuebles
- No se puede eliminar un inmueble que tenga **contrato activo**.
- No se puede eliminar un inmueble que haya sido **ingresado a la inmobiliaria para su alquiler** (historial).
- **Excepción**: Se puede eliminar un inmueble si el propietario lo **retira de la inmobiliaria**.
  - Esta acción **solo puede realizarla el Administrador**.

## BR-04: Copropiedad y Contratos
- Cuando un inmueble tiene varios propietarios, el contrato es **firmado por todos los propietarios**.
- Se puede **modificar el porcentaje de participación** de un propietario mientras el contrato esté vigente.

## BR-05: Modalidad de Pago
- Se puede **modificar la modalidad de pago** durante un contrato vigente.

## BR-06: Renovación de Contratos
- Un contrato se renueva cuando vence.
- Se permite la **renovación anticipada** del contrato (con fecha de inicio al terminar el vigente) para evitar períodos sin contrato.

## BR-07: Registro de Cobros
- Se permiten **cobros parciales** (el inquilino puede pagar un monto menor al total del período).
- Se permiten **cobros anticipados** (varios meses juntos).
- Solo el **Administrador** puede modificar o eliminar un cobro ya registrado.

## BR-08: Cálculo de Morosidad
- El tag de morosidad se calcula **automáticamente**.
- Período de gracia: **3 días** después del vencimiento de la fecha máxima de pago.
- Si no se registra el cobro después del período de gracia, se marca como **moroso**.

## BR-09: Primer Usuario del Sistema
- El primer Administrador se crea mediante un **script en consola**, estando posicionado dentro del proyecto.

## BR-10: Búsquedas
- Búsqueda por **apellido de propietario**.
- Búsqueda por **apellido de inquilino**.
- Búsqueda por **dirección del inmueble**.

## BR-11: Filtros
- Filtro por **estado**: alquilado / disponible.
- Filtro por **categoría**: urbano / rural.

## BR-12: Exportación
- Generación de **informe PDF por propietario** que incluya:
  - Inmueble
  - Fecha de cobro
  - Importe
  - Fecha de vencimiento de contrato
