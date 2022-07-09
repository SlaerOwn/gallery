from fastapi import FastAPI
import uvicorn  # type: ignore
from Routes import *

app = FastAPI()

app.include_router(Authorization.router)
