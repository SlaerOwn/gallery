from pydantic import BaseModel

from Models.UserInfo import User


class EditCommentFields(BaseModel):
    comment_id: int
    comment: str

class Comment(BaseModel):
    id: int
    author: User
    photoid: int
    description: str
    date: str
