from typing import Iterable, Union
from matchbot import Team, User


class TeamsTable:
    def __init__(self, dbi):
        self.dbi = dbi

    async def add(self, *teams: Team):
        await self.dbi.db.executemany("INSERT INTO teams(id, name, tag)"
                                      " VALUES ($1, $2, $3)",
                                      [(team.id, team.name, team.tag) for team in teams])
        await self.dbi.db.executemany("INSERT INTO team_players(team_id, steam_id)"
                                      " VALUES ($1, $2)",
                                      [(team.id, steam_id)
                                       for team in teams
                                       for steam_id in team.steam_ids])

    async def get(self, column: str, *values) -> Union[Team, Iterable[Team]]:
        if column not in ['id', 'name', 'tag']:
            raise ValueError(f"Column {column} not found in table"
                             " (expected 'id', 'name' or 'tag').")
        teams = [Team(name=record.get('name'),
                      tag=record.get('tag'),
                      id=record.get('id'))
                 for record in await self.dbi.db.fetch("SELECT id, name, tag"
                                                       " FROM teams"
                                                       f" WHERE {column} = ANY ($1);", values)]
        for team in teams:
            team.players = [User(steam_id=record.get('steam_id'),
                                 discord_id=record.get('discord_id'),
                                 display_name=record.get('display_name'))
                            for record in
                            await self.dbi.db.fetch("SELECT steam_id, discord_id, display_name"
                                                    " FROM users"
                                                    " WHERE steam_id = ANY (SELECT steam_id"
                                                                           " FROM team_players"
                                                                           " WHERE team_id = $1);",
                                                    team.id)]

        if len(values) == 1:
            if len(teams) == 1:
                return teams[0]
            elif len(teams) > 1:
                raise(LookupError(f"Multiple matching teams found with {column}={values[0]}"))
            else:
                raise(LookupError(f"No matching team found with {column}={values[0]}"))
        else:
            return teams

    async def get_by_id(self, *ids) -> Union[Team, Iterable[Team]]:
        return await self.get('id', *ids)

    async def get_by_name(self, *names) -> Union[Team, Iterable[Team]]:
        return await self.get('name', *names)

    async def get_by_tag(self, *tags) -> Union[Team, Iterable[Team]]:
        return await self.get('tag', *tags)
