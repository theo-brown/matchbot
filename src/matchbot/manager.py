from os import getenv
import aiodocker
from asyncpg import Connection
from matchbot.gameserver import GameServer
from matchbot.database import DatabaseInterface
from matchbot import MATCH_INITIALISING, MATCH_LIVE, MATCH_FINISHED
import json
import asyncio
import datetime


class Manager:
    def __init__(self):
        self.dbi = None
        self.docker = aiodocker.Docker()

    async def start(self):
        self.dbi = DatabaseInterface(host=getenv("POSTGRES_HOST"),
                                     user=getenv("POSTGRES_USER"),
                                     password=getenv("POSTGRES_PASSWORD"),
                                     database_name=getenv("POSTGRES_DB"),
                                     port=int(getenv("POSTGRES_PORT")))
        await self.dbi.connect()

        await self.dbi.add_listener('match_status', self.on_match_status_change)

        ports = [i for i in range(int(getenv("PORT_MIN")),
                                  int(getenv("PORT_MAX")) + 1)]
        gotv_ports = [i for i in range(int(getenv("GOTV_PORT_MIN")),
                                       int(getenv("GOTV_PORT_MAX")) + 1)]

        await self.dbi.servertokens.add('A')
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

    async def on_match_status_change(self, connection: Connection, pid: int, channel: str, payload: str):
        payload = json.loads(payload)
        if payload['status'] == MATCH_INITIALISING:
            match = await self.dbi.matches.get_by_id(payload['id'])
            server = await self.dbi.servers.get_available()
            await self.dbi.servers.assign(server, match)
            await server.start(self.docker)
            await self.dbi.matches.set_as_live(match)
