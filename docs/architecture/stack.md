# Stack Tecnológico

## Visión General

| Capa | Tecnología | Versión |
|------|------------|---------|
| Frontend | Svelte/SvelteKit | Última estable |
| Backend | FastAPI | Última estable |
| Base de datos | PostgreSQL | Última estable |
| API | REST | - |
| Contenedores | Podman | - |

---

## Frontend: Svelte/SvelteKit

- **Framework**: SvelteKit (SSR + SPA)
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS (darkMode: class)
- **Estado**: Svelte stores
- **Navegación**: Scroll infinito en todos los listados
- **Tema**: Modo claro/oscuro con persistencia en localStorage
- **Responsive**: Sidebar oculto en mobile (hamburger), tablas con scroll horizontal, columnas progresivas

### Paquetes principales
- `@sveltejs/kit` - Framework principal
- `svelte` - Runtime
- `tailwindcss` - Estilos
- `typescript` - Type safety

---

## Backend: FastAPI

- **Framework**: FastAPI (async)
- **Lenguaje**: Python 3.11+
- **Validación**: Pydantic v2
- **Migraciones**: Alembic
- **ORM**: SQLAlchemy 2.0 (async)

### Paquetes principales
- `fastapi` - Framework web
- `uvicorn` - ASGI server
- `sqlalchemy[asyncio]` - ORM async
- `alembic` - Migraciones
- `pydantic` - Validación de datos
- `python-jose[cryptography]` - JWT
- `passlib[bcrypt]` - Hashing de contraseñas
- `python-multipart` - Form data

---

## Base de datos: PostgreSQL

- **Motor**: PostgreSQL 15+
- **Extensions**: 
  - `uuid-ossp` - Generación de UUIDs
  - `pgcrypto` - Encriptación
- **Collation**: `es_AR.UTF-8` (para ordernamiento español)

### Patrón de esquema
```
public/
├── users          # Usuarios del sistema
├── propietarios   # Propietarios de inmuebles
├── inquilinos     # Inquilinos
├── inmuebles      # Inmuebles
├── contratos      # Contratos de alquiler
├── cobros         # Cobros realizados
├── comprobantes   # Comprobantes por propietario
└── audit_log      # Registro de auditoría
```

---

## Autenticación y Seguridad

### JWT + Cookies
- **Access Token**: JWT firmado, duración **15 minutos**
- **Refresh Token**: JWT firmado, duración **7 días** (similar a redes sociales)
- **Almacenamiento**: 
  - Access token en cookie `httpOnly`, `secure`, `sameSite=strict`
  - Refresh token en cookie `httpOnly`, `secure`, `sameSite=strict`
- **Rotación**: Refresh token se renueva en cada uso

### Flujo de autenticación
```
1. Login → access_token (15min) + refresh_token (7d)
2. Request → cookie access_token
3. Si access_token expira → usar refresh_token para obtener nuevo access_token
4. Si refresh_token expira → redirect a login
```

### Headers de seguridad
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

---

## API REST

### Convenciones
- **URLs**: kebab-case (`/api/propietarios/{id}/inmuebles`)
- **Métodos**: GET, POST, PUT, DELETE, PATCH
- **Response format**: JSON estandarizado
- **Paginación**: Scroll infinito (cursor-based)
- **Versionado**: `/api/v1/...`

### Estructura de respuesta exitosa
```json
{
  "data": {},
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Estructura de respuesta error
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Descripción del error",
    "details": []
  }
}
```

---

## Imágenes (MVP Preparado)

- **Almacenamiento**: Directorio local `/uploads/images`
- **URLs**: Acceso directo vía `/api/images/{filename}`
- **Procesamiento**: Redimensionamiento básico (pendiente post-MVP)
- **Formatos**: JPEG, PNG, WebP
- **Límite**: 5MB por imagen

> **Nota**: La funcionalidad de subida y gestión de imágenes queda preparada en la estructura pero no se implementa en el MVP.

---

## Contenedores: Podman

### Imágenes base (AWS ECR Public)
- **Frontend**: `public.ecr.aws/docker/library/node:20-alpine`
- **Backend**: `public.ecr.aws/docker/library/python:3.11-slim`
- **Database**: `public.ecr.aws/docker/library/postgres:15-alpine`

### Arquitectura de contenedores
```
┌─────────────────────────────────────────────────┐
│                    podman-compose               │
├─────────────────┬─────────────────┬─────────────┤
│   frontend      │    backend      │  database   │
│   (SvelteKit)   │    (FastAPI)    │ (PostgreSQL)│
│   :3000         │    :8000        │  :5432      │
└─────────────────┴─────────────────┴─────────────┘
```

### Variables de entorno
```env
# Database
POSTGRES_DB=alquiler
POSTGRES_USER=alquiler_user
POSTGRES_PASSWORD=${DB_PASSWORD}

# Backend
DATABASE_URL=postgresql+asyncpg://alquiler_user:${DB_PASSWORD}@db:5432/alquiler
JWT_SECRET_KEY=${JWT_SECRET}
JWT_REFRESH_SECRET_KEY=${JWT_REFRESH_SECRET}
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Frontend
PUBLIC_API_URL=http://localhost:8000/api
```

---

## Estructura del Proyecto

```
alquiler/
├── frontend/              # SvelteKit
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/
│   │   │   ├── stores/
│   │   │   ├── utils/
│   │   │   └── api.ts
│   │   ├── routes/
│   │   └── app.html
│   ├── static/
│   ├── svelte.config.js
│   ├── vite.config.ts
│   └── package.json
│
├── backend/               # FastAPI
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── deps.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── crud/
│   │   ├── services/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── db/                    # PostgreSQL
│   ├── init.sql
│   └── seed.sql
│
├── podman-compose.yml
├── .env.example
└── docs/
```

---

## Decisiones Técnicas

### Por qué FastAPI sobre Django/Flask
- **Performance**: Async nativo, ideal para I/O intensivo
- **Type safety**: Pydantic v2, validación automática
- **Documentación**: Swagger/OpenAPI automático
- **Modernidad**: Python 3.11+, type hints

### Por qué SvelteKit sobre React/Vue
- **Performance**: Compilación estática, sin virtual DOM
- **Simplicidad**: Menos boilerplate, aprendizaje rápido
- **SSR**: Soporte nativo para server-side rendering
- **Bundle size**: Más pequeño que React/Vue

### Por qué PostgreSQL sobre MySQL
- **ACID**: Transacciones completas
- **JSON**: Soporte nativo para JSONB
- **Extensions**: UUID, pgcrypto, etc.
- **Performance**: Mejor para consultas complejas

### Por qué Podman sobre Docker
- **Seguridad**: Daemonless, rootless
- **Compatibilidad**: Compatible con Docker CLI
- **Licencia**: Apache 2.0 (no restricciones comerciales)
- **Imágenes AWS**: ECR Public no tiene restricciones de Docker Hub
