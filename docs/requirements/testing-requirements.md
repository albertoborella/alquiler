# Requisitos de Testing

## TR-01: Cobertura de Test Unitarios
- Implementar **test unitarios** para todos los endpoints importantes del backend.
- Cobertura minima del **80%** en la logica de negocio critica.

## TR-02: Endpoints a Testear
Los siguientes endpoints deben tener test unitarios:

### Autenticacion
- Login (exitoso y fallido)
- Registro de usuarios (solo admin)
- Control de acceso por rol

### CRUD de Entidades
- Inmuebles: alta, baja, edicion, listado
- Propietarios: alta, baja, edicion, listado
- Inquilinos: alta, baja, edicion, listado
- Contratos: alta, edicion, listado, renovacion
- Cobros: registro, edicion, eliminacion

### Logica de Negocio
- Calculo de morosidad (BR-08)
- Generacion de comprobantes por propietario (FR-12)
- Validacion de eliminacion con dependencias (BR-01, BR-02, BR-03)
- Control de permisos por rol (FR-03)

### Busquedas y Filtros
- Busqueda por propietario, inquilino, direccion (BR-10)
- Filtros por estado y categoria (BR-11)

## TR-03: Tipos de Verificacion
Cada test debe verificar:
- **Caso exitoso**: operacion completada correctamente
- **Caso de error**: validacion de reglas de negocio
- **Caso edge**: valores limites, datos faltantes, permisos insuficientes

## TR-04: Datos de Prueba
- Utilizar fixtures o factories para datos de prueba
- Los tests no deben depender de datos de produccion
- Cada test debe ser independiente (no depender de otros tests)
