from fastapi import APIRouter, HTTPException
from Database.Database import *
from Utils.Hasher import HasherClass


router = APIRouter()


Hasher = HasherClass()
Database = DatabaseClass()


@router.post('/images')
async def create_image(login: str, token: str, image: str, description: str):
    try:
        if Database.is_writer(login, token):
            Database.add_photo(image, description)
            return HTTPException(
                status_code=200,
                detail='OK')
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


@router.get('/images/{ID}')
async def get_image(ID: str):
    try:
        Photo = await Database.get_photo(ID)
        return Photo
    except UserNotExists:
        return HTTPException(status_code=404, detail='Image not found')


@router.delete('/images/{ID}')
async def delete_image(login: str, token: str, ID: str):
    try:
        if Database.is_writer(login, token):
            Database.delete_photo(ID)
            return HTTPException(status_code=200, detail='OK')
        else:
            return HTTPException(status_code=403, detail='No permissions')
    except UserNotExists:
        return HTTPException(status_code=404, detail='User not found')


@router.put('/images/{ID}')
async def edit_image(login: str, token: str, description: str, ID: str):
    try:
        if Database.is_writer(login, token):
            Database.change_description(ID, description)
        else:
            return HTTPException(status_code=403, detail='No permissions')
    except UserNotExists:
        return HTTPException(status_code=404, detail='User not found')