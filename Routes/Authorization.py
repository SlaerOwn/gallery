from fastapi import APIRouter, HTTPException
from Database.Database import *
from Utils.Hasher import HasherClass
from Models.api import TokenResponse

router = APIRouter()

Hasher = HasherClass()
Database = DatabaseClass()

@router.post('/registration', response_model=TokenResponse)
async def register(username: str, password: str):
    try:
        password = Hasher.PasswordHash(password)
        await Database.create_user(username, password)
        return {
            "token": Hasher.GetToken(username, password)
        }
    except UserExists:
        raise HTTPException(
            status_code=409,
            detail='Username is occupied'
        )

@router.post('/authorization', response_model=TokenResponse)
async def authorization(username: str, password: str):
    try:
        hashed_password = await Database.get_user(username)
    except UserNotExists:
        raise HTTPException(
            status_code=404,
            detail='User does not exist'
        )
    if hashed_password:
        if Hasher.CheckPassword(hashed_password, password):
            return {'token': Hasher.GetToken(username, hashed_password)}
        else:
            raise HTTPException(
                status_code=400,
                detail='Wrong Password'
            )
