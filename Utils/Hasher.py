import passlib.context


class HasherClass:
    def __init__(self):
        self.PasswordHasher = passlib.context.CryptContext(schemes=['bcrypt'], deprecated='auto')
        self.TokenGenerate = passlib.context.CryptContext(schemes=['des_crypt'], deprecated='auto')

    def PasswordHash(self, Password: str) -> str:
        return self.PasswordHasher.hash(Password)  # type: ignore

    def CheckPassword(self, Hash: str, Password: str) -> bool:
        return self.PasswordHasher.verify(Password, Hash)  # type: ignore

    def GetToken(self, Login: str, HashedPassword: str) -> str:
        return self.TokenGenerate.hash(Login + HashedPassword)  # type: ignore

    def CheckToken(self, Token: str, Login: str, HashedPassword: str) -> bool:
        return self.TokenGenerate.verify(Token, Login + HashedPassword)  # type: ignore
