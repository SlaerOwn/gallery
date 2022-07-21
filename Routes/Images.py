from typing import Union
from fastapi import APIRouter, HTTPException
from Database.Database import *
from Utils.Hasher import HasherClass
from Models.api import *
from Models.Images import *

router = APIRouter()


HasherObject = HasherClass()
Database = DatabaseClass()


@router.post('/images', status_code=200)
async def create_image(image: CreateImageFields, user: NeedIDAndToken):
    try:
        if await Database.is_writer(user.user_ID):
            password = await Database.get_password(user.user_ID)
            try:
                if HasherObject.CheckToken(user.token, user.user_ID, password):
                    await Database.add_photo(image.image, image.description)
                else:
                    raise HTTPException(status_code=403, detail='Bad Token')
            except:
                raise HTTPException(status_code=401, detail='Not Authorized')
        else:
            raise HTTPException(status_code=403,
                                detail='No permissions')
    except UserNotExists:
        raise HTTPException(status_code=404,
                            detail='User does not exist')


@router.get('/images', response_model=list[ImageResponse])
async def get_all_images():
    try:
        return await Database.get_all_photos()
    except PhotoNotExists:
        raise HTTPException(status_code=404, detail='No photos yet')


@router.get('/images/{image_ID}', response_model=ImageResponse)
async def get_image(image_ID: int):
    try:
        Photo = await Database.get_photo(image_ID)
        return Photo
    except PhotoNotExists:
        raise HTTPException(status_code=404, detail='Image not found')


@router.delete('/images/{image_ID}', status_code=200)
async def delete_image(user: NeedIDAndToken, image_ID: int):
    try:
        if await Database.is_writer(user.user_ID):
            password = await Database.get_password(user.user_ID)
            try:
                if HasherObject.CheckToken(user.token, user.user_ID, password):
                    try:
                        await Database.delete_photo(image_ID)
                    except PhotoNotExists:
                        raise HTTPException(status_code=404, detail='Image not found')
                else:
                    raise HTTPException(status_code=403, detail='Bad Token')
            except:
                raise HTTPException(status_code=401, detail='Not Authorized')
        else:
            raise HTTPException(status_code=403, detail='No permissions')
    except UserNotExists:
        raise HTTPException(status_code=404, detail='User not found')


@router.put('/images/{image_ID}', status_code=200)
async def edit_image(user: NeedIDAndToken, edit: EditDescription):
    try:
        if await Database.is_writer(user.user_ID):
            password = await Database.get_password(user.user_ID)
            try:
                if HasherObject.CheckToken(user.token, user.user_ID, password):
                    try:
                        await Database.change_description(edit.image_ID, edit.description)
                    except PhotoNotExists:
                        raise HTTPException(status_code=404, detail='Image Not Found')
                else:
                    raise HTTPException(status_code=403, detail='Bad Token')
            except:
                raise HTTPException(status_code=401, detail='Not Authorized')
        else:
            raise HTTPException(status_code=403, detail='No permissions')
    except UserNotExists:
        raise HTTPException(status_code=404, detail='User not found')
