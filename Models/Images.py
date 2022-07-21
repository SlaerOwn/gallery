from pydantic import BaseModel


class CreateImageFields(BaseModel):
    image: str
    description: str


class EditDescription(BaseModel):
    image_ID: int
    description: str

class ImageResponse(BaseModel):
    image: str
    description: str
    date: str