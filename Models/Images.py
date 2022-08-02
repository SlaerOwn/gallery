from pydantic import BaseModel
from typing import List


class CreateImageFields(BaseModel):
    image: str  # blob
    tags: List[int]


class ImageResponse(BaseModel):
    imageId: int
    image: str  # blob
    tags: List[int]
