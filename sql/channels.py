import sqlite3

def create():  
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("CREATE TABLE IF NOT EXISTS channels(channel_id INTEGER PRIMARY KEY,\
                                                     send_channel_id INTEGER,\
                                                     autodelete INTEGER)")
    db.commit()
    db.close()
    
def clear():
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("DELETE FROM channels")
    db.commit()
    db.close()
    
def display():
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("SELECT * FROM channels")
    print("channel_id\tsend_channel_id\tautodelete")
    for entry in csr.fetchall():
        print("\n{}\t{}\t{}\t{}".format(*entry))

def add_row(channel_id, guild_id, send_channel_id=0, autodelete=0):
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("INSERT INTO channels(channel_id, send_channel_id, autodelete)\
                 VALUES(?, ?, ?)", (channel_id, send_channel_id, autodelete))
    db.commit()
    db.close()

def delete_row(channel_id):
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("DELETE FROM channels WHERE channel_id=?", (channel_id,))
    db.commit()
    db.close()

def set_autodelete(channel_id, autodelete: bool):
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("UPDATE channels SET autodelete =? WHERE channel_id =?",
                (int(autodelete), channel_id))
    db.commit()
    db.close()

def set_sendchannel(channel_id, send_channel_id):
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("UPDATE channels SET send_channel_id =? \
                WHERE channel_id =?",
                (send_channel_id, channel_id))
    db.commit()
    db.close()

def get_autodelete(channel_id):
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("SELECT autodelete FROM channels WHERE channel_id =?",
                (channel_id,))
    autodelete = csr.fetchone()[0]
    db.close()
    return bool(autodelete)

def get_send_channel(channel_id):
    db = sqlite3.connect('tournabot.db')
    csr = db.cursor()
    csr.execute("SELECT send_channel_id FROM channels WHERE channel_id =?",
                (channel_id,))
    send_channel_id = csr.fetchone()[0]
    db.close()
    return send_channel_id