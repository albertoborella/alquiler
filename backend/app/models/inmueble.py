from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.models.copropiedad import Copropiedad

if TYPE_CHECKING:
    from app.models.propietario import Propietario
    from app.models.contrato import Contrato


class InmuebleBase(SQLModel):
    """Base inmueble schema."""
    direccion: str = Field(max_length=500)
    categoria: str = Field(default="urbano", max_length=50)  # urbano, rural
    superficie: Optional[float] = None
    habitaciones: Optional[int] = None
    banos: Optional[int] = None
    dormitorios: Optional[int] = None
    comodidades: Optional[str] = Field(default=None, max_length=1000)
    descripcion: Optional[str] = Field(default=None, max_length=2000)
    estado: str = Field(default="disponible", max_length=50)  # alquilado, disponible


class Inmueble(InmuebleBase, table=True):
    """Inmueble model for database."""
    __tablename__ = "inmuebles"
    
    id: Optional[str] = Field(default=None, primary_key=True, max_length=36)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    propietarios: List["Propietario"] = Relationship(back_populates="inmuebles", link_model=Copropiedad)
    contratos: List["Contrato"] = Relationship(back_populates="inmueble")


class InmuebleCreate(InmuebleBase):
    """Schema for creating an inmueble."""
    pass


class InmueblePropietarioIn(SQLModel):
    """A propietario to attach: either an existing one by id, or new owner data to create."""
    propietario_id: Optional[str] = None       # if set, use existing propietario
    porcentaje_participacion: float = 100.00
    # fields to create a NEW propietario (used only when propietario_id is None):
    nombre: Optional[str] = None
    dni_cuit: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None


class InmuebleCreateConPropietarios(InmuebleCreate):
    """Schema for creating an inmueble together with its propietarios (atomic)."""
    propietarios: List[InmueblePropietarioIn] = []


class InmuebleUpdate(SQLModel):
    """Schema for updating an inmueble."""
    direccion: Optional[str] = Field(default=None, max_length=500)
    categoria: Optional[str] = Field(default=None, max_length=50)
    superficie: Optional[float] = None
    habitaciones: Optional[int] = None
    banos: Optional[int] = None
    dormitorios: Optional[int] = None
    comodidades: Optional[str] = Field(default=None, max_length=1000)
    descripcion: Optional[str] = Field(default=None, max_length=2000)
    estado: Optional[str] = Field(default=None, max_length=50)


class InmueblePublic(InmuebleBase):
    """Schema for inmueble response."""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
