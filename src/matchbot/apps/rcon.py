import asyncio
import aiorcon
from matchbot import database as db
from matchbot.apps import MatchbotBaseApp
from uuid import UUID
import contextlib
from time import time, sleep


class RconContextManager:
    def __init__(self, ip: str, port: int, rcon_password: str, retry_timeout: int = 5):
        self.ip = str(ip)
        self.port = int(port)
        self.rcon_password = rcon_password
        self.retry_timeout = int(retry_timeout)
        self.connection = None

    async def __aenter__(self):
        start_time = time()
        while not self.connection and time() - start_time < self.retry_timeout:
            try:
                self.connection = await aiorcon.RCON.create(host=self.ip,
                                                            port=self.port,
                                                            password=self.rcon_password,
                                                            loop=asyncio.get_running_loop())
            except ConnectionRefusedError:
                    print(f"RCON connection refused, retrying... [{int(time() - start_time)}s]")
                    sleep(1)

        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


if __name__ == '__main__':
    from os import getenv

    async def main():
        async with RconContextManager(getenv("SERVER_IP"),
                                      getenv("SERVER_PORT"),
                                      getenv("SERVER_RCON_PASSWORD")) as rcon:
            print(await rcon("get5_status"))

    asyncio.run(main())
