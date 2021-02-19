import sqlite3

database_file = 'tournabot.db'

def create():  
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("""
                CREATE TABLE IF NOT EXISTS channels(channel_id INT PRIMARY KEY,
                                                    redirect_channel_id INT,
                                                    autodelete INT DEFAULT 0)
                """)
    db.commit()
    db.close()
    
def clear():
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("DELETE FROM channels")
    db.commit()
    db.close()

def display(columns=''):
    if columns == '':
        return display_all()
    elif columns == "autodelete":
        return display_autodelete()
    elif columns == "redirect":
        return display_redirect()
    else:
        return "Error: expected an argument from ['', 'autodelete', 'redirect']"
    
def display_all():
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("SELECT * FROM channels")
    s = "```\nchannel_id\t\t\tredirect_channel_id\tautodelete"
    for entry in csr.fetchall():
        s+= "\n{}\t{}\t{}".format(*entry)
    s += "\n```"
    db.close()
    return s
    
def display_autodelete():
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("SELECT channel_id, autodelete FROM channels")
    s = "```channel_id\t\t\tautodelete"
    for entry in csr.fetchall():
        s+= "\n{}\t{}".format(*entry)
    s += "\n```"
    db.close()
    return s
    
def display_redirect():
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("SELECT channel_id, redirect_channel_id FROM channels")
    s = "```channel_id\t\t\tredirect_channel_id"
    for entry in csr.fetchall():
        s+= "\n{}\t{}".format(*entry)
    s += "\n```"
    db.close()
    return s

def add_row(channel_id, redirect_channel_id=0, autodelete=0):
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("""
                INSERT OR REPLACE INTO channels(channel_id, redirect_channel_id, autodelete)
                 VALUES(?, ?, ?)
                 """, (channel_id, redirect_channel_id, autodelete))
    db.commit()
    db.close()

def delete_row(channel_id):
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("DELETE FROM channels WHERE channel_id=?", (channel_id,))
    db.commit()
    db.close()

def set_autodelete(channel_id, autodelete=True):
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("""
                INSERT OR REPLACE INTO channels(channel_id, autodelete)
                VALUES(?, ?)
                """, (channel_id, int(autodelete)))
    db.commit()
    db.close()

def set_redirectchannel(channel_id, redirect_channel_id):
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("""
                INSERT OR REPLACE INTO channels(channel_id, redirect_channel_id)
                VALUES(?, ?)
                """, 
                (channel_id, redirect_channel_id))
    db.commit()
    db.close()

def get_autodelete(channel_id):
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("SELECT autodelete FROM channels WHERE channel_id =?",
                (channel_id,))
    output = csr.fetchone()
    if output:
        autodelete = output[0]
    else:
        autodelete = False
    db.close()
    return bool(autodelete)

def get_redirect_channel(channel_id):
    db = sqlite3.connect(database_file)
    csr = db.cursor()
    csr.execute("SELECT redirect_channel_id FROM channels WHERE channel_id =?",
                (channel_id,))
    output = csr.fetchone()
    if output:
        redirect_channel_id = output[0]
    else:
        redirect_channel_id = channel_id
    db.close()
    return redirect_channel_id