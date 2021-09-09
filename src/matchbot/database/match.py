from __future__ import annotations
from typing import Iterable, Optional
import datetime
from uuid import uuid4
from operator import itemgetter

MATCH_CREATED = "CREATED"
MATCH_QUEUED = "QUEUED"
MATCH_LIVE = "LIVE"
MATCH_FINISHED = "FINISHED"


class Match:
    global MATCH_CREATED
    global MATCH_QUEUED
    global MATCH_LIVE
    global MATCH_FINISHED

    def __init__(self,
                 team1_id: str, team2_id: str,
                 maps: Iterable[str],
                 sides: Iterable[str],
                 id: Optional[str] = None,
                 status: str = MATCH_CREATED,
                 created_timestamp: Optional[datetime.datetime] = None,
                 live_timestamp: Optional[datetime.datetime] = None,
                 finished_timestamp: Optional[datetime.datetime] = None):
        self.team_ids = [team1_id, team2_id]
        self.maps = maps
        self.sides = sides
        self.id = id if id else uuid4().hex
        self.created_timestamp = created_timestamp if created_timestamp else datetime.datetime.now()
        self.live_timestamp = live_timestamp
        self.finished_timestamp = finished_timestamp
        if status in [MATCH_CREATED, MATCH_QUEUED, MATCH_LIVE, MATCH_FINISHED]:
            self.status = status
        else:
            raise ValueError(f"status must be one of {MATCH_CREATED, MATCH_READY, MATCH_LIVE, MATCH_FINISHED},"
                             f"got {status}.")

    def __str__(self):
        return ("Match:\n"
                f"\tID: {self.id}\n"
                f"\tStatus: {self.status}\n"
                f"\tTeam 1: {self.team_ids[0]}\n"
                f"\tTeam 2: {self.team_ids[1]}\n"
                f"\tMaps:\n {self.maps}\n"
                f"\tSides:\n {self.sides}\n"
                f"\tCreated at: {self.created_timestamp}\n"
                f"\tLive at: {self.live_timestamp}\n"
                f"\tFinished at: {self.finished_timestamp}\n")


def from_dict(match_dict: dict) -> Match:
    return Match(name=match_dict.get('name'),
                 steam_ids=match_dict.get('steam_ids'),
                 tag=match_dict.get('tag'),
                 id=match_dict.get('id'))


class MatchesTable:
    def __init__(self, pool: asyncpg.pool.Pool):
        self.pool = pool

    async def upsert(self, *matches: Match):
        async with self.pool.acquire() as connection:
            await connection.executemany("INSERT INTO matches(id, status, created_timestamp,"
                                         " live_timestamp, finished_timestamp, team1_id, team2_id)"
                                         " VALUES ($1, $2, $3, $4, $5, $6, $7)"
                                         " ON CONFLICT (id) DO UPDATE"
                                         " SET status = excluded.status,"
                                         " created_timestamp = excluded.created_timestamp,"
                                         " live_timestamp = excluded.live_timestamp,"
                                         " finished_timestamp = excluded.finished_timestamp,"
                                         " team1_id = excluded.team1_id,"
                                         " team2_id = excluded.team2_id;",
                                         [(match.id, match.status, match.created_timestamp, match.live_timestamp,
                                           match.finished_timestamp, match.team_ids[0], match.team_ids[1])
                                          for match in matches])
            await connection.executemany("INSERT INTO match_maps(match_id, map_number, map_id, side)"
                                         " VALUES ($1, $2, $3, $4);",
                                         [(match.id, i+1, map_id, side)
                                          for match in matches
                                          for i, (map_id, side) in enumerate(zip(match.maps, match.sides))])

    async def get(self, column: str, *values: Union[str, int]) -> Union[Match, Iterable[Match]]:
        if column not in ['id', 'status', 'created_timestamp', 'live_timestamp', 'finished_timestamp',
                          'team1_id', 'team2_id', 'map_id', 'side']:
            raise ValueError(f"Column {column} not found in table"
                             " (expected 'id', 'status', 'created_timestamp', 'live_timestamp', 'finished_timestamp'," 
                             "'team1_id', 'team2_id', 'map_id', or 'side').")

        async with self.pool.acquire() as connection:
            if column == 'map_id' or column == 'side':
                match_ids = set(record.get('match_id') for record in await connection.fetch("SELECT match_id FROM match_maps"
                                                                                           f" WHERE {column} = ANY($1);",
                                                                                            values))
                matches = await self.get('id', match_ids)
            else:
                matches_temp = [{'id': record.get('id'),
                                 'status': record.get('status'),
                                 'created_timestamp': record.get('created_timestamp'),
                                 'live_timestamp': record.get('live_timestamp'),
                                 'finished_timestamp': record.get('finished_timestamp'),
                                 'team1_id': record.get('team1_id'),
                                 'team2_id': record.get('team2_id')}
                                 for record in await connection.fetch("SELECT id, status, created_timestamp,"
                                                                      " live_timestamp, finished_timestamp, team1_id, "
                                                                      " team2_id FROM matches"
                                                                     f" WHERE {column} = ANY ($1);", values)]
                match_maps_sides = [{'match_id': record.get('match_id'),
                                     'map_number': record.get('map_number'),
                                     'map_id': record.get('map_id'),
                                     'side': record.get('side')}
                                    for record in await connection.fetch("SELECT match_id, map_number, map_id, side "
                                                                         "FROM match_maps "
                                                                         "WHERE match_id = ANY ($1);",
                                                                         [match['id'] for match in matches_temp])]
                maps_by_match = {}
                for map_dict in match_maps_sides:
                    match_id = map_dict['match_id']
                    if match_id in maps_by_match.keys():
                        maps_by_match[match_id]['maps'].append((map_dict['map_number'], map_dict['map_id']))
                        maps_by_match[match_id]['sides'].append((map_dict['map_number'], map_dict['side']))
                    else:
                        maps_by_match[match_id] = {'maps': [(map_dict['map_number'], map_dict['map_id'])],
                                                   'sides': [(map_dict['map_number'], map_dict['side'])]}

                for match_maps in maps_by_match.values():
                    match_maps['maps'].sort()
                    match_maps['maps'] = [m[1] for m in match_maps['maps']]
                    match_maps['sides'].sort()
                    match_maps['sides'] = [m[1] for m in match_maps['sides']]

                matches = [Match(id=match['id'],
                                 status=match['status'],
                                 created_timestamp=match['created_timestamp'],
                                 live_timestamp=match['live_timestamp'],
                                 finished_timestamp=match['finished_timestamp'],
                                 team1_id=match['team1_id'],
                                 team2_id=match['team2_id'],
                                 maps=maps_by_match[match['id']]['maps'],
                                 sides=maps_by_match[match['id']]['sides'])
                           for match in matches_temp]

        if len(values) == 1:
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                raise (LookupError(f"Multiple matching matches found with {column}={values[0]}."))
            else:
                raise (LookupError(f"No matching match found with {column}={values[0]}."))
        else:
            return matches
