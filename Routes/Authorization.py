from fastapi import APIRouter, HTTPException
from Database.Database import *
from Models.api import SuccessAuthorizationResponse
from Utils.Hasher import HasherClass

router = APIRouter()

HasherObject = HasherClass()
Database = DatabaseClass()


@router.post('/registration', response_model=SuccessAuthorizationResponse)
async def register(username: str, password: str):
    try:
        password = HasherObject.PasswordHash(password)
        user_id = await Database.create_user(username, password)
        print(HasherObject.GetToken(user_id, password))
        return {
            "token": HasherObject.GetToken(user_id, password),
            "user_id": user_id
        }
    except UserExists:
        raise HTTPException(
            status_code=409,
            detail='Username is occupied'
        )


@router.post('/authorization', response_model=SuccessAuthorizationResponse)
async def authorization(username: str, password: str):
    try:
        user_id = await Database.get_id(username)
        hashed_password = await Database.get_password(user_id)
        if hashed_password:
            if HasherObject.CheckPassword(hashed_password, password):
                return {
                    'token': HasherObject.GetToken(user_id, hashed_password),
                    'user_id': user_id
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail='Wrong Password'
                )
    except UserNotExists:
        raise HTTPException(
            status_code=404,
            detail='User does not exist'
        )
