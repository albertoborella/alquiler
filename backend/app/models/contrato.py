from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.inmueble import Inmueble
    from app.models.inquilino import Inquilino
    from app.models.cobro import Cobro


class ContratoBase(SQLModel):
    """Base contrato schema."""
    inmueble_id: str = Field(foreign_key="inmuebles.id", max_length=36)
    inquilino_id: str = Field(foreign_key="inquilinos.id", max_length=36)
    fecha_inicio: date
    fecha_fin: date
    fecha_maxima_pago: int = Field(default=10)
    modalidad_pago: str = Field(max_length=50)  # pesos_indice, moneda_extranjera, producto_agropecuario
    frecuencia: str = Field(default="mensual", max_length=50)  # mensual, trimestral, anual, vencimiento
    monto_base: Optional[float] = None
    moneda: Optional[str] = Field(default="ARS", max_length=3)
    indice: Optional[str] = Field(default=None, max_length=50)
    periodo_indexacion: Optional[str] = Field(default=None, max_length=50)  # mensual, trimestral, anual
    tipo_producto: Optional[str] = Field(default=None, max_length=100)  # soja, trigo, maiz, etc.
    kilos: Optional[float] = None
    precio_kilo: Optional[float] = None
    fuente_precio_agro: Optional[str] = Field(default=None, max_length=255)
    activo: bool = Field(default=True)


class Contrato(ContratoBase, table=True):
    """Contrato model for database."""
    __tablename__ = "contratos"
    
    id: Optional[str] = Field(default=None, primary_key=True, max_length=36)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships - using string annotations for forward references
    inmueble: Optional["Inmueble"] = Relationship(sa_relationship_kwargs={"lazy": "select"})
    inquilino: Optional["Inquilino"] = Relationship(sa_relationship_kwargs={"lazy": "select"})
    cobros: List["Cobro"] = Relationship(back_populates="contrato", sa_relationship_kwargs={"lazy": "select"})


class ContratoCreate(ContratoBase):
    """Schema for creating a contrato."""
    pass


class ContratoUpdate(SQLModel):
    """Schema for updating a contrato."""
    inmueble_id: Optional[str] = Field(default=None, max_length=36)
    inquilino_id: Optional[str] = Field(default=None, max_length=36)
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    fecha_maxima_pago: Optional[int] = None
    modalidad_pago: Optional[str] = Field(default=None, max_length=50)
    frecuencia: Optional[str] = Field(default=None, max_length=50)
    monto_base: Optional[float] = None
    moneda: Optional[str] = Field(default=None, max_length=3)
    indice: Optional[str] = Field(default=None, max_length=50)
    periodo_indexacion: Optional[str] = Field(default=None, max_length=50)
    tipo_producto: Optional[str] = Field(default=None, max_length=100)
    kilos: Optional[float] = None
    precio_kilo: Optional[float] = None
    fuente_precio_agro: Optional[str] = Field(default=None, max_length=255)
    activo: Optional[bool] = None


class ContratoPublic(ContratoBase):
    """Schema for contrato response."""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
