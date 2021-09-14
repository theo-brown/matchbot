from __future__ import annotations
from typing import Iterable, Union, Tuple, Optional
from secrets import token_urlsafe
import uuid


class GameServer:
    def __init__(self, token: str, ip: str, port: int, gotv_port: int, id: Optional[str] = None,
                 match_id: Optional[str] = None, password: Optional[str] = None, gotv_password: Optional[str] = None,
                 rcon_password: Optional[str] = None):
        self.id = id if id else uuid.uuid4().hex
        self.token = token
        self.ip = ip
        self.port = port
        self.gotv_port = gotv_port
        self.match_id = match_id
        self.password = password
        self.rcon_password = rcon_password
        self.gotv_password = gotv_password

    def generate_passwords(self):
        self.password = token_urlsafe(6)
        self.rcon_password = token_urlsafe(6)
        self.gotv_password = token_urlsafe(6)

    def __str__(self):
        return (f"GameServer:\n"
                f"\tID: {self.id}\n"
                f"\tToken: {self.token}\n"
                f"\tIP: {self.ip}\n"
                f"\tPort: {self.port}\n"
                f"\tGOTV Port: {self.gotv_port}\n"
                f"\tMatch: {self.match_id}\n")


def from_dict(gameserver_dict: dict) -> GameServer:
    return GameServer(id=gameserver_dict.get('id'),
                      token=gameserver_dict.get('token'),
                      ip=gameserver_dict.get('ip'),
                      port=gameserver_dict.get('port'),
                      gotv_port=gameserver_dict.get('gotv_port'),
                      password=gameserver_dict.get('password'),
                      gotv_password=gameserver_dict.get('gotv_password'),
                      rcon_password=gameserver_dict.get('rcon_password'),
                      match_id=gameserver_dict.get('match_id'))


class GameServerTokensTable:
    def __init__(self, pool: asyncpg.pool.Pool):
        self.pool = pool

    async def insert(self, *tokens: str):
        async with self.pool.acquire() as connection:
            substitution = ', '.join(f"(${i+1})" for i, v in enumerate(tokens))
            await connection.execute("INSERT INTO server_tokens(token)"
                                    f" VALUES {substitution}"
                                    f" ON CONFLICT DO NOTHING;", *tokens)

    async def delete(self, *tokens: str):
        async with self.pool.acquire() as connection:
            await connection.execute("DELETE FROM server_tokens"
                                     " WHERE token = ANY($1)", tokens)

    async def get(self) -> Iterable[str]:
        async with self.pool.acquire() as connection:
            return [record.get('token')
                    for record in await connection.fetch("SELECT token FROM server_tokens")]


class GameServersTable:
    def __init__(self, pool: asyncpg.pool.Pool):
        self.pool = pool

    async def upsert(self, *servers: GameServer):
        async with self.pool.acquire() as connection:
            await connection.executemany("INSERT INTO servers(id, token, ip, port, gotv_port, password,"
                                                             " gotv_password, rcon_password, match_id)"
                                         " VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"
                                         " ON CONFLICT (token) DO UPDATE"
                                         " SET id = excluded.id,"
                                             " ip = excluded.ip,"
                                             " port = excluded.port,"
                                             " gotv_port = excluded.gotv_port,"
                                             " password = excluded.password,"
                                             " gotv_password = excluded.gotv_password,"
                                             " rcon_password = excluded.rcon_password,"
                                             " match_id = excluded.match_id;",
                                         [(server.id, server.token, server.ip, server.port, server.gotv_port,
                                           server.password, server.gotv_password, server.rcon_password,
                                           server.match_id) for server in servers])

    async def get(self, column: str, *values) -> Union[Iterable[GameServer], GameServer]:
        if column not in ['id', 'token', 'ip', 'port', 'gotv_port', 'match_id']:
            raise LookupError(f"Cannot lookup server by {column} (expected 'id', 'token', 'ip', 'port', 'gotv_port'"
                              f" or 'match_id').")

        if len(values) == 1 and values[0] is None:
            query = ("SELECT id, token, ip, port, gotv_port, password,"
                     " gotv_password, rcon_password, match_id FROM servers"
                    f" WHERE {column} IS NULL")
        else:
            query = ("SELECT id, token, ip, port, gotv_port, password,"
                     " gotv_password, rcon_password, match_id FROM servers"
                    f" WHERE {column} = ANY ($1)", values)

        async with self.pool.acquire() as connection:
            servers = [from_dict(record)
                       for record in await connection.fetch(query)]

        if len(values) == 1:
            if len(servers) == 1:
                return servers[0]
            elif len(servers) > 1:
                raise(LookupError(f"Multiple matching servers found with {column}={values[0]}"))
            else:
                raise(LookupError(f"No matching server found with {column}={values[0]}"))
        else:
            return servers

    async def get_available(self):
        async with self.dbi.pool.acquire() as connection:
            record = await connection.fetchrow("SELECT id, token, ip, port, gotv_port, password,"
                                               " gotv_password, rcon_password, match_id FROM servers"
                                               " WHERE match_id is NULL;")
        return from_dict(record)
