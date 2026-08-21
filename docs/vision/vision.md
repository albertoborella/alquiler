# Visión del Proyecto: Alquiler

## Problema

Una inmobiliaria necesita administrar de forma ordenada y confiable todos los
inmuebles que tiene disponibles para alquiler, junto con los contratos,
propietarios e inquilinos asociados. Actualmente no existe un sistema que
centralice esta información y permita consultar rápidamente el estado de cada
inmueble, los cobros y las fechas de vencimiento.

El problema se complica porque los alquileres no son uniformes: cada contrato
puede tener modalidades de pago distintas (pesos, moneda extranjera, productos
agropecuarios), frecuencias variables (mensual, trimestral, anual) y fechas
de vencimiento propias.

## Solución

**Alquiler** es un sistema de gestión de alquileres que permite a la
inmobiliaria:

- Registrar y administrar inmuebles urbanos y rurales.
- Asociar cada inmueble a su propietario (un propietario puede tener varios inmuebles).
- Registrar contratos de alquiler con fechas de inicio y fin, y modalidad de pago.
- Dar de alta inquilinos y vincularlos a contratos (un inquilino puede alquilar varios inmuebles).
- Configurar la fecha máxima de pago por contrato antes de entrar en morosidad.
- Registrar cobros considerando la modalidad de cada contrato.
- Consultar al instante si un inmueble está alquilado o disponible.

## Usuarios

| Rol | Quién es | Qué necesita |
| ---- | -------- | ------------ |
| **Operador de la inmobiliaria** | Empleado que administra los alquileres | Ver inmuebles, crear contratos, registrar cobros, consultar estados |
| **Propietario** | Dueño del inmueble (consulta, no administra) | Ver el estado de su inmueble y los cobros realizados (futuro) |

## Métricas de Éxito

- Todos los inmuebles de la inmobiliaria están registrados en el sistema.
- El estado de cada inmueble (alquilado / disponible) se refleja en tiempo real.
- Los cobros quedan registrados y auditables, independientemente de la modalidad.
- Las fechas de vencimiento de pago son visibles y alertan cuando se aproximan.
- Se puede reconstruir el historial completo de un contrato: cobros, montos, monedas.
