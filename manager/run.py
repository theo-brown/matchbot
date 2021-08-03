from matchbot.gameserver import GameServer, GameServerManager
from matchbot.database import DatabaseInterface

from os import getenv
import asyncio

dbi = DatabaseInterface(host="database",
                        user=getenv("POSTGRES_USER"),
                        password=getenv("POSTGRES_PASSWORD"),
                        database_name=getenv("POSTGRES_DB"))

async def main():
    gameservers = await dbi.generate_gameservers()
    print(gameservers)
    await dbi.add_gameserver("asdasd", "192.168.0.1", 27015, 27020)
    gameservers = await dbi.generate_gameservers()
    print(gameservers)

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    finally:
        dbi.close()