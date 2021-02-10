import sqlite3

db = sqlite3.connect('tournabot.db')

csr = db.cursor()


csr.execute("CREATE TABLE IF NOT EXISTS leaderboards(id INTEGER PRIMARY KEY,\
                                                     name TEXT,\
                                                     guild_id INTEGER)")

csr.execute("CREATE TABLE IF NOT EXISTS points(user_id INTEGER,\
                                               leaderboard_id INTEGER,\
                                               points INTEGER)")

csr.execute("CREATE TABLE IF NOT EXISTS channelmap(guild_id INTEGER,\
                                                   listen_channel_id INTEGER,\
                                                   send_channel_id INTEGER)")

csr.execute("CREATE TABLE IF NOT EXISTS autodelete(guild_id INTEGER,\
                                                   autodelete_channel_id INTEGER")

db.commit()

db.close()
