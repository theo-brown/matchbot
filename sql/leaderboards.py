import sqlite3
from operator import itemgetter

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
    print("id\tname\tguild_id")
    for entry in csr.fetchall():
        print("\n{}\t{}\t{}".format(*entry))
    db.close()

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