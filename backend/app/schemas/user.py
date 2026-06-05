from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr


UserRole = Literal["customer", "agent", "supervisor", "admin"]


class UserBase(BaseModel):
    name: str
    phone: str | None = None
    email: EmailStr
    role: UserRole
    department: str | None = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }