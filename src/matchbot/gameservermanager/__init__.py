import aiodocker
from matchbot import Match
from matchbot.gameservermanager.gameserver import GameServer
from typing import Iterable, Optional


class GameServerManager:
    def __init__(self, servers: Iterable[GameServer]):
        self.docker = aiodocker.Docker()
        self.servers = list(servers)

    def get_available_server(self) -> Optional[GameServer]:
        for server in self.servers:
            if not server.is_assigned:
                return server

    async def start_match(self, match: Match):
        if server := self.get_available_server():
            server.match = match
            await server.start(docker_instance=self.docker)
        else:
            raise ValueError("Not enough available servers.")

    def get_server(self, match_id: str) -> GameServer:
        for server in self.servers:
            if server.match.id == match_id:
                return server

    async def delete_match(self, match_id):
        server = self.get_server(match_id)
        await server.stop()
        server.match = None
