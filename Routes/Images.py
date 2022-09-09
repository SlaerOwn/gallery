from fastapi import APIRouter, HTTPException, UploadFile, Body
from typing import Dict, NewType, Type, TypeVar, Union
import aiofiles
from pathlib import Path

from Database.Database import *
from Models.Images import *
from Models.api import *
from Utils.Hasher import HasherClass

router = APIRouter()

HasherObject = HasherClass()
database = DatabaseClass()


@router.get('/images', response_model=List[ImageWithAllInfo])
async def get_all_images():
    try:
        return await database.get_all_images()
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')

@router.post('/images')
async def add_image(image: UploadFile):
    hashedFileName = HasherObject.CreateImageFileNameHash(image.filename)
    async with aiofiles.open(Path() / "Content" / \
                    "images" / hashedFileName, 'wb') as image_file:
            await image_file.write(await image.read()) # type: ignore
    return { "imageId": await database.add_image(str(Path() / "static" / \
                        "images" / hashedFileName).replace("\\", "/")) }

@router.get('/sections/{SectionId}', response_model=List[ImageWithAllInfo])
async def get_Section_Images(SectionId: int):
    try:
        return await database.get_section_images(SectionId)
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database error')
