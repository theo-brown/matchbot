from os import getenv
import aiodocker
from matchbot.gameserver import GameServer
from matchbot.database import DatabaseInterface
from matchbot import MATCH_LIVE, MATCH_FINISHED


class Manager:
    def __init__(self):
        self.dbi = None
        self.docker = aiodocker.Docker()

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

        tokens = await self.dbi.servertokens.get()

        if len(ports) != len(gotv_ports):
            raise ValueError(f"Mismatched port range ({len(ports)} port values but {len(gotv_ports)} GOTV port values).")

        if len(ports) > len(tokens):
            print("More ports than server tokens; discarding spare ports...")
            ports = ports[:len(tokens)]
            gotv_ports = gotv_ports[:len(tokens)]
            print("Done.")
        elif len(ports) < len(tokens):
            print("More server tokens than ports; discarding spare tokens...")
            tokens = tokens[:len(ports)]
            print("Done.")

        servers = [GameServer(token, getenv("PUBLIC_IP"), port, gotv_port)
                   for token, port, gotv_port in zip(tokens, ports, gotv_ports)]
        await self.dbi.servers.add(*servers)

    async def stop(self):
        await self.dbi.close()
        #TODO: also stop all running servers

    async def on_new_match(self, match_id: str):
        match = await self.dbi.matches.get_by_id(match_id)
        server = await self.dbi.servers.get_available()
        server.assign(match)
        await self.dbi.servers.update(server)
        await server.start(self.docker)
        match.status = MATCH_LIVE
        await self.dbi.matches.update(match)
