import asyncio
import asyncpg
from typing import Iterable, Union
from matchbot import Team, User
from matchbot.gameserver import GameServer
from time import sleep


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

    async def close(self):
        await self.db.close()
        del self.db
        self.db = None

    async def add_server_token(self, server_token):
        await self.db.execute("INSERT INTO server_tokens(server_token)"
                              " VALUES ($1);", server_token)

    async def get_server_tokens(self) -> Iterable[str]:
        return [record.get('server_token')
                for record in await self.db.fetch("SELECT server_token FROM server_tokens")]

    async def add_users(self, *users):
       await self.db.executemany("INSERT INTO users(steam_id, discord_id, display_name)"
                                 " VALUES ($1, $2, $3)"
                                 " ON CONFLICT (steam_id) DO UPDATE"
                                 " SET discord_id = excluded.discord_id,"
                                     " display_name = excluded.display_name;",
                                     [(user.steam_id, user.discord_id, user.display_name)
                                      for user in users])

    async def get_users(self, column: str, *values) -> Union[User, Iterable[User]]:
        if column not in ['steam_id', 'discord_id', 'display_name']:
            raise ValueError(f"Column {column} not found in table"
                             " (expected 'steam_id', 'discord_id' or 'display_name').")
        users = [User(steam_id=record.get('steam_id'),
                      discord_id=record.get('discord_id'),
                      display_name=record.get('display_name'))
                 for record in await self.db.fetch("SELECT steam_id, discord_id, display_name FROM users"
                                                  f" WHERE {column} = ANY ($1);", values)]
        if len(values) == 1:
            if users:
                return users[0]
            else:
                return None
        else:
            return users
