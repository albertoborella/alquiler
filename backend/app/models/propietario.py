from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.models.copropiedad import Copropiedad


class PropietarioBase(SQLModel):
    """Base propietario schema."""
    nombre: str = Field(max_length=255)
    dni_cuit: str = Field(max_length=20, unique=True, index=True)
    telefono: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    direccion: Optional[str] = Field(default=None, max_length=500)


class Propietario(PropietarioBase, table=True):
    """Propietario model for database."""
    __tablename__ = "propietarios"
    
    id: Optional[str] = Field(default=None, primary_key=True, max_length=36)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    inmuebles: List["Inmueble"] = Relationship(back_populates="propietarios", link_model=Copropiedad)


class PropietarioCreate(PropietarioBase):
    """Schema for creating a propietario."""
    pass


class PropietarioUpdate(SQLModel):
    """Schema for updating a propietario."""
    nombre: Optional[str] = Field(default=None, max_length=255)
    dni_cuit: Optional[str] = Field(default=None, max_length=20)
    telefono: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    direccion: Optional[str] = Field(default=None, max_length=500)


class PropietarioPublic(PropietarioBase):
    """Schema for propietario response."""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
