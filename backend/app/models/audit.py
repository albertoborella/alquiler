from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class AuditLog(SQLModel, table=True):
    """Audit log model for database."""
    __tablename__ = "audit_log"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(default=None, foreign_key="users.id", max_length=36)
    action: str = Field(max_length=50)
    table_name: str = Field(max_length=100)
    record_id: Optional[str] = Field(default=None, max_length=36)
    old_values: Optional[str] = Field(default=None)  # JSON string
    new_values: Optional[str] = Field(default=None)  # JSON string
    created_at: Optional[datetime] = Field(default=None)


class AuditLogCreate(SQLModel):
    """Schema for creating an audit log entry."""
    user_id: Optional[str] = None
    action: str
    table_name: str
    record_id: Optional[str] = None
    old_values: Optional[str] = None
    new_values: Optional[str] = None


class AuditLogPublic(SQLModel):
    """Schema for audit log response."""
    id: int
    user_id: Optional[str] = None
    action: str
    table_name: str
    record_id: Optional[str] = None
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    created_at: Optional[datetime] = None
