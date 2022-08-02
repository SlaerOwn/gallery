from fastapi import APIRouter, HTTPException
from Database.Database import *
from Models.api import *
from Utils.Hasher import HasherClass

router = APIRouter()

HasherObject = HasherClass()
Database = DatabaseClass()


@router.post('/authorization', response_model=SuccessAuthorizationResponse)
async def authorization(password: Authorization):
    try:
        hashed_password = await Database.get_password()
        if HasherObject.CheckPassword(hashed_password, password):
            return {
                'token': HasherObject.GetToken(hashed_password)
            }
        else:
            raise HTTPException(
                status_code=401,
                detail='Wrong Password'
            )
    except DatabaseError:
        raise HTTPException(status_code=500, detail='Database Error')
