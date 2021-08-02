from dotenv import load_dotenv
from os import getenv
import aiodocker
from matchbot import Match
from gameserver import GameServer


# Load environment variables
load_dotenv()
SERVER_TOKEN = getenv("SERVER_TOKEN")
SERVER_IP = getenv("SERVER_IP")
SERVER_PORT_MIN = int(getenv("SERVER_PORT_MIN"))
SERVER_PORT_MAX = int(getenv("SERVER_PORT_MAX"))


class GameServerManager:
    def __init__(self):
        self.docker = aiodocker.Docker()
        self.current_matches = {}
        self.ip = SERVER_IP

        port_range = [i for i in range(SERVER_PORT_MIN, SERVER_PORT_MAX + 1)]
        self.max_number_of_servers = len(port_range) // 2
        connect_ports = port_range[:self.max_number_of_servers]
        gotv_ports = port_range[self.max_number_of_servers:]
        self.ports = [{"port": i, "gotv_port": j} for i, j in zip(connect_ports, gotv_ports)]
        self.available_ports = set(self.ports)

    async def start_match(self, match: Match):
        if len(self.available_ports) == 0:
            raise IndexError(f"{self.max_number_of_servers} exceeded, cannot host Match {match.id}")

        self.current_matches[match.id] = match

        server_ports = self.available_ports.pop()
        match.server = GameServer(token=SERVER_TOKEN,
                                  ip=self.ip,
                                  port=server_ports["port"],
                                  gotv_port=server_ports["gotv_port"],
                                  id=match.id)

        await match.server.start(docker_instance=self.docker)

    def get_match(self, match_id: str) -> Match:
        return self.current_matches[match_id]

    async def delete_match(self, match_id):
        match = self.get_match(match_id)
        if match.server is not None:
            port = match.server.port
            gotv_port = match.server.gotv_port
            await match.server.stop()
            del match.server
            match.server = None
            self.available_ports.add({"port": port, "gotv_port": gotv_port})
        self.current_matches.pop(match_id)


