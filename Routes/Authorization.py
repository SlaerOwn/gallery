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
            detail='username is occupied'
        )