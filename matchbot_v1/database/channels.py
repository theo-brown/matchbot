from aiosqlite import Connection
db: Connection


async def create():
    await db.execute(
        "CREATE TABLE IF NOT EXISTS channels("
        "    channel_id INT PRIMARY KEY,"
        "    redirect_channel_id INT,"
        "    autodelete INT DEFAULT 0"
        ")"
    )

async def clear():
    await db.execute("DELETE FROM channels")

async def display(column=''):
    functions = {
        '': display_all,
        'autodelete': display_autodelete,
        'redirect': display_redirect,
    }
    return await functions[column]()

async def display_all():
    s = "```\nchannel_id\t\t\tredirect_channel_id\tautodelete"

    async with db.execute("SELECT * FROM channels") as cursor:
        async for channel, redirect, autodelete in cursor:
            s += f"\n{channel}\t{redirect}\t{autodelete}"

    s += "\n```"
    return s

async def display_autodelete():
    s = "```channel_id\t\t\tautodelete"

    async with db.execute("SELECT channel_id, autodelete FROM channels") as cursor:
        async for channel, autodelete in cursor:
            s += f"\n{channel}\t{autodelete}"

    s += "\n```"
    return s

async def display_redirect():
    s = "```channel_id\t\t\tredirect_channel_id"

    async with db.execute("SELECT channel_id, redirect_channel_id FROM channels") as cursor:
        async for channel, redirect in cursor:
            s += f"\n{channel}\t{redirect}"

    s += "\n```"
    return s

async def add_row(channel_id, redirect_channel_id=None, autodelete=0):
    if redirect_channel_id is None:
        redirect_channel_id = channel_id
    await db.execute(
        "INSERT OR REPLACE INTO channels(channel_id, redirect_channel_id, autodelete)"
        "VALUES(?, ?, ?)",
        (channel_id, redirect_channel_id, autodelete)
    )

async def delete_row(channel_id):
    await db.execute("DELETE FROM channels WHERE channel_id=?", (channel_id,))

async def set_autodelete(channel_id, autodelete=True):
    await db.execute(
        "INSERT OR REPLACE INTO channels(channel_id, autodelete)"
        "VALUES(?, ?)",
        (channel_id, int(autodelete))
    )

async def set_redirectchannel(channel_id, redirect_channel_id):
    await db.execute(
        "INSERT OR REPLACE INTO channels(channel_id, redirect_channel_id)"
        "VALUES(?, ?)",
        (channel_id, redirect_channel_id)
    )

async def get_autodelete(channel_id):
    async with db.execute(
                "SELECT autodelete FROM channels WHERE channel_id =?", (channel_id,)
            ) as cursor:
        data = await cursor.fetchone()
    if data is not None:
        return bool(data[0])
    return False

async def get_redirect_channel(channel_id):
    async with db.execute(
                "SELECT redirect_channel_id FROM channels WHERE channel_id =?", (channel_id,)
            ) as cursor:
        data = await cursor.fetchone()
    if data is not None:
        return data[0]
    return channel_id
