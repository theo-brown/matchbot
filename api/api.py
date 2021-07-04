from typing import Iterable
from uuid import uuid4


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