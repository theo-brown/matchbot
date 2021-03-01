import sqlite3
from operator import itemgetter

database_file = 'database.db'

def create():  
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("""
                CREATE TABLE IF NOT EXISTS 
                pickem_points(pickem_channel_id INTEGER,
                        user_id INTEGER,
                        points INTEGER)
                """)
    csr.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS unique_pickem_user_index 
                ON pickem_points(pickem_channel_id, user_id)
                """)
    db.commit() 
    db.close()
    
def clear():
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("DELETE FROM pickem_points")
    db.commit()
    db.close()

def display():
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("SELECT * FROM pickem_points")
    s = "pickem_channel_id\tuser_id\tpoints"
    for entry in csr.fetchall():
        s += "\n{}\t{}\t{}".format(*entry)
    db.close()
    return s

def add_row(pickem_channel_id, user_id, points):
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("""
                INSERT INTO pickem_points(pickem_channel_id, user_id, points)
                 VALUES(?, ?, ?) 
                ON CONFLICT(pickem_channel_id, user_id)
                 DO UPDATE SET points = points + excluded.points
                 """, (pickem_channel_id, user_id, points))
    db.commit()
    db.close()

def delete_row(pickem_channel_id, user_id):
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("""
                DELETE FROM pickem_points 
                 WHERE pickem_channel_id=? AND user_id=?
                 """, (pickem_channel_id, user_id))
    db.commit()
    db.close()

def add_points(pickem_channel_id, user_id, points):
    add_row(pickem_channel_id, user_id, points)

def set_points(pickem_channel_id, user_id, points):
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("""
                INSERT INTO pickem_points(pickem_channel_id, user_id, points)
                 VALUES(?, ?, ?) 
                ON CONFLICT(pickem_channel_id, user_id)
                 DO UPDATE SET points = excluded.points
                 """, (pickem_channel_id, user_id, points))
    db.commit()
    db.close()

def increment(pickem_channel_id, *user_ids):
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.executemany("""
                    INSERT INTO pickem_points(pickem_channel_id, user_id, points)
                     VALUES (?, ?, 1)
                    ON CONFLICT(pickem_channel_id, user_id)
                     DO UPDATE SET points = points + 1
                    """, [(pickem_channel_id, user_id) for user_id in user_ids])
    db.commit()
    db.close()

def get_list(pickem_channel_id):
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("""
                SELECT user_id, points FROM pickem_points 
                 WHERE pickem_channel_id=?
                ORDER BY points
                """, (pickem_channel_id,))
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

def get_message(pickem_channel_id):
    s = "<#{}>\n**Pick'em Predictions Leaderboard**".format(pickem_channel_id)
    for i in get_list(pickem_channel_id):
        s += "\n{}. <@{}> ({}pts)".format(*i)
    return s
