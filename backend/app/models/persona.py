from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.models.copropiedad import Copropiedad

if TYPE_CHECKING:
    from app.models.inmueble import Inmueble


class PersonaBase(SQLModel):
    """Base persona schema."""
    nombre: str = Field(max_length=255)
    cuit: str = Field(max_length=20, unique=True, index=True)
    iva: Optional[str] = Field(default=None, max_length=50)
    telefono: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    direccion: Optional[str] = Field(default=None, max_length=500)
    rol: str = Field(default="propietario", max_length=20)  # propietario, inquilino, ambos


class Persona(PersonaBase, table=True):
    """Persona model for database."""
    __tablename__ = "personas"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=36)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    inmuebles: List["Inmueble"] = Relationship(back_populates="propietarios", link_model=Copropiedad)


class PersonaCreate(PersonaBase):
    """Schema for creating a persona."""
    pass


class PersonaUpdate(SQLModel):
    """Schema for updating a persona."""
    nombre: Optional[str] = Field(default=None, max_length=255)
    cuit: Optional[str] = Field(default=None, max_length=20)
    iva: Optional[str] = Field(default=None, max_length=50)
    telefono: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    direccion: Optional[str] = Field(default=None, max_length=500)
    rol: Optional[str] = Field(default=None, max_length=20)


class PersonaPublic(PersonaBase):
    """Schema for persona response."""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
