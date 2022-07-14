import aiosqlite
import datetime
import asyncio


class UserExists(Exception): pass
class UserNotExists(Exception): pass
class PhotoNotExists(Exception): pass
class CommentNotExists(Exception): pass


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
            await db.execute("""CREATE TABLE IF NOT EXISTS photos(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    image BLOB NOT NULL,
                                    description TEXT,
                                    date TEXT
                                );
                            """)
            await db.commit()
            await db.execute("""CREATE TABLE IF NOT EXISTS comments(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    author INTEGER,
                                    photoid INTEGER,
                                    description TEXT,
                                    date TEXT
                                );
                            """)
            await db.commit()
            cursor = await db.execute('SELECT * FROM users WHERE login=?', ["admin"])
            res = list(map(lambda x: list(x), list(await cursor.fetchall())))
            if len(res) == 0:
                await db.execute("INSERT INTO users(login, password, role) VALUES(?, ?, ?);", ["admin", "admin", "admin"])
                await db.commit()
            self.database_inited = True

    async def request(self, request: str, inserts: list):
        if(not self.database_inited): await self.database_init()
        async with aiosqlite.connect(self.path_to_database) as db:
            async with db.execute(request, inserts) as cursor:
                result = list(map(lambda x: list(x), list(await cursor.fetchall())))
                await db.commit()
                return result

    async def create_user(self, login: str, password: str, role: str = 'default') -> int:
        if(len(await self.request('SELECT * FROM users WHERE login=?', [login])) == 0):
            await self.request("INSERT INTO users(login, password, role) VALUES(?, ?, ?);", [login, password, role])
            id = await self.request('SELECT userid FROM users WHERE login=?', [login])
            return id[0][0]
        else:
            raise UserExists()

    async def get_user(self, id: int) -> str:
        if(not len(await self.request('SELECT * FROM users WHERE userid=?', [id]))):
            raise UserNotExists()
        else:
            SQLResult = await self.request('SELECT userid, login, role FROM users WHERE userid=?', [id])
            return str(SQLResult[0])

    async def get_id(self, login: str) -> int:
        if not len(await self.request('SELECT * FROM users WHERE login=?', [login])):
            raise UserNotExists()
        else:
            SQLResult = await self.request('SELECT userid FROM users WHERE login=?', [login])
            return SQLResult[0][0]

    async def get_password(self, id: int) -> str:
        if(not len(await self.request('SELECT * FROM users WHERE userid=?', [id]))):
            raise UserNotExists()
        else:
            SQLResult = await self.request('SELECT password FROM users WHERE userid=?', [id])
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

    async def add_photo(self, image: str, description: str) -> None:
        date = str(datetime.datetime.now())
        await self.request("INSERT INTO photos(image, description, date) VALUES(?, ?, ?);", [image, description, date])

    async def get_photo(self, id: int):
        if(not len(await self.request('SELECT * FROM photos WHERE id=?', [id]))):
            raise PhotoNotExists()
        else:
            photo_data = await self.request('SELECT image FROM photos WHERE id=?', [id])
            return photo_data

    async def get_all_photos(self):
        if not len(await self.request('SELECT id FROM photos', [])):
            raise PhotoNotExists
        else:
            ids = await self.request('SELECT id FROM photos', [])
            return ids

    async def change_description(self, id: int, description: str) -> None:
        if(not len(await self.request('SELECT * FROM photos WHERE id=?', [id]))):
            raise PhotoNotExists()
        else:
            date = str(datetime.datetime.now())
            await self.request("Update photos set description=?, date=? where id=?", [description, date, id])

    async def delete_photo(self, id: int):
        if(not len(await self.request('SELECT * FROM photos WHERE id=?', [id]))):
            raise PhotoNotExists()
        else:
            await self.request('DELETE FROM photos WHERE id=?', [id])

    async def add_comment(self, author: int, photo: int, comment: str):
        if(not len(await self.request('SELECT * FROM users WHERE userid=?', [author]))):
            raise UserNotExists()
        if(not len(await self.request('SELECT * FROM photos WHERE id=?', [photo]))):
            raise PhotoNotExists()
        else:
            date = str(datetime.datetime.now())
            await self.request("INSERT INTO comments(author, photoid, description, date) VALUES(?, ?, ?, ?);", [author, photo, comment, date])

    async def change_comment(self, commentid: int, comment: str):
        if(not len(await self.request('SELECT * FROM comments WHERE id=?', [commentid]))):
            raise CommentNotExists()
        else:
            date = str(datetime.datetime.now())
            await self.request("Update comments set description=?, date=? where id=?", [comment, date, commentid])

    async def delete_comment(self, id: int):
        if(not len(await self.request('SELECT * FROM comments WHERE id=?', [id]))):
            raise CommentNotExists()
        else:
            await self.request('DELETE FROM comments WHERE id=?', [id])

    async def get_comments(self, photoid: int):
        if(not len(await self.request('SELECT * FROM photos WHERE id=?', [photoid]))):
            raise PhotoNotExists()
        else:
            return await self.request('SELECT * FROM comments WHERE photoid=?', [photoid])
