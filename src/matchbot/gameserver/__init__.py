from typing import Iterable, Optional
from time import time
from uuid import uuid4
from secrets import token_urlsafe
import asyncio
import aiorcon
import aiodocker
from matchbot import Match


class GameServer:
    def __init__(self, token, ip, port, gotv_port, id=uuid4().hex):
        self.id = id
        self.token = token
        self.ip = ip
        self.port = port
        self.gotv_port = gotv_port
        self.container = None
        self.rcon = None
        self.match = None
        self.connect_str = None
        self.connect_gotv_str = None

    async def start(self, docker_instance: aiodocker.docker.Docker, timeout=8):
        if self.match is None:
            raise ValueError("No match loaded.")

        # Generate passwords
        self.password = token_urlsafe(6)
        self.rcon_password = token_urlsafe(6)
        self.gotv_password = token_urlsafe(6)

        self.connect_str = f"connect {self.ip}:{self.port}; password {self.password}"
        self.connect_gotv_str = f"connect {self.ip}:{self.gotv_port}; password {self.gotv_password}"

        config = {"Image": "theobrown/csgo-docker:latest",
                  "Env": [f"SERVER_TOKEN={self.token}",
                          f"PORT={self.port}",
                          f"GOTV_PORT={self.gotv_port}",
                          f"PASSWORD={self.password}",
                          f"RCON_PASSWORD={self.rcon_password}",
                          f"GOTV_PASSWORD={self.gotv_password}",
                          f"MATCH_CONFIG={self.match.config_json}"],
                  "HostConfig": {"NetworkMode": "host"}}
        print("Spawning server...")
        self.container = await docker_instance.containers.run(config=config, name=self.id)
        await self.container.start()
        print("Establishing RCON connection...")
        start_time = time()
        duration = 0
        while duration < timeout:
            duration = time() - start_time
            try:
                self.rcon = await aiorcon.RCON.create(self.ip, self.port, self.rcon_password,
                                                      loop=asyncio.get_event_loop())
            except OSError as e:
                #print(f"RCON connection failed with error {e}\n"
                #      f"Retrying ({duration:.2f}s)...")
                continue
            except Exception as e:
                await self.stop()
                raise e
            else:
                break
        if duration >= timeout:
            await self.stop()
            raise OSError(f"RCON connection failed after {duration:.2f}s")
        else:
            print(f"RCON connection established after {duration:.2f}s.")

    async def stop(self):
        if isinstance(self.rcon, aiorcon.RCON):
            self.rcon.close()
        if isinstance(self.container, aiodocker.docker.DockerContainer):
            await self.container.delete(force=True)
        self.rcon = None
        self.container = None

    @property
    def is_assigned(self) -> bool:
        return bool(self.match)


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
            return server.connect_str, server.connect_gotv_str
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

    async def stop_all(self):
        for server in self.servers:
            await server.stop()
