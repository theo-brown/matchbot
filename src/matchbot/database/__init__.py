import asyncpg
from matchbot.database.servers import ServersTable, ServerTokensTable
from matchbot.database.users import UsersTable
from matchbot.database.teams import TeamsTable
from matchbot.database.matches import MatchesTable
from typing import Callable, Coroutine, Union


class DatabaseInterface:
    def __init__(self, host, user, password, database_name, port=5432, timeout=60):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.database_name = database_name
        self.pool = None
        self.timeout = timeout
        self.servers = None
        self.users = None
        self.teams = None
        self.matches = None
        self.listeners = []

    async def connect(self):
        while not self.pool:
            try:
                self.pool = await asyncpg.create_pool(host=self.host,
                                                      port=self.port,
                                                      user=self.user,
                                                      password=self.password,
                                                      database=self.database_name,
                                                      timeout=self.timeout)
            except:
                print("An exception occurred in establishing a connection to the database; retrying...")

        self.servertokens = ServerTokensTable(self)
        self.servers = ServersTable(self)
        self.users = UsersTable(self)
        self.teams = TeamsTable(self)
        self.matches = MatchesTable(self)

    async def close(self):
        for listener in self.listeners:
            await listener['connection'].remove_listener(listener['channel'], listener['callback'])
        await self.pool.close()
        self.pool = None

    async def add_listener(self, channel: str, callback: Union[Coroutine, Callable]):
        con = await self.pool.acquire()
        await con.add_listener(channel, callback)
        self.listeners.append({'connection': con, 'channel': channel, 'callback': callback})
