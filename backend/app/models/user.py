from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.session import metadata

# User model
users_table = metadata.tables.get("users")
if users_table is None:
    from sqlalchemy import Table, MetaData
    users_table = Table(
        "users",
        metadata,
        Column("id", String(36), primary_key=True),
        Column("email", String(255), unique=True, index=True, nullable=False),
        Column("hashed_password", String(255), nullable=False),
        Column("full_name", String(255), nullable=True),
        Column("role", String(50), nullable=False, default="empleado"),
        Column("is_active", Boolean, default=True),
        Column("created_at", DateTime(timezone=True), server_default=func.now()),
        Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
    )


class User:
    """User model class for SQLAlchemy."""
    __table__ = users_table
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
