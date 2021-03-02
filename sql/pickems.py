import aiosqlite
from operator import itemgetter

database_file = 'database.db'

async def create():  
    async with aiosqlite.connect(database_file) as db:
        await db.execute("""
                        CREATE TABLE IF NOT EXISTS 
                        pickem_points(pickem_channel_id INTEGER,
                                user_id INTEGER,
                                points INTEGER)
                        """)
        await db.execute("""
                        CREATE UNIQUE INDEX IF NOT EXISTS unique_pickem_user_index 
                        ON pickem_points(pickem_channel_id, user_id)
                        """)
        await db.commit() 
    
    
async def clear():
    async with aiosqlite.connect(database_file) as db:
        await db.execute("DELETE FROM pickem_points")
        await db.commit()

async def display():
    async with aiosqlite.connect(database_file) as db:
        with db.execute("SELECT * FROM pickem_points") as cursor:
            s = "pickem_channel_id\tuser_id\tpoints"
            for entry in cursor:
                s += "\n{}\t{}\t{}".format(*entry)
            return s

async def add_row(pickem_channel_id, user_id, points):
    async with aiosqlite.connect(database_file) as db:
        await db.execute("""
                         INSERT INTO pickem_points(pickem_channel_id, user_id, points)
                         VALUES(?, ?, ?) 
                         ON CONFLICT(pickem_channel_id, user_id)
                         DO UPDATE SET points = points + excluded.points
                         """, (pickem_channel_id, user_id, points))
        await db.commit()
    

async def delete_row(pickem_channel_id, user_id):
    async with aiosqlite.connect(database_file) as db:
        await db.execute("""
                         DELETE FROM pickem_points 
                         WHERE pickem_channel_id=? AND user_id=?
                         """, (pickem_channel_id, user_id))
        await db.commit()
    

async def add_points(pickem_channel_id, user_id, points):
    await add_row(pickem_channel_id, user_id, points)

async def set_points(pickem_channel_id, user_id, points):
    async with aiosqlite.connect(database_file) as db:
        await db.execute("""
                         INSERT INTO pickem_points(pickem_channel_id, user_id, points)
                         VALUES(?, ?, ?) 
                         ON CONFLICT(pickem_channel_id, user_id)
                         DO UPDATE SET points = excluded.points
                         """, (pickem_channel_id, user_id, points))
        await db.commit()
    

async def increment(pickem_channel_id, *user_ids):
    async with aiosqlite.connect(database_file) as db:
        await db.executemany("""
                             INSERT INTO pickem_points(pickem_channel_id, user_id, points)
                             VALUES (?, ?, 1)
                             ON CONFLICT(pickem_channel_id, user_id)
                             DO UPDATE SET points = points + 1
                             """, [(pickem_channel_id, user_id) for user_id in user_ids])
        await db.commit()
    

async def get_list(pickem_channel_id):
    async with aiosqlite.connect(database_file) as db:
        async with db.execute("""
                              SELECT user_id, points FROM pickem_points 
                              WHERE pickem_channel_id=?
                              ORDER BY points
                              """, (pickem_channel_id,)) as cursor:
            # Get the values as a list of lists [user_id, points]
            l = [list(i) async for i in cursor]
            # Sort in descending order by points (index 1)
            l.sort(reverse=True, key=itemgetter(1))
            # Rank by points, assigning same rank to ties
            # Get a list starting at 1, of length equal to len(l)
            ranks = list(range(1, len(l)+1))
            for i in range(len(l)-1):
                # If the next users points are the same as this one, set them equal
                if l[i+1][1] == l[i][1]:
                    ranks[i+1] = ranks[i]
    
    return list(zip(ranks, [i[0] for i in l], [i[1] for i in l]))

async def get_message(pickem_channel_id):
    s = "<#{}>\n**Pick'em Predictions Leaderboard**".format(pickem_channel_id)
    for i in await get_list(pickem_channel_id):
        s += "\n{}. <@{}> ({}pts)".format(*i)
    return s
