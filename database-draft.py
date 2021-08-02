class PlayerStats:
    def __init__(self,
                 matchid: str,
                 mapnumber: int,
                 steamid: int,
                 team_name: str,
                 rounds_played: int,
                 name: str,
                 kills: int,
                 deaths: int,
                 assists: int,
                 flashbang_assists: int,
                 teamkills: int,
                 headshot_kills: int,
                 damage: int,
                 bomb_plants: int,
                 bomb_defuses: int,
                 v1: int,
                 v2: int,
                 v3: int,
                 v4: int,
                 v5: int,
                 k2: int,
                 k3: int,
                 k4: int,
                 k5: int,
                 firstkill_t: int,
                 firstkill_ct: int,
                 firstdeath_t: int,
                 firstdeath_ct: int,
                 tradekill: int,
                 kast: int,
                 contribution_score: int,
                 mvp: int):

class MapStats:
    def __init__(self, matchid: str, mapname: str, start_time: datetime, end_time: datetime,
                 winner: str, team1_score: int, team2_score: int):
        self.matchid = matchid
        self.start_time = start_time
        self.mapname = mapname
        self.end_time = end_time
        self.winner = winner
        self.team1_score = team1_score
        self.team2_score = team2_score


class MatchStats:
    def __init__(self, matchid: str, start_time: datetime, end_time: datetime, winner: str, series_type: str,
                 team1: Team, team1_score: int, team2: Team, team2_score: int):
        self.matchid = matchid
        self.start_time = start_time
        self.end_time = end_time
        self.winner = winner
        self.series_type = series_type
        self.team1 = team1
        self.team1_score = team1_score
        self.team2 = team2
        self.team2_score = team2_score

        self.maps = []

    def add_map(self, map: MapStats):
        self.maps.append(map)