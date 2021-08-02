from typing import Iterable
from uuid import uuid4
import json


class User:
    def __init__(self, steam_id, display_name, discord_id=None):
        self.steam_id = steam_id
        self.display_name = display_name
        self.discord_id = discord_id


class Team:
    def __init__(self, name: str, players: Iterable[User], tag="", id=uuid4().hex):
        self.name = name
        self.players = players
        self.tag = tag
        self.id = id

    def display_names(self):
        return [player.display_name for player in self.players]

    def steam_ids(self):
        return [player.steam_id for player in self.players]

    def discord_ids(self):
        return [player.discord_id for player in self.players]


class Match:
    def __init__(self, team1: Team, team2: Team, maps: Iterable[str], sides: Iterable[str]):
        self.teams = [team1, team2]
        self.maps = maps
        self.sides = sides
        self.id = uuid4().hex

        cvars = {}
        players_per_team = max(len(self.teams[0].players), len(self.teams[1].players))
        if players_per_team == 2:
            cvars["get5_warmup_cfg"] = "warmup_2v2.cfg"
            cvars["get5_live_cfg"] = "live_2v2.cfg"
        else:
            cvars["get5_warmup_cfg"] = "warmup_5v5.cfg"
            cvars["get5_live_cfg"] = "live_5v5.cfg"

        self.cfg = {"matchid": self.id,
                    "num_maps": len(self.maps),
                    "maplist": self.maps,
                    "skip_veto": True,
                    "map_sides": self.sides,
                    "players_per_team": players_per_team,
                    "cvars": cvars}

        for i, team in enumerate(self.teams):
            self.cfg[f"team{i + 1}"] = {"name": team.name,
                                        "tag": team.tag,
                                        "players": {player.steam_id: player.display_name for player in team.players}}

        self.json = json.dumps(self.cfg)

        self.server = None
