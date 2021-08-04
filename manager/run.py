from os import getenv
import asyncio
from matchbot.gameserver import GameServer, GameServerManager
from matchbot.database import DatabaseInterface


async def main():
    try:
        dbi = DatabaseInterface(host="database",
                                user=getenv("POSTGRES_USER"),
                                password=getenv("POSTGRES_PASSWORD"),
                                database_name=getenv("POSTGRES_DB"))
        await dbi.connect()

        ports = [i for i in range(int(getenv("PORT_MIN")),
                                  int(getenv("PORT_MAX")) + 1)]
        gotv_ports = [i for i in range(int(getenv("GOTV_PORT_MIN")),
                                       int(getenv("GOTV_PORT_MAX")) + 1)]

        gsm = GameServerManager([GameServer(token=token,
                                            ip=getenv("PUBLIC_IP"),
                                            port=ports.pop(),
                                            gotv_port=gotv_ports.pop())
                                            for token in await dbi.get_server_tokens()])

        server = gsm.get_available_server()

        print(server.ip, server.port, server.gotv_port, server.token)

    finally:
        dbi.close()


if __name__ == "__main__":
    asyncio.run(main())
