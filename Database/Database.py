import aiosqlite
import datetime
import aiofiles
import os
import asyncio

class UserExists(Exception): pass
class UserNotExists(Exception): pass

class DatabaseClass:
    def __init__(self):
        self.path_to_database = "database.db"
        self.database_inited = False

    async def database_init(self):
        async with aiosqlite.connect(self.path_to_database) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS users(
                                    userid INTEGER PRIMARY KEY AUTOINCREMENT,
                                    login TEXT UNIQUE,
                                    password TEXT,
                                    role TEXT
                                );
                            """)
            await db.commit()
            self.database_inited = True

    async def request(self, request: str, inserts: list[str]):
        if(not self.database_inited): await self.database_init()
        async with aiosqlite.connect(self.path_to_database) as db:
            async with db.execute(request, inserts) as cursor:
                result = list(map(lambda x: list(x), list(await cursor.fetchall())))
                await db.commit()
                return result

    async def create_user(self, login: str, password: str, role: str = 'default') -> None:
        if(len(await self.request('SELECT * FROM users WHERE login=?', [login])) == 0):
            await self.request("INSERT INTO users(login, password, role) VALUES(?, ?, ?);", [login, password, role])
        else:
            raise UserExists()

    async def get_user(self, login: str) -> str:
        if(not len(await self.request('SELECT * FROM users WHERE login=?', [login]))):
            raise UserNotExists()
        else:
            SQLResult = await self.request('SELECT userid, login, role FROM users WHERE login=?', [login])
            return str(SQLResult[0])

    async def get_password(self, login: str) -> str:
        if(not len(await self.request('SELECT * FROM users WHERE login=?', [login]))):
            raise UserNotExists()
        else:
            SQLResult = await self.request('SELECT password FROM users WHERE login=?', [login])
            return str(SQLResult[0][0])

    
    async def delete_user(self, id: int) -> None:
        if(not len(await self.request('SELECT * FROM users WHERE userid=?', [id]))):
            raise UserNotExists()
        else:
            await self.request('DELETE FROM users WHERE userid=?', [id])

    async def is_writer(self, id: int) -> bool:
        if(not len(await self.request('SELECT * FROM users WHERE userid=?', [id]))):
            raise UserNotExists()
        else:
            role = await self.request('SELECT role FROM users WHERE userid=?', [id])    
            if role[0][0] == "default":
                return False
            else:
                return True  

class DatabasePhoto:
    def __init__(self):
        self.path_to_database = "database.db"
        self.database_inited = False

    async def database_init(self):
        async with aiosqlite.connect(self.path_to_database) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS photos(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    image BLOB NOT NULL,
                                    description TEXT,
                                    date TEXT
                                );
                            """)
            await db.commit()
            self.database_inited = True

    async def request(self, request: str, inserts: list):
        if(not self.database_inited): await self.database_init()
        async with aiosqlite.connect(self.path_to_database) as db:
            async with db.execute(request, inserts) as cursor:
                result = list(map(lambda x: list(x), list(await cursor.fetchall())))
                await db.commit()
                return result

    async def convert_to_blob(self, filename):
        async with aiofiles.open(filename, 'rb') as file:
            blob_data = await file.read()
        return blob_data

    async def convert_from_blob(self, data, filename):
        async with aiofiles.open(filename, 'wb') as file:
            await file.write(data)
        return file

    async def add_photo(self, image, description: str) -> None:
        photo = await self.convert_to_blob(image)
        date = str(datetime.datetime.now())
        await self.request("INSERT INTO photos(image, description, date) VALUES(?, ?, ?);", [photo, description, date])

    async def get_photo(self, id: int):
        if(not len(await self.request('SELECT * FROM photos WHERE id=?', [id]))):
            raise UserNotExists()
        else:
            photo_data = await self.request('SELECT image FROM photos WHERE id=?', [id])
            photo_path = ("Photos/" + str(id) + ".jpg")
            photo = await self.convert_from_blob(photo_data[0][0], photo_path)
            return photo_data
