import aiosqlite

database_file = 'database.db'

async def create():  
    async with aiosqlite.connect(database_file) as db:
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS channels(channel_id INT PRIMARY KEY,
                                                             redirect_channel_id INT,
                                                             autodelete INT DEFAULT 0)
                         """)
        await db.commit()
        
async def clear():
    async with aiosqlite.connect(database_file) as db:
        await db.execute("DELETE FROM channels")
        await db.commit()

async def display(columns=''):
    if columns == '':
        return await display_all()
    elif columns == "autodelete":
        return await display_autodelete()
    elif columns == "redirect":
        return await display_redirect()
    else:
        return "Error: expected an argument from ['', 'autodelete', 'redirect']"
    
async def display_all():
    async with aiosqlite.connect(database_file) as db:
        async with db.execute("SELECT * FROM channels") as cursor:
            s = "```\nchannel_id\t\t\tredirect_channel_id\tautodelete"
            async for entry in cursor:
                s+= "\n{}\t{}\t{}".format(*entry)
            s += "\n```"
            return s
    
async def display_autodelete():
    async with aiosqlite.connect(database_file) as db:
        async with db.execute("SELECT channel_id, autodelete FROM channels") as cursor:
            s = "```channel_id\t\t\tautodelete"
            async for entry in cursor:
                s+= "\n{}\t{}".format(*entry)
            s += "\n```"
            return s
    
async def display_redirect():
    async with aiosqlite.connect(database_file) as db:
        async with db.execute("SELECT channel_id, redirect_channel_id FROM channels") as cursor:
            s = "```channel_id\t\t\tredirect_channel_id"
            async for entry in cursor:
                s+= "\n{}\t{}".format(*entry)
            s += "\n```"
            return s

async def add_row(channel_id, redirect_channel_id=0, autodelete=0):
    async with aiosqlite.connect(database_file) as db: 
        await db.execute("""
                         INSERT OR REPLACE INTO channels(channel_id, redirect_channel_id, autodelete)
                         VALUES(?, ?, ?)
                         """, (channel_id, redirect_channel_id, autodelete))
        await db.commit()

async def delete_row(channel_id):
    async with aiosqlite.connect(database_file) as db: 
        await db.execute("DELETE FROM channels WHERE channel_id=?", (channel_id,))
        await db.commit()
    

async def set_autodelete(channel_id, autodelete=True):
    async with aiosqlite.connect(database_file) as db: 
        await db.execute("""
                         INSERT OR REPLACE INTO channels(channel_id, autodelete)
                         VALUES(?, ?)
                         """, (channel_id, int(autodelete)))
        await db.commit()
    

async def set_redirectchannel(channel_id, redirect_channel_id):
    async with aiosqlite.connect(database_file) as db: 
        await db.execute("""
                         INSERT OR REPLACE INTO channels(channel_id, redirect_channel_id)
                         VALUES(?, ?)
                         """,
                         (channel_id, redirect_channel_id))
        await db.commit()
    

async def get_autodelete(channel_id):
    async with aiosqlite.connect(database_file) as db: 
        async with db.execute("SELECT autodelete FROM channels WHERE channel_id =?",
                    (channel_id,)) as cursor:
            output = await cursor.fetchone()
            if output:
                autodelete = output[0]
            else:
                autodelete = False

            return bool(autodelete)

async def get_redirect_channel(channel_id):
    async with aiosqlite.connect(database_file) as db: 
       async with db.execute("SELECT redirect_channel_id FROM channels WHERE channel_id =?",
                    (channel_id,)) as cursor:
            output = await cursor.fetchone()
            if output:
                redirect_channel_id = output[0]
            else:
                redirect_channel_id = channel_id

            return redirect_channel_id
