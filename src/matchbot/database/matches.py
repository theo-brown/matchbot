from matchbot import Match
from typing import Union, Iterable


class MatchesTable:
    def __init__(self, dbi):
        self.dbi = dbi

    async def add(self, *matches: Match):
        await self.dbi.db.executemany("INSERT INTO matches(id, status, live_timestamp, team1_id, team2_id)"
                                      " VALUES ($1, $2, $3, $4, $5);",
                                      [(match.id, match.status, match.live_timestamp, match.teams[0].id, match.teams[1].id)
                                       for match in matches])

        await self.dbi.db.executemany("INSERT INTO match_maps(match_id, map_number, map_id, side)"
                                      " VALUES ($1, $2, $3, $4);",
                                      [(match.id, i+1, map, side)
                                       for match in matches
                                       for i, (map, side) in enumerate(zip(match.maps, match.sides))])

    async def update(self, *matches: Match):
        #TODO: add update to match_maps as well
        await self.dbi.db.executemany("UPDATE matches"
                                      " SET status = $2, live_timestamp = $3, team1_id = $4, team2_id = $5"
                                      " WHERE id = $1;",
                                      [(match.id, match.status, match.live_timestamp, match.teams[0].id, match.teams[1].id)
                                       for match in matches])

    async def get(self, column: str, *values) -> Union[Match, Iterable[Match]]:
        if column not in ['id', 'status', 'live_timestamp', 'team1_id', 'team2_id'] and column != 'team_id':
            raise ValueError(f"Column {column} not found in table"
                             " (expected 'id', 'status', 'live_timestamp', 'team1_id', 'team2_id',"
                             " or 'team_id' to match both team1_id and team2_id")
        matches = []
        if column == 'team_id':
            query = ("SELECT id, status, live_timestamp, team1_id, team2_id"
                     " FROM matches"
                    f" WHERE team1_id = ANY ($1) OR team2_id = ANY ($1);")
        else:
            query = ("SELECT id, status, live_timestamp, team1_id, team2_id"
                     " FROM matches"
                    f" WHERE {column} = ANY ($1);")
        for match_record in await self.dbi.db.fetch(query, values):
            team1, team2 = await self.dbi.teams.get_by_id(match_record.get('team1_id'), match_record.get('team2_id'))
            map_records = await self.dbi.db.fetch("SELECT map_id, side FROM match_maps WHERE match_id = $1",
                                                  match_record.get('id'))
            matches.append(Match(team1=team1,
                                 team2=team2,
                                 maps=[map_record.get('map_id') for map_record in map_records],
                                 sides=[map_record.get('side') for map_record in map_records],
                                 id=match_record.get('id'),
                                 live_timestamp=match_record.get('live_timestamp'),
                                 status=match_record.get('status')))
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

    async def get_by_status(self, *statuses: int) -> Union[Match, Iterable[Match]]:
        return await self.get('status', *statuses)

    async def get_by_live_timestamp(self, *live_timestamps: str) -> Union[Match, Iterable[Match]]:
        return await self.get('live_timestamp', *live_timestamps)

    async def get_by_team_id(self, *team_ids: str) -> Union[Match, Iterable[Match]]:
        return await self.get('team_id', *team_ids)
