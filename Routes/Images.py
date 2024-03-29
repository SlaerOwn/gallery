from fastapi import APIRouter, HTTPException, UploadFile
import aiofiles
from pathlib import Path
from PIL import Image

from Database.Database import *
from Models.Images import *
from Models.api import *
from Utils.Hasher import HasherClass

router = APIRouter()

HasherObject = HasherClass()
database = DatabaseClass()
Env = EnvClass()

@router.get('/images', response_model=List[ImageWithAllInfo])
async def get_all_images():
    try:
        return await database.get_all_images()
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')

@router.get('/images/{imageId}', response_model=ImageWithAllInfo)
async def get_image(imageId: int):
    try:
        return await database.get_image(imageId)
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')

@router.post('/images')
async def add_image(upload_image: UploadFile):
    hashedFileName = HasherObject.CreateImageFileNameHash(upload_image.filename)
    async with aiofiles.open(Path() / "Content" / "images" / \
                    "full_size" / hashedFileName, 'wb') as image_file:
            await image_file.write(await upload_image.read()) # type: ignore
    image = Image.open(str(Path() / "Content" / "images" \
        / "full_size" / hashedFileName).replace("\\", "/"))
    compressed_coefficient = (image.size[0]*image.size[1])/(Env.env["GALLERY_PREVIEW_TARGET_SIZE"])
    compressed_image = image.resize(
        (
            int(image.size[0]/(compressed_coefficient if compressed_coefficient > 1 else 1)), 
            int(image.size[1]/(compressed_coefficient if compressed_coefficient > 1 else 1))
        )
    )
    compressed_image.save(Path() / "Content" / "images" / "previews" / hashedFileName)
    return {"imageId": await database.add_image(str(hashedFileName)) }

@router.get('/sections/{SectionId}', response_model=List[ImageWithAllInfo])
async def get_Section_Images(SectionId: int):
    try:
        return await database.get_section_images(SectionId)
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database error')
