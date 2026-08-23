from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class InquilinoBase(SQLModel):
    """Base inquilino schema."""
    nombre: str = Field(max_length=255)
    dni: str = Field(max_length=20, unique=True, index=True)
    telefono: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    direccion: Optional[str] = Field(default=None, max_length=500)


class Inquilino(InquilinoBase, table=True):
    """Inquilino model for database."""
    __tablename__ = "inquilinos"
    
    id: Optional[str] = Field(default=None, primary_key=True, max_length=36)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


class InquilinoCreate(InquilinoBase):
    """Schema for creating an inquilino."""
    pass


class InquilinoUpdate(SQLModel):
    """Schema for updating an inquilino."""
    nombre: Optional[str] = Field(default=None, max_length=255)
    dni: Optional[str] = Field(default=None, max_length=20)
    telefono: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    direccion: Optional[str] = Field(default=None, max_length=500)


class InquilinoPublic(InquilinoBase):
    """Schema for inquilino response."""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
