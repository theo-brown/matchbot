from typing import Iterable, Optional
from time import time
from uuid import uuid4
from secrets import token_urlsafe
import asyncio
import aiorcon
import aiodocker
from matchbot import Match


class GameServer:
    def __init__(self, token, ip, port, gotv_port, id=None, match=None,
                 password=None, gotv_password=None, rcon_password=None):
        if id:
            self.id = id
        else:
            self.id = uuid4().hex
        self.token = token
        self.ip = ip
        self.port = port
        self.gotv_port = gotv_port
        self.container = None
        self.rcon = None
        self.match = match
        self.password = password
        self.rcon_password = rcon_password
        self.gotv_password = gotv_password

    def assign(self, match: Match):
        self.match = match
        # Generate passwords
        self.password = token_urlsafe(6)
        self.rcon_password = token_urlsafe(6)
        self.gotv_password = token_urlsafe(6)

    async def start(self, docker_instance: aiodocker.docker.Docker):
        if not self.is_assigned:
            raise ValueError("No match loaded.")

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
        await self.connect_rcon()

    async def connect_rcon(self, timeout=5):
        if self.rcon:
            return self.rcon
        else:
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
                raise OSError(f"RCON connection failed after {duration:.2f}s")
            else:
                print(f"RCON connection established after {duration:.2f}s.")
                return self.rcon

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

    @property
    def connect_str(self) -> Optional[str]:
        if self.password and self.is_assigned:
            return f"connect {self.ip}:{self.port}; password {self.password}"
        else:
            return None

    @property
    def connect_gotv_str(self) -> Optional[str]:
        if self.gotv_password and self.is_assigned:
            return f"connect {self.ip}:{self.gotv_port}; password {self.gotv_password}"
        else:
            return None
