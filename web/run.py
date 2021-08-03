import asyncio
import aiopg
from os import getenv


async def main():
    while True:
        try:
            async with aiopg.connect(user=getenv("POSTGRES_USER"),
                                     database=getenv("POSTGRES_DB"),
                                     password=getenv("POSTGRES_PASSWORD"),
                                     host="database") as db:
                async with db.cursor() as cur:
                    await cur.execute("SELECT * FROM information_schema.tables WHERE table_schema = 'public'")
                    return await cur.fetchall()
        except:
            continue


if __name__ == "__main__":
    print(asyncio.run(main()))
