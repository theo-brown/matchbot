from __future__ import annotations
from typing import Iterable, Union, Tuple
from matchbot.gameserver import GameServer


class ServerTokensTable:
    def __init__(self, dbi: DatabaseInterface):
        self.dbi = dbi

    async def add(self, *tokens: str):
        await self.dbi.db.executemany("INSERT INTO server_tokens(token)"
                                      " VALUES ($1);", tokens)

    async def get(self) -> Iterable[str]:
        return [record.get('token')
                for record in await self.dbi.db.fetch("SELECT token FROM server_tokens")]


class ServersTable:
    def __init__(self, dbi: DatabaseInterface):
        self.dbi = dbi

    async def add(self, *servers: GameServer):
        await self.dbi.db.executemany("INSERT INTO servers(id, token, ip, port, gotv_port, password,"
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
                                        server.match.id if server.is_assigned else None)
                                       for server in servers])

    async def update(self, *servers: GameServer):
        await self.dbi.db.executemany("UPDATE servers"
                                      " SET ip = $2, port = $3, gotv_port = $4, password = $5,"
                                      " gotv_password = $6, rcon_password = $7, match_id = $8"
                                      " WHERE id = $1;",
                                      [(server.id, server.ip, server.port, server.gotv_port,
                                        server.password, server.gotv_password, server.rcon_password,
                                        server.match.id if server.is_assigned else None)
                                       for server in servers])

    async def get(self, column: str, *values) -> Union[Iterable[GameServer], GameServer]:
        if column not in ['token', 'ip', 'port', 'match_id']:
            raise LookupError(f"Cannot lookup server by {column} (expected 'token', 'ip', 'port', or 'match_id').")

        servers = [GameServer(id=record.get('id'),
                              token=record.get('token'),
                              ip=record.get('ip'),
                              port=record.get('port'),
                              gotv_port=record.get('gotv_port'),
                              password=record.get('password'),
                              gotv_password=record.get('gotv_password'),
                              rcon_password=record.get('rcon_password'),
                              match=await self.dbi.matches.get_by_id(record.get('match_id')))
                   for record in await self.dbi.db.fetch("SELECT id, token, ip, port, gotv_port, password,"
                                                         " gotv_password, rcon_password, match_id FROM servers")]

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
        record = await self.dbi.db.fetchrow("SELECT id, token, ip, port, gotv_port FROM servers"
                                            " WHERE match_id is NULL;")

        return GameServer(id=record.get('id'),
                          token=record.get('token'),
                          ip=str(record.get('ip')),
                          port=record.get('port'),
                          gotv_port=record.get('gotv_port'))
