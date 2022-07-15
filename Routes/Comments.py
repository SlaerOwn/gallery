from fastapi import APIRouter, HTTPException
from Database.Database import *
from Utils.Hasher import HasherClass
from Models.Comments import *
from Models.api import *

router = APIRouter()

HasherObject = HasherClass()
Database = DatabaseClass()


@router.post('/images/{image_ID}/comments', status_code=200)
async def add_comment(comment: CreateCommentsField, user: NeedIDAndToken):
    try:
        if await Database.is_writer(user.user_ID):
            password = await Database.get_password(user.user_ID)
            try:
                if HasherObject.CheckToken(user.token, user.user_ID, password):
                    try:
                        await Database.add_comment(user.user_ID, comment.image_ID, comment.comment)
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


@router.get('/images/{image_ID}/comments')
async def all_comments(image_ID: int):
    try:
        return await Database.get_comments(image_ID)
    except PhotoNotExists:
        raise HTTPException(status_code=404, detail='Image not found')


@router.delete('/images/{image_ID}/comments/{comment_id}', status_code=200)
async def delete_comment(user: NeedIDAndToken, comment_ID: int):
    try:
        if await Database.is_writer(user.user_ID):
            password = await Database.get_password(user.user_ID)
            try:
                if HasherObject.CheckToken(user.token, user.user_ID, password):
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
        if await Database.is_writer(user.user_ID):
            password = await Database.get_password(user.user_ID)
            try:
                if HasherObject.CheckToken(user.token, user.user_ID, password):
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
