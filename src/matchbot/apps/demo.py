import asyncio
from os import getenv
from dotenv import load_dotenv
from matchbot import redis
from matchbot.database import new_pool, gameserver, user, team, match
from random import randint

load_dotenv("../../../.env")


async def main():
    pool = await new_pool(host="localhost",
                          port=getenv("POSTGRES_PORT"),
                          user=getenv("POSTGRES_USER"),
                          password=getenv("POSTGRES_PASSWORD"),
                          database_name=getenv("POSTGRES_DB"))
    gameservertokens_table = gameserver.GameServerTokensTable(pool)
    gameservers_table = gameserver.GameServersTable(pool)
    users_table = user.UsersTable(pool)
    teams_table = team.TeamsTable(pool)
    matches_table = match.MatchesTable(pool)

    users =  [user.User(412041897672347230, "gla1ve"),
              user.User(989585413720717397, "Magisk"),
              user.User(560203868182492203, "dev1ce"),
              user.User(935591857927709199, "dupreeh"),
              user.User(397595632166082027, "Xyp9x"),
              user.User(141770607075093884, "s1mple"),
              user.User(990923677509346665, "Boombl4"),
              user.User(641151321829893629, "electronic"),
              user.User(846354701750384649, "Perfecto"),
              user.User(926869577381900030, "flamie")]

    team1 = team.Team(name="Astralis",
                      steam_ids=[user.steam_id for user in users[:5]],
                      tag="AST",
                      id="805718beaa0143af8414e7bc1df9c7ec")

    team2 = team.Team(name="Natus Vincere",
                      steam_ids=[user.steam_id for user in users[5:]],
                      tag="NAVI",
                      id="532ebcffe3264a3ea9d8a5f8a83b5c65")


    m1 = Match(team1_id="805718beaa0143af8414e7bc1df9c7ec",
               team2_id="532ebcffe3264a3ea9d8a5f8a83b5c65",
               maps=["de_dust2", "de_overpass", "de_vertigo"],
               sides=["team2_ct", "team1_ct", "knife"])

    await users_table.upsert(*users)
    await teams_table.upsert(team1, team2)
    await matches_table.upsert(m1)
    await gameservertokens_table.insert("FIRSTTOKEN")
    await gameservers_table.upsert(gameserver.GameServer("FIRSTTOKEN",
                                                         "192.168.0.1",
                                                         1, 2))
