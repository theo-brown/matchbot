import asyncio
import asyncpg
from typing import Iterable, Union
from matchbot import Team, User
from matchbot.gameserver import GameServer


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

    async def add_server_token(self, server_token: str):
        await self.db.execute("INSERT INTO server_tokens(server_token)"
                              " VALUES ($1);", server_token)

    async def get_server_tokens(self) -> Iterable[str]:
        return [record.get('server_token')
                for record in await self.db.fetch("SELECT server_token FROM server_tokens")]

    async def add_users(self, *users: User):
       await self.db.executemany("INSERT INTO users(steam_id, discord_id, display_name)"
                                 " VALUES ($1, $2, $3)"
                                 " ON CONFLICT (steam_id) DO UPDATE"
                                 " SET discord_id = excluded.discord_id,"
                                     " display_name = excluded.display_name;",
                                     [(user.steam_id, user.discord_id, user.display_name)
                                      for user in users])

    async def get_users(self, column: str, *values: Union[int, str]) -> Union[User, Iterable[User]]:
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

    async def add_teams(self, *teams: Team):
        await self.db.executemany("INSERT INTO teams(team_id, team_name, team_tag)"
                                  " VALUES ($1, $2, $3)",
                                  [(team.id, team.name, team.tag) for team in teams])
        values = []
        for team in teams:
            values += [(team.id, steam_id) for steam_id in team.steam_ids]
        await self.db.executemany("INSERT INTO team_players(team_id, steam_id)"
                                  " VALUES ($1, $2)",
                                  values)

    async def get_teams(self, column: str, *values) -> Union[Team, Iterable[Team]]:
        if column not in ['team_id', 'team_name', 'team_tag']:
            raise ValueError(f"Column {column} not found in table"
                             " (expected 'team_id', 'team_name' or 'team_tag').")
        teams = [Team(name=record.get('team_name'),
                      tag=record.get('team_tag'),
                      id=record.get('team_id'))
                 for record in await self.db.fetch("SELECT team_id, team_name, team_tag"
                                                   " FROM teams"
                                                  f" WHERE {column} = ANY ($1);", values)]
        for team in teams:
            steam_ids = await self.db.fetch("SELECT steam_id"
                                            " FROM team_players"
                                            " WHERE team_id = $1", (team.id))
            team.players = await self.get_users('steam_id', *steam_ids)

        if len(values) == 1:
            if teams:
                return teams[0]
            else:
                return None
        else:
            return teams