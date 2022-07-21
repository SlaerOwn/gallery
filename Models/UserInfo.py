from __future__ import annotations

from pydantic import BaseModel


class UserInfoFields(BaseModel):
    fcs: str
    pp: str


class User(BaseModel):
    user_id: int
    login: str
    role: str
    fcs: str
    pp: str
