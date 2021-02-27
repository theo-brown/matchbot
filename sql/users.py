import sqlite3

database_file = 'database.db'

def create():  
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("""
                CREATE TABLE IF NOT EXISTS users(user_id INT PRIMARY KEY,
                                                 steam64_id INT)
                """)
    db.commit()
    db.close()
    
def clear():
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("DELETE FROM users")
    db.commit()
    db.close()

def display():
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("SELECT * FROM users")
    s = "user_id\t\t\tsteam64_id"
    for entry in csr.fetchall():
        s += "\n{}\t{}".format(*entry)
    db.close()
    return s

def add_steam64_id(user_id, steam64_id):
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("""
                INSERT OR REPLACE INTO users(user_id, steam64_id)
                 VALUES(?, ?)
                 """, (user_id, steam64_id))
    db.commit()
    db.close()
