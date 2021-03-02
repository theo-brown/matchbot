import aiosqlite

database_file = 'database.db'

async def create():  
    async with aiosqlite.connect(database_file) as db:
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS users(user_id INT PRIMARY KEY,
                                                         steam64_id INT)
                         """)
        await db.commit()
    
    
async def clear():
    async with aiosqlite.connect(database_file) as db:
        await db.execute("DELETE FROM users")
        await db.commit()
    

async def display():
    async with aiosqlite.connect(database_file) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            s = "user_id\t\t\tsteam64_id"
            for entry in cursor:
                s += "\n{}\t{}".format(*entry)
            return s

async def add_steam64_id(user_id, steam64_id):
    async with aiosqlite.connect(database_file) as db:
        await db.execute("""
                         INSERT OR REPLACE INTO users(user_id, steam64_id)
                         VALUES(?, ?)
                         """, (user_id, steam64_id))
        await db.commit()
    

async def get_steam64_id(user_id):
    async with aiosqlite.connect(database_file) as db:
        with db.execute("""
                        SELECT steam64_id FROM users
                        WHERE user_id =?
                        """, (user_id,)) as cursor:
            output = await cursor.fetchone()
            if output:
                steam64_id = output[0]
            else:
                steam64_id = 0
    return steam64_id

async def get_steam64_ids(user_ids):
    async with aiosqlite.connect(database_file) as db:
        parameters = ", ".join(['?']*len(user_ids))
        async with db.execute(f"""
                        SELECT steam64_id FROM users
                        WHERE user_id IN ({parameters})
                        """, user_ids) as cursor:
            steam64_ids = [i[0] async for i in cursor]
        return steam64_ids