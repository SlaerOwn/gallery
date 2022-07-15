from __future__ import annotations

from pydantic import BaseModel
from typing import Union


class UserInfoFields(BaseModel):
    user_ID: int
    FIO: Union[str, None]
    ProfilePicture: Union[str, None]


class GiveUser(BaseModel):
    user_ID: int
    login: str
    role: str
    FIO: str
    Profile_picture: str
