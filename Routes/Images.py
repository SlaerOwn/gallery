from fastapi import APIRouter, HTTPException
from Database.Database import *
from Utils.Hasher import HasherClass
from Models.api import TokenResponse

router = APIRouter()

Hasher = HasherClass()
Database = DatabaseClass()


@router.post('/images')
async def create_image(login: str, token: str, image: str, description: str):
    try:
        if Database.is_authorized(login, token):
            Database.create_image(image, description)
            return HTTPException(
                status_code=200,
                detail= 'OK')

    except NoPermissionError:
        return HTTPException(status_code=403,
                             detail='No permissions')

    except UserNotExists:
        return HTTPException(status_code=404,
                             detail='User does not exist')


@router.get('/images')
async def get_all_images():
    return Database.get_images()


@router.delete('/images/{image_id}')
async def delete_image(login: str, token: str, ID: str):
    try:
        if Database.is_authorized(login, token):
            Database.delete_image(ID)
            return HTTPException(status_code=200, detail='OK')

    except NoPermissionError:
        return HTTPException(status_code=403, detail='No permissions')

    except UserNotExists:
        return HTTPException(status_code=404, detail='User not found')