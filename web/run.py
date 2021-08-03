import asyncio
import aiopg
from os import getenv


async def main():
    while True:
        try:
            async with await aiopg.connect(user=getenv("POSTGRES_USER"),
                                           database=getenv("POSTGRES_DB"),
                                           password=getenv("POSTGRES_PASSWORD"),
                                           host="database") as db:
                async with await db.cursor() as cur:
                    await cur.execute("SELECT * FROM information_schema.tables WHERE table_schema = 'public'")
                    ret = await cur.fetchall()
                    return ret
        except:
            continue


if __name__ == "__main__":
    print(asyncio.run(main()))
