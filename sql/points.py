import sqlite3

def create():  
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("CREATE TABLE IF NOT EXISTS points(user_id INTEGER,\
                                                   leaderboard_id INTEGER,\
                                                   points INTEGER)")
    db.commit()
    db.close()
    
def clear():
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("DELETE FROM points")
    db.commit()
    db.close()

def display():
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("SELECT * FROM points")
    print("user_id\tleaderboard_id\tpoints")
    for entry in csr.fetchall():
        print("\n{}\t{}\t{}".format(*entry))
    db.close()

def add_row(user_id, leaderboard_id, points):
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("INSERT INTO points(user_id, leaderboard_id, points)\
                 VALUES(?, ?, ?)", (user_id, leaderboard_id, points))
    db.commit()
    db.close()

def delete_row(user_id, leaderboard_id):
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("DELETE FROM points WHERE user_id=? AND leaderboard_id=?",
                (user_id, leaderboard_id))
    db.commit()
    db.close()

def add_points(user_id, leaderboard_id, points):
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("SELECT points FROM points WHERE user_id = ? AND leaderboard_id = ?",
                (user_id, leaderboard_id))
    points += csr.fetchone()[0]
    csr.execute("UPDATE points SET points =? \
                WHERE user_id =? AND leaderboard_id =?",\
                (points, user_id, leaderboard_id))
    db.commit()
    db.close()