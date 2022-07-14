from fastapi import APIRouter, HTTPException
from Database.Database import *
from Utils.Hasher import HasherClass
from Models.api import TokenResponse

router = APIRouter()

Hasher = HasherClass()
Database = DatabaseClass()


@router.post('/registration')
async def register(username: str, password: str):
    try:
        password = Hasher.PasswordHash(password)
        user_id = await Database.create_user(username, password)
        print(Hasher.GetToken(user_id, password))
        return {
            "token": Hasher.GetToken(user_id, password),
            "user_id": user_id
        }
    except UserExists:
        raise HTTPException(
            status_code=409,
            detail='Username is occupied'
        )


@router.post('/authorization')
async def authorization(username: str, password: str):
    try:
        user_id = await Database.get_id(username)
        hashed_password = await Database.get_password(user_id)
        if hashed_password:
            if Hasher.CheckPassword(hashed_password, password):
                return {'token': Hasher.GetToken(user_id, hashed_password),
                        'user_id': user_id}
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
