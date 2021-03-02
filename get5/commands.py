import json
from classes import Team, Map
from typing import Iterable


async def generate_config(team1: Team, team2: Team, maps: Iterable[Map]):
    config = {}
    # Match settings
    config["matchid"] = f"{team1.name} vs {team2.name}"
    config["num_maps"] = len(maps)
    config["maplist"] = [m.ingame_name for m in maps]
    config["skip_veto"] = True
    config["map_sides"] = []
    for m in maps:
        if m.sides["ct"] == team1:
            config["map_sides"].append("team1_ct")
        elif m.sides["ct"] == team2:
            config["map_sides"].append("team2_ct")
        else:
            config["map_sides"].append("knife")
    # Team settings
    for i, team in enumerate([team1, team2]):
        config[f"team{i+1}"] = {}
        t = config[f"team{i+1}"]
        t["name"] = team.name
        t["players"] = await team.get_players_steam_ids()
    
    # with open("get5/configs/match.cfg", 'w') as f:
    #     json.dump(config, f)

    return config