import aiosqlite

class UserExists(Exception): pass

class DatabaseClass:
    def __init__(self):
        self.path_to_database = "database.db"
        self.database_inited = False

    async def database_init(self):
        async with aiosqlite.connect(self.path_to_database) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS users(
                                    userid INTEGER PRIMARY KEY AUTOINCREMENT,
                                    login TEXT UNIQUE,
                                    password TEXT
                                );
                            """)
            await db.commit()
            self.database_inited = True

    async def request(self, request: str, inserts: list[str]):
        if(not self.database_inited): await self.database_init()
        async with aiosqlite.connect(self.path_to_database) as db:
            async with db.execute(request, inserts) as cursor:
                result = cursor.fetchall()
                await db.commit()
                return result

    async def get_request(self, request: str, inserts: list[str]):
        if(not self.database_inited): await self.database_init()
        async with aiosqlite.connect(self.path_to_database) as db:
            async with db.execute(request, inserts) as cursor:
                result = cursor.fetchone()
                await db.commit()
                return result[0]

    async def create_user(self, login: str, password: str) -> None:
        if(await self.request('SELECT * FROM users WHERE login=?', [login, password]) is None):
            await self.request("INSERT INTO users(login, password) VALUES(?, ?);", [login, password])
        else:
            raise UserExists()

    async def get_user(self, login: str) -> None:
        if(await self.request('SELECT * FROM users WHERE login=?', [login]) is None):
            raise UserExists()
        else:
            await self.get_request('SELECT password FROM users WHERE login=?', [login])
