from pydantic import BaseModel


class SuccessAuthorizationResponse(BaseModel):
    user_id: int
    token: str


class NeedIDAndToken(BaseModel):
    user_ID: int
    token: str
