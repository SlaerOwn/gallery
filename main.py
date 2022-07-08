from fastapi import FastAPI, HTTPException
import uvicorn  # type: ignore
from multiprocessing import AuthenticationError
from Routes import Authorization
from utils.Hasher import *


Hasher = HasherClass()


app = FastAPI()


app.include_router(Authorization.router)

