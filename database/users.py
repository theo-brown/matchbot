from aiosqlite import Connection
db: Connection


async def create():
    await db.execute(
        "CREATE TABLE IF NOT EXISTS users("
        "   user_id INT PRIMARY KEY,"
        "   steam64_id INT"
        ")"
    )

async def clear():
    await db.execute("DELETE FROM users")

async def display():
    s = "user_id\t\t\tsteam64_id"

    async with db.execute("SELECT * FROM users") as cursor:
        async for uid, steam in cursor:
            s += f"\n{uid}\t{steam}"

    return s

async def add_steam64_id(user_id, steam64_id):
    await db.execute(
        "INSERT OR REPLACE INTO users(user_id, steam64_id)"
        "   VALUES(?, ?)",
        (user_id, steam64_id)
    )


async def add_steam64_ids(users):
    await db.executemany(
        "INSERT OR REPLACE INTO users(user_id, steam64_id)"
        " VALUES (?, ?)",
        ((discord, steam) for discord,steam in users.items())
    )


async def get_steam64_id(user_id):
    async with db.execute(
                "SELECT steam64_id FROM users"
                "   WHERE user_id =?",
                (user_id,)
            ) as cursor:
        data = await cursor.fetchone()
    if data is not None:
        return data[0]
    return None

async def get_steam64_ids(user_ids):
    parameters = ", ".join(['?']*len(user_ids))
    async with db.execute(
                f"SELECT steam64_id FROM users"
                f"  WHERE user_id IN ({parameters})",
                user_ids
            ) as cursor:
        steam64_ids = [i async for (i,) in cursor]
    return steam64_ids
