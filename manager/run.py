from os import getenv
import asyncio
from matchbot.gameserver import GameServerManager
from matchbot.database import DatabaseInterface


async def main():
    try:
        dbi = DatabaseInterface(host="database",
                                user=getenv("POSTGRES_USER"),
                                password=getenv("POSTGRES_PASSWORD"),
                                database_name=getenv("POSTGRES_DB"))
        await dbi.connect()

        gameservers = await dbi.get_gameservers()

        gsm = GameServerManager(gameservers)

        server = gsm.get_available_server()

        print(server.ip, server.port, server.gotv_port, server.token)

    finally:
        dbi.close()


if __name__ == "__main__":
    asyncio.run(main())
