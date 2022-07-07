from database import *
from Hasher import Hasher


class DatabaseConnectionError(Exception): pass


class DatabaseLoginExistsError: pass


class Authorization:
    def register(self, username: str, password: str) -> object:
        try:
            password = Hasher.PasswordHash(password)
            Database.create_user(username, password)
        except UserExists:
            raise DatabaseLoginExistsError