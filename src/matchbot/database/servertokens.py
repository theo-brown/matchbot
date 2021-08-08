from asyncpg import Connection
from typing import Iterable


class ServerTokensTable:
    def __init__(self, dbi):
        self.dbi = dbi

    async def add(self, *server_tokens: str):
        await self.dbi.db.executemany("INSERT INTO server_tokens(server_token)"
                                      " VALUES ($1);", server_tokens)

    async def get(self) -> Iterable[str]:
        return [record.get('server_token')
                for record in await self.dbi.db.fetch("SELECT server_token FROM server_tokens")]
