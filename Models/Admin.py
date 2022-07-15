from pydantic import BaseModel


class ChangeRoleFields(BaseModel):
    user_ID: int
    role: str
