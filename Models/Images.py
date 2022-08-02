from pydantic import BaseModel
from typing import List


class CreateImageFields(BaseModel):
    image: str  # blob
    tags: List[int]


class ImageResponse(BaseModel):
    imageId: int
    image: str  # blob
    tags: List[int]


class CreateTagFields(BaseModel):
    tag: str


class TagResponse(BaseModel):
    tagId: int
    tag: str


class CreateSectionFields(BaseModel):
    section: str
    includedTags: List[TagResponse]


class SectionResponse(BaseModel):
    sectionId: int
    section: str
    includedTags: List[TagResponse]

