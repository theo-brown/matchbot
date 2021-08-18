from typing import Iterable, Optional
from uuid import uuid4
import json
import datetime

# Global constants for match status
MATCH_CREATED = 'CREATED'
MATCH_INITIALISING = 'INITIALISING'
MATCH_LIVE = 'LIVE'
MATCH_FINISHED = 'FINISHED'


class User:
    def __init__(self, steam_id, display_name, discord_id=None):
        self.steam_id = steam_id
        self.display_name = display_name
        self.discord_id = discord_id


class Team:
    def __init__(self, name: str, players: Iterable[User] = [], tag="", id=None):
        self.name = name
        self.players = players
        self.tag = tag
        if id:
            self.id = id
        else:
            self.id = uuid4().hex

    @property
    def display_names(self):
        return [player.display_name for player in self.players]

    @property
    def steam_ids(self):
        return [player.steam_id for player in self.players]

    @property
    def discord_ids(self):
        return [player.discord_id for player in self.players]


class Match:
    global MATCH_CREATED
    global MATCH_INITIALISING
    global MATCH_LIVE
    global MATCH_FINISHED

    def __init__(self, team1: Team, team2: Team, maps: Iterable[str], sides: Iterable[str],
                 id: Optional[str] = None, status: str = MATCH_CREATED,
                 created_timestamp: Optional[datetime.datetime] = None,
                 live_timestamp: Optional[datetime.datetime] = None,
                 finished_timestamp: Optional[datetime.datetime] = None):
        self.teams = [team1, team2]
        self.maps = maps
        self.sides = sides
        if id:
            self.id = id
        else:
            self.id = uuid4().hex
        if created_timestamp:
            self.created_timestamp = created_timestamp
        else:
            self.created_timestamp = datetime.datetime.now()
        self.live_timestamp = live_timestamp
        self.finished_timestamp = finished_timestamp
        if status in [MATCH_CREATED, MATCH_INITIALISING, MATCH_LIVE, MATCH_FINISHED]:
            self.status = status
        else:
            raise ValueError(f"status must be one of {MATCH_CREATED, MATCH_READY, MATCH_LIVE, MATCH_FINISHED},"
                             f"got {status}.")

        cvars = {}
        players_per_team = max(len(self.teams[0].players), len(self.teams[1].players))
        if players_per_team == 2:
            cvars["get5_warmup_cfg"] = "warmup_2v2.cfg"
            cvars["get5_live_cfg"] = "live_2v2.cfg"
        else:
            cvars["get5_warmup_cfg"] = "warmup_5v5.cfg"
            cvars["get5_live_cfg"] = "live_5v5.cfg"

        self.config = {"matchid": self.id,
                       "num_maps": len(self.maps),
                       "maplist": self.maps,
                       "skip_veto": True,
                       "map_sides": self.sides,
                       "players_per_team": players_per_team,
                       "cvars": cvars}

        for i, team in enumerate(self.teams):
            self.config[f"team{i + 1}"] = {"name": team.name,
                                           "tag": team.tag,
                                           "players": dict(zip(team.steam_ids, team.display_names))}

        self.config_json = json.dumps(self.config)

    def set_as_live(self):
        self.status = MATCH_LIVE
        self.live_timestamp = datetime.datetime.now()

    def set_as_initialising(self):
        self.status = MATCH_INITIALISING
