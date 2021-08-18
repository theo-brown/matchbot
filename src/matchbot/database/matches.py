from __future__ import annotations
from matchbot import Match, MATCH_INITIALISING
from typing import Union, Iterable
import datetime
import asyncio


class MatchesTable:
    def __init__(self, dbi: DatabaseInterface):
        self.dbi = dbi

    async def add(self, *matches: Match):
        async with self.dbi.pool.acquire() as connection:
            await connection.executemany("INSERT INTO matches(id, status, created_timestamp, live_timestamp,"
                                                            " finished_timestamp, team1_id, team2_id)"
                                         " VALUES ($1, $2, $3, $4, $5, $6, $7);",
                                         [(match.id, match.status, match.created_timestamp, match.live_timestamp,
                                          match.finished_timestamp, match.teams[0].id, match.teams[1].id)
                                          for match in matches])

            await connection.executemany("INSERT INTO match_maps(match_id, map_number, map_id, side)"
                                         " VALUES ($1, $2, $3, $4);",
                                         [(match.id, i+1, map, side)
                                          for match in matches
                                          for i, (map, side) in enumerate(zip(match.maps, match.sides))])


    async def update(self, *matches: Match):
        await asyncio.gather(self.dbi.pool.executemany("UPDATE matches"
                                                       " SET status = $2, created_timestamp = $3, live_timestamp = $4,"
                                                       " finished_timestamp = $5, team1_id = $6, team2_id = $7"
                                                       " WHERE id = $1;",
                                                       [(match.id, match.status, match.created_timestamp,
                                                         match.live_timestamp, match.finished_timestamp,
                                                         match.teams[0].id, match.teams[1].id)
                                                         for match in matches]),
                             self.dbi.pool.executemany("INSERT INTO match_maps(match_id, map_number, map_id, side)"
                                                       " VALUES ($1, $2, $3, $4)"
                                                       " ON CONFLICT(match_id, map_number) DO UPDATE"
                                                       " SET map_id = $3, side = $4;",
                                                       [(match.id, i+1, map, side)
                                                        for match in matches
                                                        for i, (map, side) in enumerate(zip(match.maps, match.sides))]))

    async def get(self, column: str, *values) -> Union[Match, Iterable[Match]]:
        if column not in ['id', 'status', 'created_timestamp', 'live_timestamp', 'finished_timestamp',
                          'team1_id', 'team2_id'] and column != 'team_id':
            raise ValueError(f"Column {column} not found in table"
                             " (expected one of ['id', 'status', 'created_timestamp', 'live_timestamp',"
                             " 'finished_timestamp'', 'team1_id', 'team2_id'],"
                             " or 'team_id' to match from both team1_id and team2_id")

        if column == 'team_id':
            query = ("SELECT id, status, created_timestamp, live_timestamp, finished_timestamp, team1_id, team2_id"
                     " FROM matches"
                     f" WHERE team1_id = ANY ($1) OR team2_id = ANY ($1);")
        else:
            query = ("SELECT id, status, created_timestamp, live_timestamp, finished_timestamp, team1_id, team2_id"
                     " FROM matches"
                     f" WHERE {column} = ANY ($1);")
                     
        async with self.dbi.pool.acquire() as connection:
            # Get data from match table
            match_records = await connection.fetch(query, values)
            # Get data from maps table
            # map_records is a dict, keys: match id, values: list of records
            # TODO: Currently this performs a database operation for each match, which could probably be optimised
            map_records = {match_record.get('id'): await connection.fetch("SELECT map_id, side"
                                                                        " FROM match_maps"
                                                                        " WHERE match_id = $1"
                                                                        " ORDER BY map_number ASC",
                                                                         match_record.get('id'))
                                          for match_record in match_records}

        # Get data from teams table
        # sum([[1,2], [3,4]], []) produces a flattened list [1,2,3,4]
        # set() eliminates duplicates
        # Combine to produce a 1d list of all team ids
        all_team_ids = set(sum([[match_record.get('team1_id'), match_record.get('team2_id')]
                                for match_record in match_records], []))
        teams_dict = {team.id: team for team in await self.dbi.teams.get_by_id(*all_team_ids)}

        matches = [Match(team1=teams_dict[match_record.get('team1_id')],
                         team2=teams_dict[match_record.get('team2_id')],
                         maps=[record.get('map_id') for record in map_records[match_record.get('id')]],
                         sides=[record.get('side') for record in map_records[match_record.get('id')]],
                         id=match_record.get('id'),
                         status=match_record.get('status'),
                         created_timestamp=match_record.get('created_timestamp'),
                         live_timestamp=match_record.get('live_timestamp'),
                         finished_timestamp=match_record.get('finished_timestamp'))
                   for match_record in match_records]

        if len(values) == 1:
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                raise(LookupError(f"Multiple matching matches found with {column}={values[0]}"))
            else:
                raise(LookupError(f"No matching match found with {column}={values[0]}"))
        else:
            return matches

    async def get_by_id(self, *ids: str) -> Union[Match, Iterable[Match]]:
        return await self.get('id', *ids)

    async def get_by_status(self, *statuses: str) -> Union[Match, Iterable[Match]]:
        return await self.get('status', *statuses)

    async def get_by_created_timestamp(self, *created_timestamps: datetime.datetime) -> Union[Match, Iterable[Match]]:
        return await self.get('created_timestamp', *created_timestamps)

    async def get_by_live_timestamp(self, *live_timestamps: datetime.datetime) -> Union[Match, Iterable[Match]]:
        return await self.get('live_timestamp', *live_timestamps)

    async def get_by_finished_timestamp(self, *finished_timestamps: datetime.datetime) -> Union[Match, Iterable[Match]]:
        return await self.get('finished_timestamp', *finished_timestamps)

    async def get_by_team_id(self, *team_ids: str) -> Union[Match, Iterable[Match]]:
        return await self.get('team_id', *team_ids)

    async def set_as_live(self, *matches: Match):
        for match in matches:
            match.set_as_live()
        await self.update(*matches)

    async def set_as_initialising(self, *matches: Match):
        for match in matches:
            match.set_as_initialising()
        await self.update(*matches)
