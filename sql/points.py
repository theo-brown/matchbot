import sqlite3
from operator import itemgetter

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
    s = "user_id\tleaderboard_id\tpoints"
    for entry in csr.fetchall():
        s += "\n{}\t{}\t{}".format(*entry)
    db.close()
    return s

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
    
def get_list(leaderboard_id):
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("SELECT user_id, points FROM points WHERE leaderboard_id=? \
                ORDER BY points", (leaderboard_id,))
    # Get the values as a list of lists [user_id, points]
    l = [list(i) for i in csr.fetchall()]
    # Sort in descending order by points (index 1)
    l.sort(reverse=True, key=itemgetter(1))
    # Rank by points, assigning same rank to ties
    # Get a list starting at 1, of length equal to len(l)
    ranks = list(range(1, len(l)+1))
    for i in range(len(l)-1):
        # If the next users points are the same as this one, set them equal
        if l[i+1][1] == l[i][1]:
            ranks[i+1] = ranks[i]
    db.close()
    return list(zip(ranks, [i[0] for i in l], [i[1] for i in l]))