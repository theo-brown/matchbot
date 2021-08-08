from os import getenv
import asyncio
from matchbot.gameserver import GameServer, GameServerManager
from matchbot.database import DatabaseInterface
from matchbot import MATCH_LIVE, MATCH_FINISHED


class Manager:
    def __init__(self):
        self.dbi = None
        self.gsm = None

    async def start(self):
        self.dbi = DatabaseInterface(host=getenv("POSTGRES_HOST"),
                                     user=getenv("POSTGRES_USER"),
                                     password=getenv("POSTGRES_PASSWORD"),
                                     database_name=getenv("POSTGRES_DB"))
        await self.dbi.connect()

        await self.dbi.add_listener('new_match', self.on_new_match)

        ports = [i for i in range(int(getenv("PORT_MIN")),
                                  int(getenv("PORT_MAX")) + 1)]
        gotv_ports = [i for i in range(int(getenv("GOTV_PORT_MIN")),
                                       int(getenv("GOTV_PORT_MAX")) + 1)]

        self.gsm = GameServerManager([GameServer(token=token,
                                                 ip=getenv("PUBLIC_IP"),
                                                 port=ports.pop(),
                                                 gotv_port=gotv_ports.pop())
                                      for token in await self.dbi.servertokens.get()])

    async def on_new_match(self, match_id: str):
        match = await self.dbi.matches.get_by_id(match_id)
        await self.gsm.start_match(match)
        match.status = MATCH_LIVE
        await self.dbi.matches.update(match)

if __name__ == "__main__":
    manager = Manager()
    asyncio.run(manager.start())
