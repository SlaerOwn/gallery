from fastapi import APIRouter, HTTPException
from Database.Database import *
from Utils.Hasher import HasherClass

router = APIRouter()


Hasher = HasherClass()
Database = DatabaseClass()


@router.post('/images')
async def create_image(user_ID: int, token: str, image: str, description: str):
    try:
        if await Database.is_writer(user_ID):
            password = await Database.get_password(user_ID)
            try:
                if Hasher.CheckToken(token, user_ID, password):
                    await Database.add_photo(image, description)
                    return HTTPException(status_code=200,
                                         detail='OK')
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


@router.get('/images')
async def get_all_images():
    try:
        return {'Photos': Database.get_all_photos()}
    except PhotoNotExists:
        raise HTTPException(status_code=404, detail='No photos yet')



@router.get('/images/{image_ID}')
async def get_image(image_ID: int):
    try:
        Photo = await Database.get_photo(image_ID)
        return {'Photo': Photo}
    except PhotoNotExists:
        raise HTTPException(status_code=404, detail='Image not found')


@router.delete('/images/{image_ID}')
async def delete_image(user_ID: int, token: str, image_ID: int):
    try:
        if await Database.is_writer(user_ID):
            password = await Database.get_password(user_ID)
            try:
                if Hasher.CheckToken(token, user_ID, password):
                    try:
                        await Database.delete_photo(image_ID)
                        return HTTPException(status_code=200, detail='OK')
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


@router.put('/images/{image_ID}')
async def edit_image(user_ID: int, token: str, description: str, image_ID: int):
    try:
        if await Database.is_writer(user_ID):
            password = await Database.get_password(user_ID)
            try:
                if Hasher.CheckToken(token, user_ID, password):
                    try:
                        await Database.change_description(image_ID, description)
                        return HTTPException(status_code=200, detail='description changed')
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
