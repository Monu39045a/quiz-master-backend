from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserRegistration(BaseModel):
    user_id: str
    full_name: Optional[str] = None
    email: str
    password: str
    is_trainer: Optional[bool] = False
    is_participant: Optional[bool] = False


class UserResponseOut(BaseModel):
    id: int
    user_id: str
    full_name: Optional[str] = None
    email: str
    is_trainer: bool
    is_participant: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class LoginRequest(BaseModel):
    user_id: str
    password: str
    role: str  # "trainer" or "participant"


class LoginResponse(BaseModel):
    user: UserResponseOut
    token: str
