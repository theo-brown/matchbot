import asyncpg
from matchbot.database.servertokens import ServerTokensTable
from matchbot.database.users import UsersTable
from matchbot.database.teams import TeamsTable

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

        self.servertokens = ServerTokensTable(self.db)
        self.users = UsersTable(self.db)
        self.teams = TeamsTable(self.db)

    async def close(self):
        await self.db.close()
        del self.db
        self.db = None

