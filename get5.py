import json
from classes import Team, Map
from typing import Iterable


def generate_get5_config(team1: Team, team2: Team, maps: Iterable[Map]):
    config = {}
    # Match settings
    config["matchid"] = f"{team1.name} vs {team2.name}"
    config["num_maps"] = len(maps)
    config["maplist"] = [m.ingame_name for m in maps]
    config["skip_veto"] = True
    # Team settings
    for i, team in enumerate([team1, team2]):
        config[f"team{i+1}"] = {}
        t = config[f"team{i+1}"]
        t["name"] = team.name
        t["players"] = team.get_players_steam_ids()
    
    with open("match.cfg", 'w') as f:
        json.dump(config, f)

    return config