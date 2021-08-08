from os import getenv
import asyncio
from matchbot.gameserver import GameServer, GameServerManager
from matchbot.database import DatabaseInterface


class Manager:
    def __init__(self):
        pass

    async def start(self):
        self.dbi = DatabaseInterface(host="database",
                                     user=getenv("POSTGRES_USER"),
                                     password=getenv("POSTGRES_PASSWORD"),
                                     database_name=getenv("POSTGRES_DB"))
        await self.dbi.connect()

        ports = [i for i in range(int(getenv("PORT_MIN")),
                                  int(getenv("PORT_MAX")) + 1)]
        gotv_ports = [i for i in range(int(getenv("GOTV_PORT_MIN")),
                                       int(getenv("GOTV_PORT_MAX")) + 1)]

        self.gsm = GameServerManager([GameServer(token=token,
                                                 ip=getenv("PUBLIC_IP"),
                                                 port=ports.pop(),
                                                 gotv_port=gotv_ports.pop())
                                      for token in await self.dbi.servertokens.get()])


if __name__ == "__main__":
    manager = Manager()
    asyncio.run(manager.start())
