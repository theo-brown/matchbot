from dotenv import load_dotenv
from os import getenv
from typing import Union, Iterable, Mapping
from uuid import uuid4
from secrets import token_urlsafe
import asyncio
import aiodocker
import aiorcon
from time import time
import json

# Load environment variables
load_dotenv()
SERVER_TOKEN = getenv("SERVER_TOKEN")
HOST_IP = getenv("HOST_IP")
HOST_PORT = getenv("HOST_PORT")
STEAM_ID = getenv("STEAM_ID")
# Connect to docker
docker = aiodocker.Docker()


async def get_steam_id_dict(*player_names):
    return {player_name: STEAM_ID for player_name in player_names}


class Team:
    def __init__(self, name: str, player_dict: Mapping[str, int], tag=""):
        self.name = name
        self.player_dict = player_dict
        self.players = list(self.player_dict.keys())
        self.ids = list(self.player_dict.values())
        self.tag = tag


async def new_team(name: str, player_names: Iterable[str], tag=""):
    player_dict = await get_steam_id_dict(*player_names)
    return Team(name, player_dict, tag)


class Match:
    def __init__(self, team1: Team, team2: Team, maps: Iterable[str], sides: Iterable[str]):
        self.teams = [team1, team2]
        self.maps = maps
        self.sides = sides
        self.id = uuid4().hex

        self.cfg = {}

        self.cfg["matchid"] = self.id
        self.cfg["num_maps"] = len(self.maps)
        self.cfg["maplist"] = self.maps
        self.cfg["skip_veto"] = True

        self.cfg["map_sides"] = self.sides

        self.cfg["cvars"] = {}
        players_per_team = max(len(self.teams[0].players), len(self.teams[1].players))
        self.cfg["players_per_team"] = players_per_team
        if players_per_team == 2:
            self.cfg["cvars"]["get5_warmup_cfg"] = "warmup_2v2.cfg"
            self.cfg["cvars"]["get5_live_cfg"] = "live_2v2.cfg"
        else:
            self.cfg["cvars"]["get5_warmup_cfg"] = "warmup_5v5.cfg"
            self.cfg["cvars"]["get5_live_cfg"] = "live_5v5.cfg"

        for i, team in enumerate(self.teams):
            self.cfg[f"team{i + 1}"] = {"name": team.name,
                                        "tag": team.tag,
                                        "players": {str(steam_id): "" for steam_id in team.ids}}

        self.json = json.dumps(self.cfg)

        self.server = GameServer(HOST_IP, HOST_PORT, id=self.id, match_config=self.json)


async def new_match(team1: Team, team2: Team, maps: Iterable[str], sides: Iterable[str]):
    match = Match(team1, team2, maps, sides)
    await match.server.start()
    return match


class GameServer:
    def __init__(self, ip, port=27015, gotv_port=27020, id=uuid4().hex, match_config=""):
        self.id = id
        self.ip = ip
        self.port = port
        self.gotv_port = gotv_port
        self.password = token_urlsafe(6)
        self.rcon_password = token_urlsafe(6)
        self.gotv_password = token_urlsafe(6)
        self.match_config = match_config

        self.connect_str = f"connect {self.ip}:{self.port}; password {self.password}"
        self.connect_gotv_str = f"connect {self.ip}:{self.gotv_port}; password {self.gotv_password}"

        self.container = None
        self.rcon = None

    async def start(self, timeout=8):
        config = {"Image": "theobrown/csgo-server:latest",
                  "Env": [f"SERVER_TOKEN={SERVER_TOKEN}",
                          f"PORT={self.port}",
                          f"GOTV_PORT={self.gotv_port}",
                          f"PASSWORD={self.password}",
                          f"RCON_PASSWORD={self.rcon_password}",
                          f"GOTV_PASSWORD={self.gotv_password}",
                          f"MATCH_CONFIG={self.match_config}"],
                  "HostConfig": {"NetworkMode": "host"}}
        print("Spawning server...")
        self.container = await docker.containers.run(config=config, name=self.id)
        await self.container.start()
        print("Establishing RCON connection...")
        start_time = time()
        duration = 0
        while (duration < timeout):
            duration = time() - start_time
            try:
                self.rcon = await aiorcon.RCON.create(self.ip, self.port, self.rcon_password, loop=asyncio.get_event_loop())
            except OSError as e:
                #print(f"RCON connection failed with error {e}\n"
                #      f"Retrying ({duration:.2f}s)...")
                continue
            except Exception as e:
                await self.stop()
                raise e
            else:
                break
        if duration >= timeout:
            await self.stop()
            raise OSError(f"RCON connection failed after {duration:.2f}s")
        else:
            print(f"RCON connection established after {duration:.2f}s.")
        print("Loading get5 config...")
        response = await self.rcon("get5_loadmatch match_config.json")
        print(response)

    async def stop(self):
        if self.rcon is not None:
            self.rcon.close()
            self.rcon = None
        if self.container is not None:
            await self.container.delete(force=True)
            self.container = None
