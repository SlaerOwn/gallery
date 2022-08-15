from fastapi import APIRouter, HTTPException
from Database.Database import *
from Models.Images import *
from Models.api import *
from Utils.Hasher import HasherClass

router = APIRouter()

HasherObject = HasherClass()
database = DatabaseClass()


@router.get('/')
async def get_Tags():
    try:
        Tags = await database.get_tags()
        return {'Tags': Tags}
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')

'''
async def get_Sections():
    try:
        Sections = await database.get_sections()
        return {'sections': Sections}
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')
'''


