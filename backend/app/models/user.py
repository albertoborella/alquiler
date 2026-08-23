from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class UserBase(SQLModel):
    """Base user schema."""
    email: str = Field(max_length=255, unique=True, index=True)
    full_name: Optional[str] = Field(default=None, max_length=255)
    role: str = Field(default="empleado", max_length=50)


class User(UserBase, table=True):
    """User model for database."""
    __tablename__ = "users"
    
    id: Optional[str] = Field(default=None, primary_key=True, max_length=36)
    hashed_password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str


class UserUpdate(SQLModel):
    """Schema for updating a user."""
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    role: Optional[str] = Field(default=None, max_length=50)
    is_active: Optional[bool] = None


class UserPublic(UserBase):
    """Schema for user response."""
    id: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LoginRequest(SQLModel):
    """Schema for login request."""
    email: str
    password: str


class TokenResponse(SQLModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
