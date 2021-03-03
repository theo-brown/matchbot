from discord import Member, Role
import database.users

class Team:
    def __init__(self, team, captain=None, players=[]):
        if isinstance(team, Role):
            self.players = set(team.members)
            self.name = team.name
            self.mention = team.mention
            if isinstance(captain, Member) and captain in self.players:
                self.captain = captain
            else:
                self.captain = team.members[0]
        elif isinstance(team, Member):
            self.captain = team
            self.players = set(players + [self.captain])
            self.name = f"Team {self.captain.display_name}"
            self.mention = f"Team {self.captain.mention}"
        else:
            raise ValueError(f"Expected a Role and/or a Member "
                             f"(got {type(team)} and {type(captain)})")

    def add_player(self, player):
        self.players.add(player)
    
    def display(self):
        s = ""
        for player in self.players:
            s += f"{player.mention}\n"
        return s
    
    def get_players_ids(self):
        return [player.id for player in self.players]
    
    async def get_players_steam_ids(self):
        return await database.users.get_steam64_ids(self.get_players_ids())
    

class Map:
    def __init__(self, readable_name, ingame_name):
        self.readable_name = readable_name
        self.ingame_name = ingame_name
        self.sides = {"t": None, "ct": None}
        self.pickedby = None
        
    def pick(self, team: Team):
        self.pickedby = team
    
    def choose_side(self, team: Team, side: str):
        if side == "Counter-terrorists": side = "ct"
        if side == "Terrorists": side = "t"
        if side in ["t", "ct"]:
            self.sides[side] = team