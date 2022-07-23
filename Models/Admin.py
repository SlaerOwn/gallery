from pydantic import BaseModel


class ChangeRoleFields(BaseModel):
    user_id: int
    role: str
