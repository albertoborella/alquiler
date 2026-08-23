from typing import Optional, List
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship


class CobroBase(SQLModel):
    """Base cobro schema."""
    contrato_id: str = Field(foreign_key="contratos.id", max_length=36)
    fecha_cobro: date
    monto: float
    moneda_original: Optional[str] = Field(default=None, max_length=3)
    monto_original: Optional[float] = None
    cotizacion: Optional[float] = None
    fuente_precio: Optional[str] = Field(default=None, max_length=255)
    precio_producto: Optional[float] = None
    observaciones: Optional[str] = Field(default=None, max_length=1000)


class Cobro(CobroBase, table=True):
    """Cobro model for database."""
    __tablename__ = "cobros"
    
    id: Optional[str] = Field(default=None, primary_key=True, max_length=36)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    contrato: Optional["Contrato"] = Relationship(sa_relationship_kwargs={"lazy": "select"})
    comprobantes: List["Comprobante"] = Relationship(back_populates="cobro", sa_relationship_kwargs={"lazy": "select"})


class CobroCreate(CobroBase):
    """Schema for creating a cobro."""
    pass


class CobroUpdate(SQLModel):
    """Schema for updating a cobro."""
    contrato_id: Optional[str] = Field(default=None, max_length=36)
    fecha_cobro: Optional[date] = None
    monto: Optional[float] = None
    moneda_original: Optional[str] = Field(default=None, max_length=3)
    monto_original: Optional[float] = None
    cotizacion: Optional[float] = None
    fuente_precio: Optional[str] = Field(default=None, max_length=255)
    precio_producto: Optional[float] = None
    observaciones: Optional[str] = Field(default=None, max_length=1000)


class CobroPublic(CobroBase):
    """Schema for cobro response."""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
