from fastapi import APIRouter, HTTPException
from typing import List

from Database.Database import *
from Utils.Hasher import HasherClass
from Models.api import *
from Models.Images import *

router = APIRouter()


HasherObject = HasherClass()
Database = DatabaseClass()


@router.post('/admin', status_code=200)
async def create_image(image: CreateImageFields, user: NeedToken):
    hashed_password = await Database.get_password()
    if HasherObject.CheckToken(user.token, hashed_password):
        await Database.add_photo(image.image, image.tags)
    else:
        raise HTTPException(status_code=401, detail='Bad Token')


@router.get('/images', response_model=List[ImageResponse])
async def get_all_images():
    return {'photos': await Database.get_all_photos()}


@router.get('/images/{image_ID}', response_model=ImageResponse)
async def get_image(image_ID: int):
    try:
        Photo = await Database.get_photo(image_ID)
        return Photo
    except PhotoNotExists:
        raise HTTPException(status_code=404, detail='Image not found')


