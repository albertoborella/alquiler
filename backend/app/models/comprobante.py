from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.cobro import Cobro
    from app.models.propietario import Propietario


class ComprobanteBase(SQLModel):
    """Base comprobante schema."""
    cobro_id: str = Field(foreign_key="cobros.id", max_length=36)
    propietario_id: str = Field(foreign_key="propietarios.id", max_length=36)
    tipo: str = Field(default="comprobante", max_length=50)  # expensas, honorarios, comprobante
    numero: Optional[str] = Field(default=None, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=1000)
    monto_proporcional: float
    porcentaje_participacion: float


class Comprobante(ComprobanteBase, table=True):
    """Comprobante model for database."""
    __tablename__ = "comprobantes"
    
    id: Optional[str] = Field(default=None, primary_key=True, max_length=36)
    created_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    cobro: Optional["Cobro"] = Relationship(sa_relationship_kwargs={"lazy": "select"})
    propietario: Optional["Propietario"] = Relationship(sa_relationship_kwargs={"lazy": "select"})


class ComprobanteCreate(ComprobanteBase):
    """Schema for creating a comprobante."""
    pass


class ComprobanteUpdate(SQLModel):
    """Schema for updating a comprobante."""
    cobro_id: Optional[str] = Field(default=None, max_length=36)
    propietario_id: Optional[str] = Field(default=None, max_length=36)
    tipo: Optional[str] = Field(default=None, max_length=50)
    numero: Optional[str] = Field(default=None, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=1000)
    monto_proporcional: Optional[float] = None
    porcentaje_participacion: Optional[float] = None


class ComprobantePublic(ComprobanteBase):
    """Schema for comprobante response."""
    id: str
    created_at: Optional[datetime] = None
