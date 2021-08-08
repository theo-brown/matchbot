from typing import Iterable
from uuid import uuid4
import json
from datetime import datetime


# Global constants for match status
MATCH_SCHEDULED = 0
MATCH_QUEUED = 1
MATCH_LIVE = 2
MATCH_FINISHED = 3


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
    global MATCH_SCHEDULED
    global MATCH_QUEUED
    global MATCH_LIVE
    global MATCH_FINISHED

    def __init__(self, team1: Team, team2: Team, maps: Iterable[str], sides: Iterable[str],
                 id=None, live_timestamp=None, status=None):
        self.teams = [team1, team2]
        self.maps = maps
        self.sides = sides
        if id:
            self.id = id
        else:
            self.id = uuid4().hex
        if live_timestamp:
            self.live_timestamp = live_timestamp
        else:
            self.live_timestamp = datetime.now()
        if status is not None:
            self.status = status
        else:
            status = MATCH_SCHEDULED

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
