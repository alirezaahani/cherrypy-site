import hashlib
import sqlite3

DB_NAME = './private/database.sqlite3'

def hasher(text):
    return hashlib.sha512(text.encode()).hexdigest()

con = sqlite3.connect(DB_NAME)
cur = con.cursor()

cur.execute('DROP TABLE IF EXISTS posts')
cur.execute('DROP TABLE IF EXISTS menu')
cur.execute('DROP TABLE IF EXISTS users')
cur.execute('DROP TABLE IF EXISTS allow')
con.commit()

cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        nickname TEXT UNIQUE
        )''')
cur.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nickname TEXT,
        text TEXT,
        title TEXT,
        date TEXT
        )''')
cur.execute('''CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        link TEXT
        )''')
cur.execute('''CREATE TABLE IF NOT EXISTS allow (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE
        )''')
con.commit()

username = password = nickname = ''

while len(username) < 3:
    username = input('Enter a username for login (At least 3 chars):')

while len(password) < 3:
    password = input('Enter a password for login (At least 3 chars):')

while len(nickname) < 3:
    nickname = input('Enter a nickname for login (At least 3 chars):')

cur.execute('INSERT INTO users (password,username,nickname) VALUES (?,?,?)',(hasher(password),username,nickname,))
cur.execute("INSERT INTO menu (link,text) VALUES ('/','Home')")
cur.execute("INSERT INTO menu (link,text) VALUES ('/login','Login')")
cur.execute("INSERT INTO menu (link,text) VALUES ('/signin','SignIn')")

con.commit()
con.close()