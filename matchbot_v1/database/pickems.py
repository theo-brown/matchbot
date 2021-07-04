from aiosqlite import Connection
db: Connection


async def create():
    await db.executescript(
        "CREATE TABLE IF NOT EXISTS pickem_points("
        "   pickem_channel_id INTEGER,"
        "   user_id INTEGER,"
        "   points INTEGER"
        ");"
        "CREATE UNIQUE INDEX IF NOT EXISTS unique_pickem_user_index"
        "   ON pickem_points(pickem_channel_id, user_id)"
    )
    
async def clear():
    await db.execute("DELETE FROM pickem_points")

async def display():
    s = "pickem_channel_id\tuser_id\tpoints"

    async with db.execute("SELECT * FROM pickem_points") as cursor:
        async for channel, user, points in cursor:
            s += f"\n<#{channel}>\t{user}\t{points}"

    return s

async def add_row(pickem_channel_id, user_id, points):
    await db.execute(
        "INSERT INTO pickem_points(pickem_channel_id, user_id, points)"
        "   VALUES(?, ?, ?)"
        "   ON CONFLICT(pickem_channel_id, user_id)"
        "       DO UPDATE SET points = points + excluded.points",
        (pickem_channel_id, user_id, points)
    )
    

async def delete_row(pickem_channel_id, user_id):
    await db.execute(
        "DELETE FROM pickem_points"
        "   WHERE pickem_channel_id=? AND user_id=?",
        (pickem_channel_id, user_id)
    )
    

async def add_points(pickem_channel_id, user_id, points):
    await add_row(pickem_channel_id, user_id, points)

async def set_points(pickem_channel_id, user_id, points):
    await db.execute(
        "INSERT INTO pickem_points(pickem_channel_id, user_id, points)"
        "   VALUES(?, ?, ?)"
        "   ON CONFLICT(pickem_channel_id, user_id)"
        "       DO UPDATE SET points = excluded.points",
        (pickem_channel_id, user_id, points)
    )
    

async def increment(pickem_channel_id, *user_ids):
    await db.executemany(
        "INSERT INTO pickem_points(pickem_channel_id, user_id, points)"
        "   VALUES (?, ?, 1)"
        "   ON CONFLICT(pickem_channel_id, user_id)"
        "       DO UPDATE SET points = points + 1",
        ((pickem_channel_id, user_id) for user_id in user_ids)
    )
    

async def get_list(pickem_channel_id):
    async with db.execute(
                "SELECT user_id, points FROM pickem_points"
                "   WHERE pickem_channel_id=?"
                "   ORDER BY points DESC",
                (pickem_channel_id,)
            ) as cursor:
        data = await cursor.fetchall()

    ### Rank by points, assigning same rank to ties
    # ranks before ties
    ranks = list(range(1, len(data)+1))
    for i in range(len(data)-1):
        # If the next users points are the same, they have the same rank
        if data[i+1][1] == data[i][1]:
            ranks[i+1] = ranks[i]

    return ((rank, user, points) for rank, (user, points) in zip(ranks, data))

async def get_message(pickem_channel_id):
    s = f"<#{pickem_channel_id}>\n**Pick'em Predictions Leaderboard**"
    for rank, user, points in await get_list(pickem_channel_id):
        s += f"\n{rank}. <@{user}> ({points}pts)"
    return s
