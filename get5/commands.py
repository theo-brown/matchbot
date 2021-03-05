import json
from classes import Team, Map
from typing import Iterable
from valve.rcon import execute as rcon_execute
from os import getenv

async def generate_config(team1: Team, team2: Team, maps: Iterable[Map], gametype='5v5_bo1'):
    config = {}
    # Match settings
    config["matchid"] = f"{team1.name} vs {team2.name}"
    config["num_maps"] = len(maps)
    config["maplist"] = [m.ingame_name for m in maps]
    config["skip_veto"] = True
    config["cvars"] = {}
    config["cvars"]["get5_check_auths"] = 1
    if '2v2' in gametype:
        config["cvars"]["get5_warmup_cfg"] = "get5/warmup_2v2.cfg"
        config["cvars"]["get5_live_cfg"] = "get5/live_2v2.cfg"
    else:
        config["cvars"]["get5_warmup_cfg"] = "get5/warmup_5v5.cfg"
        config["cvars"]["get5_live_cfg"] = "get5/live_5v5.cfg"
    config["map_sides"] = []
    for m in maps:
        if m.sides["ct"] == team1:
            config["map_sides"].append("team1_ct")
        elif m.sides["ct"] == team2:
            config["map_sides"].append("team2_ct")
        elif m.sides["t"] == team1:
            config["map_sides"].append("team1_t")
        elif m.sides["t"] == team2:
            config["map_sides"].append("team2_t")
        else:
            config["map_sides"].append("knife")
    # Team settings
    for i, team in enumerate([team1, team2]):
        config[f"team{i+1}"] = {}
        t = config[f"team{i+1}"]
        t["name"] = team.name
        t["players"] = [str(i) for i in await team.get_players_steam_ids()]
    
    with open("get5/configs/match_config.json", 'w') as f:
        json.dump(config, f)

    return config

def get_config_from_file():
    with open("configs/match_config.json") as f:
        config = json.load(f)
    return config

def force_loadmatch(server_ip, server_port, rcon_password):
    endmatch(server_ip, server_port, rcon_password)
    loadmatch(server_ip, server_port, rcon_password)

def loadmatch(server_ip, server_port, rcon_password):
    rcon_execute((server_ip, server_port), rcon_password, f"get5_loadmatch_url \"{getenv('MATCH_CONFIG_URL')}\"")

def endmatch(server_ip, server_port, rcon_password):
    rcon_execute((server_ip, server_port), rcon_password, f"get5_endmatch")

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv('../.env')