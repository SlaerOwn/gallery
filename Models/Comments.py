from pydantic import BaseModel


class CreateCommentsField(BaseModel):
    image_ID: int
    comment: str


class EditCommentFields(BaseModel):
    comment_ID: int
    comment: str
