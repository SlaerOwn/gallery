from fastapi import APIRouter, HTTPException
from Database.Database import *
from Models.api import NeedIDAndToken
from Models.Admin import *
from Utils.Hasher import HasherClass

router = APIRouter()

HasherObject = HasherClass()
Database = DatabaseClass()


@router.put('/admin')
async def edit_writers(user: NeedIDAndToken, change: ChangeRoleFields):
    try:
        if await Database.is_admin(user.user_id):
            password = await Database.get_password(user.user_id)
            if HasherObject.CheckToken(user.token, user.user_id, password):
                await Database.change_role(change.user_id, change.role)
            else:
                raise HTTPException(status_code=403, detail='Bad Token')
        else:
            raise HTTPException(status_code=403, detail='No permissions')
    except UserNotExists:
        raise HTTPException(status_code=404, detail='User not found')


@router.get('/admin', status_code=200)
async def get_writers(user: NeedIDAndToken):
    try:
        if await Database.is_admin(user.user_id):
            password = await Database.get_password(user.user_id)
            if HasherObject.CheckToken(user.token, user.user_id, password):
                await Database.get_writers()
            else:
                raise HTTPException(status_code=403, detail='Bad Token')
        else:
            raise HTTPException(status_code=403, detail='No permissions')
    except UserNotExists:
        raise HTTPException(status_code=404, detail='User not found')
