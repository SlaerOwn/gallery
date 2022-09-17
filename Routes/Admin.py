from fastapi import APIRouter, HTTPException
from typing import List

from Database.Database import *
from Models.Admin import CheckToken, EditInfo
from Utils.Hasher import HasherClass
from Models.api import *
from Models.Images import *

router = APIRouter()

HasherObject = HasherClass()
database = DatabaseClass()

@router.post('/admin/token', status_code=200)
async def check_token(body: CheckToken):
    try:
        hashed_password = await database.get_password()
        try:
            token_correct = HasherObject.CheckToken(body.token, hashed_password)
        except Exception: raise HTTPException(status_code=401)
        if(token_correct):
            return
        else:
            raise HTTPException(status_code=401)
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')



@router.post('/admin/section', status_code=200)
async def create_Section(Section: CreateSectionFields, user: NeedToken):
    try:
        hashed_password = await database.get_password()
        hash = str(hashed_password['hashOfPassword'])
        if HasherObject.CheckToken(user.token, hash):
            await database.create_section(Section.section, Section.includedTags)
        else:
            raise HTTPException(status_code=401, detail='Bad Token')
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')


@router.delete('/admin/section', status_code=200)
async def delete_Section(SectionId: int, user: NeedToken):
    try:
        hashed_password = await database.get_password()
        hash = str(hashed_password['hashOfPassword'])
        if HasherObject.CheckToken(user.token, hash):
            try:
                await database.delete_section(SectionId)
            except SectionNotFound:
                raise HTTPException(status_code=404, detail='Section not Found')
        else:
            raise HTTPException(status_code=401, detail='Bad Token')
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')


@router.put('/about', status_code=200)
async def edit_info(user: NeedToken, info: EditInfo):
    try:
        password = await database.get_password()
        hash = str(password['hashOfPassword'])
        if HasherObject.CheckToken(user.token, hash):
            await database.edit_info(info.info)
        else:
            raise HTTPException(status_code=403, detail='Bad Token')
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')


@router.get('/about', status_code=200)
async def AdminInfo():
    try:
        Admin = await database.get_admin()
        return {'Admin': Admin}
    except DatabaseError:
        return HTTPException(status_code=500, detail='Database Error')


@router.post('/authorization', response_model=SuccessAuthorizationResponse)
async def authorization(password: Authorization):
    try:
        hashed_password = await database.get_password()
        hash = str(hashed_password)
        if HasherObject.CheckPassword(hash, password.password):
            return {
                'token': HasherObject.GetToken(hash)
            }
        else:
            raise HTTPException(
                status_code=401,
                detail='Wrong Password'
            )
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')


@router.post('/admin/tag', status_code=200)
async def create_tag(Tag: CreateTagFields, user: NeedToken):
    try:
        hashed_password = await database.get_password()
        hash = str(hashed_password['hashOfPassword'])
        if HasherObject.CheckToken(user.token, hash):
            await database.create_tag(Tag.tag)
        else:
            raise HTTPException(status_code=401, detail='Bad Token')
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')


@router.delete('/admin/tag', status_code=200)
async def delete_tag(tagId: int, user: NeedToken):
    try:
        hashed_password = await database.get_password()
        hash = str(hashed_password['hashOfPassword'])
        if HasherObject.CheckToken(user.token, hash):
            try:
                await database.delete_tag(tagId)
            except TagNotFound:
                raise HTTPException(status_code=404, detail='Tag not Found')
        else:
            raise HTTPException(status_code=401, detail='Bad Token')
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')


@router.post('/admin', status_code=200)
async def create_image(image: CreateImageFields, user: NeedToken):
    hashed_password = await database.get_password()
    hash = str(hashed_password['hashOfPassword'])
    if HasherObject.CheckToken(user.token, hash):
        await database.add_photo(image.image, image.tags)
    else:
        raise HTTPException(status_code=401, detail='Bad Token')