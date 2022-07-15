from fastapi import APIRouter, HTTPException
from Database.Database import *
from Models.api import NeedIDAndToken
from Utils.Hasher import HasherClass
from Models.UserInfo import UserInfoFields, GiveUser

router = APIRouter()

HasherObject = HasherClass()
Database = DatabaseClass()


@router.get('/userinfo/{user_ID}', status_code=200)
async def get_user(user_ID: int):
    user = await Database.get_user(user_ID)
    return {'user': user}


@router.put('/userinfo/{user_ID}', status_code=200)
async def edit_info(user: NeedIDAndToken, info: UserInfoFields):
    try:
        password = await Database.get_password(user.user_ID)
        if HasherObject.CheckToken(user.token, user.user_ID, password):
            Database.edit_info(info.user_ID, info.FIO, info.ProfilePicture)
        else:
            raise HTTPException(status_code=403, detail='Bad Token')
    except UserNotExists:
        return HTTPException(status_code=404, detail='User not found')
