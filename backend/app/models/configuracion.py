from typing import Optional
from sqlmodel import SQLModel, Field


class Configuracion(SQLModel, table=True):
    """Key-value configuration store."""
    __tablename__ = "configuracion"
    
    key: str = Field(max_length=100, primary_key=True)
    value: Optional[str] = Field(default=None, max_length=500)


class ConfiguracionUpdate(SQLModel):
    """Schema for updating configuration."""
    key: str
    value: Optional[str] = None
