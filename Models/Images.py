from pydantic import BaseModel
from typing import List, TypedDict

from Models.api import NeedToken

# - TAGS -
class TagResponse(BaseModel):
    tagId: int
    tag: str

class CreateTagFields(BaseModel):
    tag: str
    
class AddTagsToImageFields(BaseModel):
    tags: List[int]

class TagInDatabase(BaseModel):
    tagId: int
    tag: str

# - SECTIONS -
class CreateSectionFields(BaseModel):
    section: str
    includedTags: List[TagResponse]

class SectionResponse(BaseModel):
    sectionId: int
    section: str
    includedTags: List[TagResponse]

class SectionInDatabase(BaseModel):
    sectionId: int
    section: str

# - IMAGES -
class ImageInDatabase(BaseModel):
    imageId: int
    image: str

class ImageWithAllInfoInDatabase(TypedDict):
    imageId: int
    image: str
    tagId: int
    tag: str
    sectionId: int
    section: str

class ImageWithAllInfo(TypedDict):
    imageId: int
    image: str
    tags: List[TagInDatabase] | None
    sections: List[SectionInDatabase] | None

class CreateImageFields(NeedToken):
    tags: List[int]