import asyncio
import aiorcon
from matchbot import database as db
from matchbot.apps import MatchbotBaseApp
from uuid import UUID
import contextlib


class RconContextManager:
    def __init__(self, ip: str, port: int, rcon_password: str):
        self.ip = ip
        self.port = port
        self.rcon_password = rcon_password
        self.connection = None

    async def __aenter__(self):
        self.connection = await aiorcon.RCON.create(host=self.ip,
                                                    port=self.port,
                                                    password=self.rcon_password,
                                                    loop=asyncio.get_running_loop())
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


class RconManager(MatchbotBaseApp):
    def __init__(self,
                 db_host: str, db_port: int, db_user: str, db_password: str, db_name: str,
                 redis_host: str, redis_port: int,
                 *args, **kwargs):
        super().__init__(db_host, db_port, db_user, db_password, db_name, redis_host, redis_port, db_echo=False,
                         *args, **kwargs)

    @contextlib.asynccontextmanager
    async def new_rcon(self, server_id: UUID) -> RconContextManager:
        async with self.new_session() as session:
            server = await session.get(db.models.Server, server_id)
        async with RconContextManager(ip=str(server.ip),
                                      port=server.port,
                                      rcon_password=server.rcon_password) as rcon:
            yield rcon


if __name__ == '__main__':
    from os import getenv

    async def main():
        rcon_manager = RconManager(db_host=getenv("POSTGRES_HOST"),
                                   db_port=getenv("POSTGRES_PORT"),
                                   db_user=getenv("POSTGRES_USER"),
                                   db_password=getenv("POSTGRES_PASSWORD"),
                                   db_name=getenv("POSTGRES_DB"),
                                   redis_host=getenv("REDIS_HOST"),
                                   redis_port=getenv("REDIS_PORT"))

        while True:
            try:
                async with rcon_manager.new_rcon("3b3ba856-180b-499d-9028-4ff1bb7c3c0a") as rcon:
                    print(await rcon("get5_status"))
            except ConnectionRefusedError:
                print("Connection refused, retrying...")

    asyncio.run(main())
