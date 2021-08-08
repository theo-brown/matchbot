import asyncpg
from matchbot.database.servertokens import ServerTokensTable
from matchbot.database.users import UsersTable
from matchbot.database.teams import TeamsTable
from matchbot.database.matches import MatchTable

class DatabaseInterface:
    def __init__(self, host, user, password, database_name, port=5432, timeout=60):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.database_name = database_name
        self.db = None
        self.timeout = timeout

    async def connect(self):
        self.db = await asyncpg.connect(host=self.host,
                                        port=self.port,
                                        user=self.user,
                                        password=self.password,
                                        database=self.database_name,
                                        timeout=self.timeout)

        self.servertokens = ServerTokensTable(self)
        self.users = UsersTable(self)
        self.teams = TeamsTable(self)
        self.matches = MatchTable(self)

    async def close(self):
        await self.db.close()
        del self.db
        self.db = None

