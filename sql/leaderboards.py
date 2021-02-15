import sqlite3

def create():  
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("CREATE TABLE IF NOT EXISTS leaderboards(id INTEGER PRIMARY KEY,\
                                                         name TEXT,\
                                                         guild_id INTEGER)")
    db.commit()
    db.close()
    
def clear():
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("DELETE FROM leaderboards")
    db.commit()
    db.close()
    
def display():
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("SELECT * FROM leaderboards")
    s = "id\tname\tguild_id"
    for entry in csr.fetchall():
        s += "\n{}\t{}\t{}".format(*entry)
    db.close()
    return s

def add_row(leaderboard_name, guild_id):
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("SELECT MAX(id) FROM leaderboards")
    max_id = csr.fetchone()[0]
    leaderboard_id = (max_id + 1) if max_id is not None else 0
    csr.execute("INSERT INTO leaderboards(id, name, guild_id)\
                 VALUES(?, ?, ?)", (leaderboard_id, leaderboard_name, guild_id))
    db.commit()
    db.close()

def delete_row(leaderboard_id):
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("DELETE FROM leaderboards WHERE id=?", (leaderboard_id,))
    db.commit()
    db.close()
    
def get_id(leaderboard_name, leaderboard_guild_id):
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("SELECT id FROM leaderboards WHERE name=? AND guild_id=?",
                (leaderboard_name, leaderboard_guild_id))
    leaderboard_id = csr.fetchone()[0]
    db.close()
    return leaderboard_id
