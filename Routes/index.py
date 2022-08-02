from fastapi import APIRouter, HTTPException
from Database.Database import *
from Models.Images import *
from Models.api import *
from Utils.Hasher import HasherClass

router = APIRouter()

HasherObject = HasherClass()
Database = DatabaseClass()


@router.get('', response_model=List[ImageResponse])
async def get_all_images():
    try:
        return {'photos': await Database.get_all_photos()}
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')


@router.get('/{SectionId}', response_model=List[ImageResponse])
async def get_Section_Images(SectionId: int):
    try:
        Photos = await Database.get_section_photos(SectionId)
        return {'Photos': Photos}
    except SectionNotExists:
        raise HTTPException(status_code=404, detail='Section not Found')
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database error')


@router.get('/', response_model=List[Section])
async def get_Sections():
    try:
        Sections = await Database.get_sections()
        return {'sections': Sections}
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')


@router.get('/', response_model=List[Tag])
async def get_Tags():
    try:
        Tags = await Database.get_tags()
        return {'Tags': Tags}
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')
