from fastapi import APIRouter, HTTPException
from Database.Database import *
from Models.api import NeedToken
from Models.Admin import *
from Utils.Hasher import HasherClass

router = APIRouter()

HasherObject = HasherClass()
Database = DatabaseClass()


@router.put('/about', status_code=200)
async def edit_info(user: NeedToken, info: EditInfo):
    try:
        password = await Database.get_password()
        if HasherObject.CheckToken(user.token, password):
            await Database.edit_info(info.info)
        else:
            raise HTTPException(status_code=403, detail='Bad Token')
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')


@router.get('/about', status_code=200)
async def AdminInfo():
    try:
        Admin = await Database.get_admin()
        return {'Admin': Admin}
    except DatabaseError:
        return HTTPException(status_code=500, detail='Database Error')
