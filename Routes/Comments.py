from fastapi import APIRouter, HTTPException
from Database.Database import *
from Utils.Hasher import HasherClass
from Models.Comments import *
from Models.api import *

router = APIRouter()

HasherObject = HasherClass()
Database = DatabaseClass()


@router.post('/images/{image_ID}/comments', status_code=200)
async def add_comment(comment: str, user: NeedIDAndToken, image_ID: int):
    try:
        if await Database.is_writer(user.user_id):
            password = await Database.get_password(user.user_id)
            try:
                if HasherObject.CheckToken(user.token, user.user_id, password):
                    try:
                        await Database.add_comment(user.user_id, image_ID, comment)
                    except PhotoNotExists:
                        raise HTTPException(status_code=404, detail='Image not found')
                else:
                    raise HTTPException(status_code=403, detail='Bad Token')
            except:
                raise HTTPException(status_code=401, detail='Not Authorized')
        else:
            raise HTTPException(status_code=403, detail='No permission')
    except UserNotExists:
        raise HTTPException(status_code=404, detail='User not found')


@router.get('/images/{image_ID}/comments')#, response_model=list[Comment])
async def all_comments(image_ID: int):
    try:
        return await Database.get_comments(image_ID)
    except PhotoNotExists:
        raise HTTPException(status_code=404, detail='Image not found')


@router.delete('/images/{image_ID}/comments/{comment_id}', status_code=200)
async def delete_comment(user: NeedIDAndToken, comment_ID: int, image_ID: int):
    try:
        if await Database.is_writer(user.user_id):
            password = await Database.get_password(user.user_id)
            try:
                if HasherObject.CheckToken(user.token, user.user_id, password):
                    try:
                        await Database.delete_comment(comment_ID)
                    except CommentNotExists:
                        raise HTTPException(status_code=404, detail='Comment not found')
                    except PhotoNotExists:
                        raise HTTPException(status_code=404, detail='Image not found')
            except:
                raise HTTPException(status_code=401, detail='Not Authorized')
        else:
            raise HTTPException(status_code=403, detail='No permission')
    except UserNotExists:
        raise HTTPException(status_code=404, detail='User not found')


@router.put('/images/{image_ID}/comments/{comment_id}', status_code=200)
async def edit_comment(user: NeedIDAndToken, edit: EditCommentFields):
    try:
        if await Database.is_writer(user.user_id):
            password = await Database.get_password(user.user_id)
            try:
                if HasherObject.CheckToken(user.token, user.user_id, password):
                    try:
                        await Database.change_comment(edit.comment_ID, edit.comment)
                    except CommentNotExists:
                        raise HTTPException(status_code=404, detail='Comment not found')
                else:
                    raise HTTPException(status_code=403, detail='Bad Token')
            except:
                raise HTTPException(status_code=401, detail='Not Authorized')
        else:
            raise HTTPException(status_code=403, detail='No permission')
    except UserNotExists:
        raise HTTPException(status_code=404, detail='User not exists')
