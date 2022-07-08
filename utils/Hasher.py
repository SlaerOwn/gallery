import passlib.context


class HasherClass:
    def __init__(self):
        self.PasswordHashing = passlib.context.CryptContext(schemes=['bcrypt'], deprecated='auto')
        self.TokenGenerate = passlib.context.CryptContext(schemes=['des_crypt'], deprecated='auto')


    def PasswordHash(self, password: str) -> str:
        return self.PasswordHashing.hash(password)

    def CheckPassword(self, Hash: str, password: str) -> bool:
        return self.PasswordHashing.verify(password, Hash)


    def GetToken(self, Login: str, HashedPassword: str) -> str:
        return self.TokenGenerate.hash(Login) + HashedPassword

    def CheckToken(self, Token: str, Login: str, HashedPassword: str) -> bool:
        return self.TokenGenerate.verify(Token, Login + HashedPassword)
