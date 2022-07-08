from fastapi import APIRouter, HTTPException
from Database.database import *
from utils.Hasher import HasherClass
from models.api import TokenResponse


class DatabaseConnectionError(Exception): pass


class WrongPasswordError(Exception): pass


class DatabaseLoginExistsError(Exception): pass


router = APIRouter()

Hasher = HasherClass()
Database = DatabaseClass()


@router.post('/registration', response_model=TokenResponse)
async def register(username: str, password: str):
    try:
        password = Hasher.PasswordHash(password)
        Database.create_user(username, password)
        return {
            "token": Hasher.GetToken(username, password)
        }
    except UserExists:
        raise HTTPException(
            status_code=409,
            detail='username is occupied'
        )



@router.post('/authorization')
async def authorization(username: str, password: str):
    try:
        hashed_password = Database.get_user(username)
    except UserNotExists:
        return HTTPException(
            status_code=404,
            detail='User does not exist')
    if hashed_password:
        print(hashed_password, password)
        if Hasher.CheckPassword(hashed_password, password):
            return {'token': Hasher.GetToken(username, hashed_password)}
        else:
            return HTTPException(
                status_code=400,
                detail='Wrong Password'
        )