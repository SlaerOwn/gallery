import sqlite3


class UserExists(Exception): pass


class DatabaseClass:
    def __init__(self):
        self.connect = sqlite3.connect('database.db')
        self.cur = self.connect.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users(
                userid INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE,
                password TEXT
            );
        """)
        self.connect.commit()

    def create_user(self, login: str, password: str) -> None:
        info = self.cur.execute('SELECT * FROM users WHERE login=?', (login,))
        if info.fetchone() is None:
            user = (login, password)
            self.cur.execute("INSERT INTO users(login, password) VALUES(?, ?);", user)
        else:
            raise UserExists()
        self.connect.commit()


    def get_user(self, login):
        info = self.cur.execute('SELECT password FROM users WHERE login=?', (login,))
        if info.fetchone() is None:
            print("Такого пользователя не существует!")  # в будущем сообщение об ошибке
        else:
            self.cur.execute('SELECT password FROM users WHERE login=?', (login,))
            password = self.cur.fetchone()
            print(password[0])
            return password

