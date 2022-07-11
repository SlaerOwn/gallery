from fastapi import APIRouter, HTTPException
from Database.Database import *
from Utils.Hasher import HasherClass

router = APIRouter()


Hasher = HasherClass()
Database = DatabaseClass()


@router.post('/images')
async def create_image(user_ID: int, token: str, image: str, description: str):
    try:
        if Database.is_writer(user_ID):
            password = await Database.get_password(user_ID)
            if Hasher.CheckToken(token, user_ID, password):
                await Database.add_photo(image, description)
                return HTTPException(status_code=200,
                                     detail='OK')
            else:
                return HTTPException(status_code=403, detail='Bad Token')
        else:
            return HTTPException(status_code=403,
                                 detail='No permissions')
    except UserNotExists:
        return HTTPException(status_code=404,
                             detail='User does not exist')


@router.get('/images')
async def get_all_images():
    amount = await Database.get_all_photos()
    lst = []
    for i in range(amount):
        lst += Database.get_photo(amount)
    return lst


@router.get('/images/{image_ID}')
async def get_image(image_ID: int):
    try:
        Photo = await Database.get_photo(image_ID)
        return Photo
    except PhotoNotExists:
        return HTTPException(status_code=404, detail='Image not found')


@router.delete('/images/{image_ID}')
async def delete_image(user_ID: int, token: str, image_ID: int):
    try:
        if Database.is_writer(user_ID):
            password = await Database.get_password(user_ID)
            if Hasher.CheckToken(token, user_ID, password):
                try:
                    await Database.delete_photo(image_ID)
                    return HTTPException(status_code=200, detail='OK')
                except PhotoNotExists:
                    return HTTPException(status_code=404, detail='Image not found')

            else:
                return HTTPException(status_code=403, detail='Bad Token')
        else:
            return HTTPException(status_code=403, detail='No permissions')
    except UserNotExists:
        return HTTPException(status_code=404, detail='User not found')


@router.put('/images/{image_ID}')
async def edit_image(user_ID: int, token: str, description: str, image_ID: int):
    try:
        if Database.is_writer(user_ID):
            password = await Database.get_password(user_ID)
            if Hasher.CheckToken(token, user_ID, password):
                try:
                    await Database.change_description(image_ID, description)
                except PhotoNotExists:
                    return HTTPException(status_code=404, detail='Image Not Found')
            else:
                return HTTPException(status_code=403, detail='Bad Token')
        else:
            return HTTPException(status_code=403, detail='No permissions')
    except UserNotExists:
        return HTTPException(status_code=404, detail='User not found')
