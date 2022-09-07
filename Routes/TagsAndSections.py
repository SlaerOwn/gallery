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
        Tags = await database.get_tags()
        return {'Tags': Tags}
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')

@router.get('/sections')
async def get_Sections():
    try:
        return await database.get_sections()
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')
