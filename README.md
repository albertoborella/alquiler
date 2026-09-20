# Alquiler - Sistema de Gestión de Alquileres

Sistema web para la gestión de inmuebles en alquiler, propietarios, inquilinos, contratos y cobros.

## Requisitos

- Podman (o Docker)
- podman-compose (o docker-compose)

## Inicio Rápido

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd alquiler
```

2. Levantar los servicios:
```bash
podman-compose up --build
```

3. Acceder a los servicios:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/api/docs
- **Base de datos**: localhost:5432

## Estructura del Proyecto

```
alquiler/
├── backend/          # FastAPI
├── frontend/         # SvelteKit
├── db/              # Scripts de base de datos
├── docs/            # Documentación
├── uploads/         # Archivos subidos
└── podman-compose.yml
```

## Stack Tecnológico

- **Frontend**: Svelte/SvelteKit + TypeScript + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy + Alembic
- **Base de datos**: PostgreSQL 15+
- **Autenticación**: JWT + Cookies
- **Contenedores**: Podman + AWS ECR Public

## Desarrollo

### Backend

El backend se ejecuta automáticamente con `podman-compose up --build`. Para desarrollo local:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Gestión de Usuarios

La aplicación utiliza un modelo de usuarios con roles jerárquicos:

| Rol | Permisos |
|-----|----------|
| `admin` | Acceso total: crear/editar/eliminar usuarios, gestionar todos los módulos |
| `empleado` | Acceso a módulos operativos (inmuebles, contratos, cobros, personas) |

**Flujo de alta de usuarios:**

1. **Superadmin (primera vez):** Se crea desde la consola con un script interactivo:
   ```bash
   podman-compose exec backend python -m app.scripts.createsuperuser
   ```
   El script pide: email, nombre completo (opcional), y contraseña con confirmación.

2. **Usuarios adicionales:** Los crea el superadmin o un admin desde la app (sección *Usuarios*), asignando email, nombre, contraseña y rol.

3. **Cambio de contraseña:** Cada usuario puede cambiar su propia contraseña desde el link *Cambiar Contraseña* en la pantalla de login, o desde dentro de la app. La contraseña actual es requerida para confirmar el cambio.

### Autenticación

En desarrollo, el access_token se envía via header `X-Access-Token`.

**Desde Swagger UI** (http://localhost:8000/api/docs):
1. Expandí `POST /api/login`, hacé login con tu superadmin
2. Copiá el valor de `access_token` de la respuesta
3. Clickeá el candado 🔒 arriba a la derecha
4. Pegá el token en el campo `X-Access-Token` y clickeá **Authorize**
5. Ahora TODOS los endpoints funcionan (listar, crear, etc.)

**Desde terminal con curl:**
```bash
# Login — copiá el access_token de la respuesta
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@alquiler.com", "password": "tu_contraseña"}'

# Listar todos los usuarios
curl -H "X-Access-Token: <tu_access_token>" http://localhost:8000/api/users

# Listar solo superadmins
curl -H "X-Access-Token: <tu_access_token>" "http://localhost:8000/api/users?role=admin"

# Crear un usuario normal
curl -X POST http://localhost:8000/api/users \
  -H "X-Access-Token: <tu_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"email": "empleado@alquiler.com", "password": "123456", "full_name": "Empleado", "role": "empleado"}'
```

### Frontend

El frontend se ejecuta automáticamente con `podman-compose up --build`. Para desarrollo local:

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Autenticación
- `POST /api/login` - Iniciar sesión
- `POST /api/logout` - Cerrar sesión
- `POST /api/refresh` - Refrescar token
- `GET /api/me` - Obtener usuario actual
- `POST /api/change-password` - Cambiar contraseña propia (requiere auth)

### Usuarios
- `GET /api/users` - Listar usuarios (autenticado, filtrar con `?role=admin`)
- `POST /api/users` - Crear usuario (solo admin)
- `GET /api/users/{id}` - Obtener usuario (autenticado)
- `PUT /api/users/{id}` - Actualizar usuario (solo admin)
- `DELETE /api/users/{id}` - Eliminar usuario (solo admin)

## Variables de Entorno

Las variables de entorno se configuran en el archivo `.env`:

```env
DB_PASSWORD=alquiler_dev_2024
JWT_SECRET=super-secret-jwt-key-change-in-production
JWT_REFRESH_SECRET=super-secret-refresh-key-change-in-production
ENVIRONMENT=development
```

## Licencia

Privado - Uso interno de la inmobiliaria.
