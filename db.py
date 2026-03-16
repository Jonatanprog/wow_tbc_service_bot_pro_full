
import sqlite3

conn = sqlite3.connect("bot.db")
c = conn.cursor()

def init_db():
    c.execute('''
    CREATE TABLE IF NOT EXISTS professions(
        user_id INTEGER,
        character TEXT,
        profession TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        profession TEXT,
        description TEXT
    )
    ''')
    conn.commit()

def add_profession(user_id, character, profession):
    c.execute("INSERT INTO professions VALUES (?,?,?)", (user_id, character, profession))
    conn.commit()

def list_professions(profession):
    c.execute("SELECT user_id, character FROM professions WHERE profession=?", (profession,))
    return c.fetchall()

def create_order(user_id, profession, description):
    c.execute("INSERT INTO orders(user_id, profession, description) VALUES (?,?,?)",
              (user_id, profession, description))
    conn.commit()

def list_orders():
    c.execute("SELECT id, profession, description FROM orders")
    return c.fetchall()
