from fastapi import APIRouter, HTTPException
from typing import List

from Database.Database import *
from Utils.Hasher import HasherClass
from Models.api import *
from Models.Images import *

router = APIRouter()


HasherObject = HasherClass()
Database = DatabaseClass()


@router.post('/admin', status_code=200)
async def create_image(image: CreateImageFields, user: NeedToken):
    hashed_password = await Database.get_password()
    if HasherObject.CheckToken(user.token, hashed_password):
        await Database.add_photo(image.image, image.tags)
    else:
        raise HTTPException(status_code=401, detail='Bad Token')


@router.post('/admin', status_code=200)
async def create_tag(Tag: CreateTagFields, user: NeedToken):
    try:
        hashed_password = await Database.get_password()
        if HasherObject.CheckToken(user.token, hashed_password):
            await Database.Create_tag(Tag.tag)
        else:
            raise HTTPException(status_code=401, detail='Bad Token')
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')


@router.delete('/admin', status_code=200)
async def delete_tag(tagId: int, user: NeedToken):
    try:
        hashed_password = await Database.get_password()
        if HasherObject.CheckToken(user.token, hashed_password):
            try:
                await Database.delete_tag(tagId)
            except TagNotFound:
                raise HTTPException(status_code=404, detail='Tag not Found')
        else:
            raise HTTPException(status_code=401, detail='Bad Token')
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')


@router.post('/admin', status_code=200)
async def create_Section(Section: CreateSectionFields, user: NeedToken):
    try:
        hashed_password = await Database.get_password()
        if HasherObject.CheckToken(user.token, hashed_password):
            await Database.Create_Section(Section.section, Section.includedTags)
        else:
            raise HTTPException(status_code=401, detail='Bad Token')
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')


@router.delete('/admin', status_code=200)
async def delete_Section(SectionId: int, user: NeedToken):
    try:
        hashed_password = await Database.get_password()
        if HasherObject.CheckToken(user.token, hashed_password):
            try:
                await Database.delete_Section(SectionId)
            except SectionNotFound:
                raise HTTPException(status_code=404, detail='Section not Found')
        else:
            raise HTTPException(status_code=401, detail='Bad Token')
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')