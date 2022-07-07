import passlib.context


class Hasher:
    def __init__(self):
        self.PasswordHash = passlib.context.CryptContext(schemes=['bcrypt'], deprecated='auto')
        self.TokenGenerate = passlib.context.CryptContext(schemes=['des_crypt'], deprecated='auto')

    def PasswordHash(self, Password: str) -> str:
        return self.PasswordHash.hash(Password)

    def CheckPassword(self, Hash: str, Password: str) -> bool:
        return self.PasswordHash.verify(Password, Hash)


    def GetToken(self, Login: str, HashedPassword: str) -> str:
        return self.TokenGenerate.hash(Login + HashedPassword)

    def CheckToken(self, Token: str, Login: str, HashedPassword: str) -> bool:
        return self.TokenGenerate.verify(Token, Login + HashedPassword)
