from fastapi import APIRouter, HTTPException
from Database.Database import *
from Models.Images import *
from Models.api import *
from Utils.Hasher import HasherClass

router = APIRouter()

HasherObject = HasherClass()
database = DatabaseClass()


@router.get('/tags')
async def get_Tags():
    try:
        return await database.get_tags()
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')


@router.put('/images/{imageId}/tags/{tagId}')
async def edit_tag_name(tagId: int, edited_name: str, user: NeedToken):
    try:
        authorized = HasherObject.CheckToken(user.token, await database.get_password())
        if (not authorized): raise HTTPException(status_code=401, detail='Not Authorized')
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')
    try:
        await database.edit_tag_name(tagId, edited_name)
    except DatabaseError:
        raise HTTPException(status_code=200, detail='OK')


@router.post('/images/{imageId}/tags/{tagId}')
async def add_tag_to_image(imageId: int, tagId: int, user: NeedToken):
    try: 
        authorized = HasherObject.CheckToken(user.token, await database.get_password())
        if(not authorized): raise Exception()
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')
    except: raise HTTPException(status_code=401)
    try:
        await database.add_tag_to_image(imageId, tagId)
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')

@router.delete('/images/{imageId}/tags/{tagId}')
async def delete_tag_from_image(imageId: int, tagId: int, user: NeedToken):
    try: 
        authorized = HasherObject.CheckToken(user.token, await database.get_password())
        if(not authorized): raise Exception()
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')
    except: raise HTTPException(status_code=401)
    try:
        await database.delete_tag_from_image(imageId, tagId)
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')

@router.get('/sections')
async def get_Sections():
    try:
        return await database.get_sections()
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')
