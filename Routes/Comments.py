from fastapi import APIRouter, HTTPException
from Database.Database import *
from Utils.Hasher import HasherClass

router = APIRouter()

Hasher = HasherClass()
Database = DatabaseClass()


@router.post('/images/{image_ID}/comments')
async def add_comment(image_ID: str, user_ID: str, token: str, comment: str):
    try:
        if Database.is_writer(user_ID):
            password = await Database.get_password(user_ID)
            if Hasher.CheckToken(token, user_ID, password):
                try:
                    Database.add_comment(image_ID, comment)
                except ImageNotFound:
                    return HTTPException(status_code=404, detail='Image not found')
            else:
                return HTTPException(status_code=403, detail='Bad Token')
        else:
            return HTTPException(status_code=403, detail='No permission')
    except UserNotExists:
        return HTTPException(status_code=404, detail='User not found')


@router.get('/images/{image_ID}/comments')
async def all_comments(image_ID: str):
    try:
        amount = await Database.get_all_comments(image_ID)
        lst = []
        for i in range(amount):
            lst += Database.get_comment(amount)
    except ImageNotFound:
        return HTTPException(status_code=404, detail='Image not found')


@router.delete('/images/{image_ID}/comments/{comment_id}')
async def delete_comment(image_ID: str, user_ID: str, token: str, comment_ID: str):
    try:
        if Database.is_writer(user_ID):
            password = await Database.get_password(user_ID)
            if Hasher.CheckToken(token, user_ID, password):
                try:
                    Database.delete_comment(image_ID, comment_ID)
                    return HTTPException(status_code=200, detail='OK')
                except CommentNotExists:
                    return HTTPException(status_code=404, detail='Comment not found')
                except ImageNotFound:
                    return HTTPException(status_code=404, detail='Image not found')
        else:
            return HTTPException(status_code=403, detail='No permission')
    except UserNotExists:
        return HTTPException(status_code=404, detail='User not found')


@router.put('/images/{image_ID}/comments/{comment_id}')
async def edit_comment(image_ID: str, user_ID: str, token: str, comment_id: str, comment: str):
    try:
        if Database.is_writer(user_ID):
            password = await Database.get_password(user_ID)
            if Hasher.CheckToken(token, user_ID, password):
                try:
                    Database.edit_comment(image_ID, comment_id, comment)
                    return HTTPException(status_code=200, detail='OK')
                except CommentNotExists:
                    return HTTPException(status_code=404, detail='Comment not found')
            else:
                return HTTPException(status_code=403, detail='Bad Token')
        else:
            return HTTPException(status_code=403, detail='No permission')
    except UserNotExists:
        return HTTPException(status_code=404, detail='User not exists')
