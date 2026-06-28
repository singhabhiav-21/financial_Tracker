from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class UpdateUserRequest(BaseModel):
    email: str
    name: Optional[str] = None
    new_email: Optional[str] = None


class UpdatePasswordRequest(BaseModel):
    email: str
    old_password: str
    password: str
    re_password: str
    