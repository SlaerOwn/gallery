from typing import TypedDict
from pydantic import BaseModel

# --- Routes ---

class EditInfo(BaseModel):
    info: str


# --- Database ---

class AdminInDatabase(TypedDict):
    hashOfPassword: str
    aboutMe: str | None
    avatar: str | None
