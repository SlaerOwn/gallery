from fastapi import FastAPI
import uvicorn  # type: ignore
from Routes import *

app = FastAPI()

app.include_router(Authorization.router)
app.include_router(Images.router)
app.include_router(Comments.router)
app.include_router(Admin.router)
app.include_router(UserInfo.router)