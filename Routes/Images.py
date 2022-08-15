from fastapi import APIRouter, HTTPException
from typing import Dict

from Database.Database import *
from Models.Images import *
from Models.api import *
from Utils.Hasher import HasherClass

router = APIRouter()

HasherObject = HasherClass()
database = DatabaseClass()


@router.get('/', response_model=List[ImageInDatabase])
async def get_all_images():
    try:
        return await database.get_all_photos()
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')


@router.get('/{SectionId}', response_model=List[ImageInDatabase])
async def get_Section_Images(SectionId: int):
    try:
        return await database.get_section_photos(SectionId)
    except SectionNotFound:
        raise HTTPException(status_code=404, detail='Section not Found')
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database error')
