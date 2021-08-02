import asyncio
import aiopg
from os import getenv


async def main():
    db = await aiopg.connect(user=getenv("DB_USER"),
                             database=getenv("DB_DATABASE"),
                             password=getenv("DB_PASSWORD"),
                             host="database")
    cur = await db.cursor()
    await cur.execute("SELECT * FROM tbl")
    ret = await cur.fetchall()
    return ret


if __name__ == "__main__":
    asyncio.run(main())
