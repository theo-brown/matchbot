from uuid import uuid4
from secrets import token_urlsafe
import asyncio
import aiorcon
import aiodocker
from time import time


class GameServer:
    def __init__(self, token, ip, port=27015, gotv_port=27020, id=uuid4().hex, match_config=""):
        self.token = token
        self.id = id
        self.ip = ip
        self.port = port
        self.gotv_port = gotv_port
        self.password = token_urlsafe(6)
        self.rcon_password = token_urlsafe(6)
        self.gotv_password = token_urlsafe(6)
        self.match_config = match_config

        self.connect_str = f"connect {self.ip}:{self.port}; password {self.password}"
        self.connect_gotv_str = f"connect {self.ip}:{self.gotv_port}; password {self.gotv_password}"

        self.container = None
        self.rcon = None

    async def start(self, docker_instance: aiodocker.docker.Docker, timeout=8):
        config = {"Image": "theobrown/csgo-docker:latest",
                  "Env": [f"SERVER_TOKEN={self.token}",
                          f"PORT={self.port}",
                          f"GOTV_PORT={self.gotv_port}",
                          f"PASSWORD={self.password}",
                          f"RCON_PASSWORD={self.rcon_password}",
                          f"GOTV_PASSWORD={self.gotv_password}",
                          f"MATCH_CONFIG={self.match_config}"],
                  "HostConfig": {"NetworkMode": "host"}}
        print("Spawning server...")
        self.container = await docker_instance.containers.run(config=config, name=self.id)
        await self.container.start()
        print("Establishing RCON connection...")
        start_time = time()
        duration = 0
        while (duration < timeout):
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