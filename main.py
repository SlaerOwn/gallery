from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from Database.Database import DatabaseConnectionError, DatabaseBaseClass
from Routes import *
from Utils.Hasher import HasherClass


app = FastAPI()
database = DatabaseBaseClass()
HasherObject = HasherClass()


@app.on_event("startup")  # type: ignore
async def startup_server():
    if not await database.database_init():
        raise DatabaseConnectionError()


@app.on_event("shutdown")  # type: ignore
async def shutdown_server():
    await database.database_uninit()

app.mount("/static/", StaticFiles(directory="Content"), name="static")
app.include_router(Admin.router)
app.include_router(Images.router)
app.include_router(TagsAndSections.router)