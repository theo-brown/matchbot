import asyncpg
from matchbot.database.servers import ServersTable, ServerTokensTable
from matchbot.database.users import UsersTable
from matchbot.database.teams import TeamsTable
from matchbot.database.matches import MatchesTable
from typing import Callable


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
        await self.db.close()
        del self.db
        await self.pool.close()
        self.pool = None

    async def add_listener(self, channel: str, callback: Callable[[str], None]):
        await self.db.add_listener(channel, lambda connection, pid, channel, payload: callback(payload))
