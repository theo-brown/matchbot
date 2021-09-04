from __future__ import annotations
from typing import Optional, Iterable, Union
from uuid import uuid4


class Team:
    def __init__(self, name: str, steam_ids: Iterable[int], tag: Optional[str] = '', id: Optional[str] = None):
        self.name = name
        self.steam_ids = steam_ids
        self.tag = tag
        self.id = id if id else uuid4().hex

    def __str__(self):
        return ("Team:\n"
                f"\tID: {self.id}\n"
                f"\tName: {self.name}\n"
                f"\tTag: {self.tag}\n"
                f"\tPlayer IDs: {self.steam_ids}")


def from_dict(team_dict: dict) -> Team:
    return Team(name=team_dict.get('name'),
                steam_ids=team_dict.get('steam_ids'),
                tag=team_dict.get('tag'),
                id=team_dict.get('id'))


class TeamsTable:
    def __init__(self, pool: asyncpg.pool.Pool):
        self.pool = pool

    async def upsert(self, *teams: Team):
        async with self.pool.acquire() as connection:
            await connection.executemany("INSERT INTO teams(id, name, tag)"
                                         " VALUES ($1, $2, $3)"
                                         " ON CONFLICT (id) DO UPDATE"
                                         " SET name = excluded.name,"
                                         " tag = excluded.tag;",
                                         [(team.id, team.name, team.tag)
                                          for team in teams])
            await connection.executemany("INSERT INTO team_players(team_id, steam_id)"
                                         " VALUES ($1, $2);",
                                         [(team.id, user_id)
                                          for team in teams for user_id in team.steam_ids])

    async def get(self, column: str, *values: Union[str, int]) -> Union[Team, Iterable[Team]]:
        if column not in ['id', 'name', 'tag', 'steam_id']:
            raise ValueError(f"Column {column} not found in table"
                             " (expected 'id', 'name', 'tag' or 'steam_id').")

        async with self.pool.acquire() as connection:
            if column == 'steam_id':
                team_ids = [record.get('team_id') for record in await connection.fetch("SELECT team_id FROM team_players"
                                                                                       " WHERE steam_id = ANY($1);",
                                                                                       values)]
                teams = await self.get('id', team_ids)
            else:
                teams = [{'id': record.get('id'),
                          'name': record.get('name'),
                          'tag': record.get('tag')}
                         for record in await connection.fetch("SELECT id, name, tag FROM teams"
                                                              f" WHERE {column} = ANY ($1);", values)]
                user_ids = [{'team_id': record.get('team_id'),
                             'steam_id': record.get('steam_id')}
                            for record in await connection.fetch("SELECT team_id, steam_id FROM team_players"
                                                                 " WHERE team_id = ANY($1);",
                                                                 [team['id'] for team in teams])]
                teams = [Team(id=team['id'],
                              name=team['name'],
                              tag=team['tag'],
                              steam_ids=[user['steam_id'] for user in user_ids if user['team_id'] == team['id']])
                         for team in teams]

        if len(values) == 1:
            if len(teams) == 1:
                return teams[0]
            elif len(teams) > 1:
                raise (LookupError(f"Multiple matching teams found with {column}={values[0]}."))
            else:
                raise (LookupError(f"No matching team found with {column}={values[0]}."))
        else:
            return teams
