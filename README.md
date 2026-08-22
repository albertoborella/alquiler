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

### Usuarios (Solo Admin)
- `GET /api/users` - Listar usuarios
- `POST /api/users` - Crear usuario
- `GET /api/users/{id}` - Obtener usuario
- `PUT /api/users/{id}` - Actualizar usuario
- `DELETE /api/users/{id}` - Eliminar usuario

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
