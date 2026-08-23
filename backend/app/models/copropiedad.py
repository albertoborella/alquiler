from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Copropiedad(SQLModel, table=True):
    """Copropiedad link model for many-to-many relationship."""
    __tablename__ = "copropiedad"
    
    id: Optional[str] = Field(default=None, primary_key=True, max_length=36)
    propietario_id: str = Field(foreign_key="propietarios.id", max_length=36)
    inmueble_id: str = Field(foreign_key="inmuebles.id", max_length=36)
    porcentaje_participacion: float = Field(default=100.00)
    created_at: Optional[datetime] = Field(default=None)


class CopropiedadCreate(SQLModel):
    """Schema for creating a copropiedad relationship."""
    propietario_id: str
    porcentaje_participacion: float = 100.00


class CopropiedadPublic(SQLModel):
    """Schema for copropiedad response."""
    id: str
    propietario_id: str
    inmueble_id: str
    porcentaje_participacion: float
    created_at: Optional[datetime] = None
