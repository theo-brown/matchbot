from __future__ import annotations
import asyncio
import aiodocker
import matchbot.redis
import matchbot.database
import matchbot.database.gameserver
import matchbot.database.match
import matchbot.database.user
import matchbot.database.team
from typing import Optional
import asyncpg


class MatchStarter:
    def __init__(self, db_host: str, db_port: int, db_user: str,
                 db_password: str, db_name: str, db_timeout=5,
                 redis_host: str = 'localhost', redis_port: int = 6379,
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.db_timeout = db_timeout
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.loop = loop
        self.db_pool = None
        self.servers = None
        self.matches = None
        self.teams = None
        self.users = None

        self.docker = aiodocker.Docker()
        self.eventhandler = matchbot.redis.EventHandler(channel="match_queue",
                                                        callback=self.start_match,
                                                        loop=self.loop,
                                                        host=self.redis_host,
                                                        port=self.redis_port)

    async def connect(self):
        self.db_pool = await matchbot.database.new_pool(host=self.db_host, port=self.db_port, user=self.db_user,
                                                        password=self.db_password, database_name=self.db_name,
                                                        timeout=self.db_timeout)
        self.servers = matchbot.database.gameserver.GameServersTable(self.db_pool)
        self.matches = matchbot.database.match.MatchesTable(self.db_pool)
        self.teams = matchbot.database.team.TeamsTable(self.db_pool)
        self.users = matchbot.database.user.UsersTable(self.db_pool)

    async def start(self):
        self.eventhandler.start()

    async def stop(self):
        self.eventhandler.stop()
        self.db_pool.close()
        self.servers = None
        self.matches = None
        self.teams = None
        self.users = None

    async def generate_config(self, match: Match) -> dict:
        print("Fetching teams...")
        team1, team2 = await self.teams.get('id', match.team_ids[0], match.team_ids[1])
        print(f"{team1}\n{team2}")

        players_per_team = max(len(team1.steam_ids), len(team2.steam_ids))
        return {"matchid": match.id,
                "num_maps": len(match.maps),
                "maplist": match.maps,
                "skip_veto": True,
                "map_sides": match.sides,
                "players_per_team": players_per_team,
                "team1": {"name": team1.name,
                          "tag": team1.tag,
                          "players": {user.steam_id: user.display_name
                                      for user in await self.users.get('steam_id', *team1.steam_ids)}},
                "team2": {"name": team2.name,
                          "tag": team2.tag,
                          "players": {user.steam_id: user.display_name
                                      for user in await self.users.get('steam_id', *team2.steam_ids)}},
                "cvars": {"get5_warmup_cfg": "warmup_2v2.cfg" if players_per_team == 2 else "warmup_5v5.cfg",
                          "get5_live_cfg": "live_2v2.cfg" if players_per_team == 2 else "live_5v5.cfg"}}


    async def start_match(self, match_json: str):
        match = matchbot.database.match.from_json_str(match_json)

        try:
            print("Getting available server...")
            available_servers = await self.servers.get('match_id', None)
            if isinstance(available_servers, matchbot.database.gameserver.GameServer):
                server = available_servers
            else:
                server = available_servers[0]
        except LookupError as err:
            #TODO: handle this error nicely
            raise LookupError("No free servers available.")

        print(f"Available {server}")
        match_config = await self.generate_config(match)
        print(f"Match config: {match_config}")
        server.generate_passwords()

        container_config = {"Image": "theobrown/csgo-docker:latest",
                            "Env": [f"SERVER_TOKEN={server.token}",
                                    f"PORT={server.port}",
                                    f"GOTV_PORT={server.gotv_port}",
                                    f"PASSWORD={server.password}",
                                    f"RCON_PASSWORD={server.rcon_password}",
                                    f"GOTV_PASSWORD={server.gotv_password}",
                                    f"MATCH_CONFIG={match_config}"],
                            "HostConfig": {"NetworkMode": "host"}}

        print(f"Container config: {container_config}")
        self.container = await self.docker.containers.run(config=container_config, name=server.id)

        print("Updating tables...")
        match.status = matchbot.database.match.MATCH_LIVE
        await self.matches.upsert(match)
        server.match_id = match.id
        await self.servers.upsert(server)
        print("Done.")
