from pydantic import BaseModel

class CreateImageFields(BaseModel):
    image: str
    description: str