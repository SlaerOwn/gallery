from databases import Database
from fastapi import FastAPI
import uvicorn
from Database.Database import DatabaseClass, DatabaseConnectionError
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

@app.get("/test")
async def test():
    return await database.get_admin()