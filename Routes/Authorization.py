from fastapi import APIRouter, HTTPException
from Database.Database import *
from Models.api import *
from Utils.Hasher import HasherClass

router = APIRouter()

HasherObject = HasherClass()
Database = DatabaseClass()


@router.post('/authorization', response_model=SuccessAuthorizationResponse)
async def authorization(password: Authorization):
    hashed_password = await Database.get_password()
    if HasherObject.CheckPassword(hashed_password, password):
        return {
            'token': HasherObject.GetToken(hashed_password)
        }
    else:
        raise HTTPException(
            status_code=400,
            detail='Wrong Password'
        )
