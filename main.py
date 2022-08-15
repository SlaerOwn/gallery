from typing import List
from fastapi import FastAPI
import uvicorn #type: ignore
from Database.Database import DatabaseClass, DatabaseConnectionError
from Models.Images import ImageInDatabase
from Routes import *

app = FastAPI()
database = DatabaseClass()

@app.on_event("startup") #type: ignore
async def startup_server():
    if(not await database.database_init()):
        raise DatabaseConnectionError()
@app.on_event("shutdown") #type: ignore
async def shutdown_server():
    await database.database_uninit()

#app.include_router(Admin.router)
#app.include_router(Images.router)
#app.include_router(TagsAndSections.router)

@app.get("/test", response_model=List[ImageInDatabase])
async def test():
    return await database.get_all_photos()
