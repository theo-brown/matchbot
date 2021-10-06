from __future__ import annotations
from src import Match, Team
from matchbot.apps import MatchbotBaseApp
from sqlalchemy import select

#
# class MatchStarter(MatchbotBaseApp):
#     def __init__(self):
#         pass
#         # self.docker = aiodocker.Docker()
#         # self.new_event_handler('match_queue', self.start_match)
#
#     async def generate_config(self, match_id: str) -> dict:
#         async with self.new_session() as session:
#             match_result = await session.execute(select(Match).where(Match.id==match_id))
#             match = match_result.scalar()
#             team1_result = await session.execute(select(Team).where(Team.id==match.team1_id))
#             team1 = team1_result.scalar()
#             team2_result = await session.execute(select(Team).where(Team.id==match.team2_id))
#             team2 = team2.scalar()
#
#         players_per_team = max(len(team1.users), len(team2.users))
#         return {"matchid": match.id,
#                 "num_maps": len(match.maps),
#                 "maplist": match.maps,
#                 "skip_veto": True,
#                 "map_sides": [match_map.side for match_map in match.maps],
#                 "players_per_team": players_per_team,
#                 "team1": {"name": team1.name,
#                           "tag": team1.tag,
#                           "players": {user.steam_id: user.display_name
#                                       for user in team1.users}},
#                 "team2": {"name": team2.name,
#                           "tag": team2.tag,
#                           "players": {user.steam_id: user.display_name
#                                       for user in team2.users}},
#                 "cvars": {"get5_warmup_cfg": "warmup_2v2.cfg" if players_per_team == 2 else "warmup_5v5.cfg",
#                           "get5_live_cfg": "live_2v2.cfg" if players_per_team == 2 else "live_5v5.cfg"}}

    #
    # async def start_match(self, match_json: str):
    #     print("matchstarter.start_match() triggered")
    #     match = matchbot.database.match.from_json_str(match_json)
    #
    #     try:
    #         print("Getting available server...")
    #         available_servers = await self.servers.get('match_id', None)
    #         if isinstance(available_servers, matchbot.database.gameserver.GameServer):
    #             server = available_servers
    #         else:
    #             server = available_servers[0]
    #     except LookupError as err:
    #         #TODO: handle this error nicely
    #         raise LookupError("No free servers available.")
    #
    #     print(f"Available {server}")
    #     match_config = await self.generate_config(match)
    #     print(f"Match config: {match_config}")
    #     server.generate_passwords()
    #
    #     container_config = {"Image": "theobrown/csgo-docker:latest",
    #                         "Env": [f"SERVER_TOKEN={server.token}",
    #                                 f"PORT={server.port}",
    #                                 f"GOTV_PORT={server.gotv_port}",
    #                                 f"PASSWORD={server.password}",
    #                                 f"RCON_PASSWORD={server.rcon_password}",
    #                                 f"GOTV_PASSWORD={server.gotv_password}",
    #                                 f"MATCH_CONFIG={match_config}"],
    #                         "HostConfig": {"NetworkMode": "host"}}
    #
    #     print(f"Container config: {container_config}")
    #     self.container = await self.docker.containers.run(config=container_config, name=server.id)
    #
    #     print("Updating tables...")
    #     match.status = matchbot.database.match.MATCH_LIVE
    #     await self.matches.upsert(match)
    #     server.match_id = match.id
    #     await self.servers.upsert(server)
    #     print("Done.")
