from fastapi import FastAPI, HTTPException
import uvicorn  # type: ignore
from fastapi.encoders import jsonable_encoder
from database import Database
from Authorization import *

users = {}

app = FastAPI()



@app.post('registration')
async def register(username: str, password: str) -> str:
    try:
        Authorization.register(username, password)
        return Hasher.GetToken(Hasher, username, password)
    except UserExists:
        raise HTTPException(
            status_code=409,
            detail='username is occupied'
        )


@app.post('/auth')
async def authorization(username: str, password: str) -> str:
    pass