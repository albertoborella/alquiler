#!/usr/bin/env python3
"""
Create a superadmin user interactively.

Usage (from project root /alquiler):
    podman-compose exec backend python -m app.scripts.createsuperuser
"""

import sys
import getpass
import re
import asyncio
from datetime import datetime
import uuid

from sqlmodel import select
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def validate_email(email: str) -> bool:
    """Basic email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def prompt_input(prompt_text: str, validator=None, error_msg: str = "") -> str:
    """Prompt for input with optional validation."""
    while True:
        value = input(prompt_text).strip()
        if validator and not validator(value):
            print(f"  ❌ {error_msg}")
            continue
        return value


def prompt_password(prompt_text: str = "Contraseña: ") -> str:
    """Prompt for password (hidden input) with confirmation."""
    while True:
        password = getpass.getpass(prompt_text)
        if len(password) < 6:
            print("  ❌ La contraseña debe tener al menos 6 caracteres")
            continue

        confirm = getpass.getpass("Confirmar contraseña: ")
        if password != confirm:
            print("  ❌ Las contraseñas no coinciden, intentá de nuevo")
            continue

        return password


async def create_superadmin():
    """Interactive superadmin creation."""
    print("\n" + "=" * 50)
    print("  🔧 Crear Superadministrador")
    print("=" * 50)

    # Email
    email = prompt_input(
        "\nEmail: ",
        validator=validate_email,
        error_msg="Ingresá un email válido (ej: admin@alquiler.com)"
    )

    # Full name
    full_name = input("Nombre completo (opcional, Enter para omitir): ").strip() or None

    # Password
    password = prompt_password()

    # Confirm
    print(f"\n  📧 Email:     {email}")
    print(f"  👤 Nombre:    {full_name or '(no especificado)'}")
    print(f"  🔒 Rol:       admin (superadministrador)")

    confirm = input("\n¿Crear este usuario? (s/n): ").strip().lower()
    if confirm not in ("s", "si", "sí", "y", "yes"):
        print("\n⚠️  Operación cancelada.")
        return

    # Create in database
    async with AsyncSessionLocal() as db:
        # Check if email already exists
        result = await db.execute(select(User).where(User.email == email))
        if result.scalars().first():
            print(f"\n❌ Ya existe un usuario con el email '{email}'.")
            print("   Usá otro email o eliminá el usuario existente.")
            sys.exit(1)

        user = User(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role="admin",
            is_active=True,
            created_at=datetime.utcnow(),
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        print(f"\n✅ Superadministrador creado exitosamente!")
        print(f"   ID:    {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Rol:   {user.role}")
        print()


def main():
    try:
        asyncio.run(create_superadmin())
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación interrumpida.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
