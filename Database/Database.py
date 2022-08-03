from __future__ import annotations
from typing import Any

from databases import Database
import datetime
from Models.Admin import AdminInDatabase
from Utils import *

class DatabaseError(Exception): pass
class UserExists(DatabaseError): pass
class UserNotExists(DatabaseError): pass
class PhotoNotExists(DatabaseError): pass
class CommentNotExists(DatabaseError): pass

class DatabaseConnectionError(DatabaseError): pass
class DatabaseTransactionError(DatabaseError): pass

class DatabaseBaseClass:
    def __init__(self):
        self.path_to_database = "database.db"
        self.database_inited: bool = False
        self.Hasher = Hasher.HasherClass()
        self.connection_URL : str = "sqlite:///./database.db"
        self.database: Database | None = None

    async def database_init(self):
        self.database = Database(self.connection_URL)
        await self.database.connect()
        self.database_inited = True
        try:
            await self.request(
                'CREATE TABLE IF NOT EXISTS admin('\
                '    hashOfPassword TEXT PRIMARY KEY,'\
                '    aboutMe TEXT UNIQUE,'\
                '    avatar TEXT);'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS images('\
                '    imageId INTEGER PRIMARY KEY AUTOINCREMENT,'\
                '    image BLOB NOT NULL,'\
                '    tags TEXT);'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS tags('\
                '    tagId INTEGER PRIMARY KEY AUTOINCREMENT,'\
                '    tag TEXT);'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS sections('\
                '    sectionId INTEGER PRIMARY KEY AUTOINCREMENT,'\
                '    section TEXT,'\
                '    includedTags TEXT);'
            )
        except Exception as e:
            print(e)
            self.database_inited = False
        finally:
            return self.database_inited
    
    async def database_uninit(self):
        if(self.database): await self.database.disconnect()

    async def request(self, request: str, *args: dict[str, str | int], **other: str | int):
        if(not self.database_inited or self.database == None):
            if(not await self.database_init()):
                raise DatabaseConnectionError()
        try:
            common_dict = {key: value for dict in [*args, other] for key, value in dict.items()}
            if("select" not in request.lower()):
                await self.database.execute(request) #type: ignore
                return None
            else:
                response: list[dict[str, Any]] = \
                    list(map(
                        lambda x: dict(x), #type: ignore
                        await self.database.fetch_all(request, common_dict) #type: ignore
                    ))
                return response
        except Exception as e:
            print(f"Request error - {e}")
            raise DatabaseTransactionError()


class DatabaseClass(DatabaseBaseClass):

    # --- REQUESTS ---

    getAdminRequest = "SELECT * FROM admin"



    # --- FUNCTIONS ---

    async def get_admin(self) -> AdminInDatabase | None:
        response = await self.request(self.getAdminRequest)
        return None if response is None else response[0] #type: ignore

'''
    async def create_user(self, login: str, password: str, role: str = 'default', fcs: str = "none", pp: str = "none") -> int:
        if(len(await self.request('SELECT * FROM users WHERE login=?', [login])) == 0):
            await self.request("INSERT INTO users(login, password, role, fcs, pp) VALUES(?, ?, ?, ?, ?);", [login, password, role, fcs, pp])
            id = await self.request('SELECT userid FROM users WHERE login=?', [login])
            return id[0][0]
        else:
            raise UserExists()

    async def get_user(self, id: int):
        if(not len(await self.request('SELECT * FROM users WHERE userid=?', [id]))):
            raise UserNotExists()
        else:
            SQLResult = (await self.request('SELECT userid, login, role, fcs, pp FROM users WHERE userid=?', [id]))[0]
            return {
                "user_id": SQLResult[0],
                "login": SQLResult[1],
                "role": SQLResult[2],
                "fcs": SQLResult[3],
                "pp": SQLResult[4],
            }

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
            role = (await self.request('SELECT role FROM users WHERE userid=?', [id]))[0][0]
            if role == "writer" or role == "admin":
                return True
            else:
                return False

    async def is_admin(self, id: int) -> bool:
        if(not len(await self.request('SELECT * FROM users WHERE userid=?', [id]))):
            raise UserNotExists()
        else:
            role = await self.request('SELECT role FROM users WHERE userid=?', [id])
            if role[0][0] == "admin":
                return True
            else:
                return False

    async def change_role(self, id: int, role: str):
        if(not len(await self.request('SELECT * FROM users WHERE userid=?', [id]))):
            raise UserNotExists()
        else:
            await self.request("Update users set role=? where id=?", [role, id])

    async def edit_info(self, id: int, fcs: str, pp: str):
        if(not len(await self.request('SELECT * FROM users WHERE userid=?', [id]))):
            raise UserNotExists()
        else:
            await self.request("UPDATE users set fcs=?, pp=? where userid=?", [fcs, pp, id])

    async def add_photo(self, image: str, description: str) -> None:
        date = str(datetime.datetime.now())
        await self.request("INSERT INTO photos(image, description, date) VALUES(?, ?, ?);", [image, description, date])

    async def get_photo(self, id: int):
        if(not len(await self.request('SELECT * FROM photos WHERE id=?', [id]))):
            raise PhotoNotExists()
        else:
            photo_data = \
                (await self.request('SELECT image, description, date FROM photos WHERE id=?', [id]))[0]
            return {
                "id": str(photo_data[0]),
                "image": str(photo_data[0]),
                "description": str(photo_data[1]),
                "date": str(photo_data[2]),
            }

    async def get_all_photos(self):
        if not len(await self.request('SELECT id FROM photos', [])):
            raise PhotoNotExists
        else:
            photos = await self.request('SELECT * FROM photos', [])
            return [
                {
                    "id": str(photo_data[0]),
                    "image": str(photo_data[1]),
                    "description": str(photo_data[2]),
                    "date": str(photo_data[3]),
                } for photo_data in photos
            ]

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
            await self.request("INSERT INTO comments(author, photoid, comment, date) VALUES(?, ?, ?, ?);", [author, photo, comment, date])

    async def change_comment(self, commentid: int, comment: str):
        if(not len(await self.request('SELECT * FROM comments WHERE id=?', [commentid]))):
            raise CommentNotExists()
        else:
            date = str(datetime.datetime.now())
            await self.request("Update comments set comment=?, date=? where id=?", [comment, date, commentid])

    async def delete_comment(self, id: int):
        if(not len(await self.request('SELECT * FROM comments WHERE id=?', [id]))):
            raise CommentNotExists()
        else:
            await self.request('DELETE FROM comments WHERE id=?', [id])

    async def get_comments(self, photoid: int):
        if(not len(await self.request('SELECT * FROM photos WHERE id=?', [photoid]))):
            raise PhotoNotExists()
        else:
            comments = await self.request('SELECT * FROM comments JOIN users ON author = userid WHERE photoid=?', [photoid])
            return [
                {
                    "id": comment[0],
                    "photoid": comment[2],
                    "comment": comment[3],
                    "date": comment[4],
                    "author": {
                        "user_id": comment[5],
                        "login": comment[6],
                        "role": comment[10],
                        "fcs": comment[7],
                        "pp": comment[8],
                    }
                } for comment in comments
            ]
'''