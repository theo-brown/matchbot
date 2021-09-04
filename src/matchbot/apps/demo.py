import asyncio
from os import getenv
from dotenv import load_dotenv
from matchbot import redis
from matchbot.database import new_pool, gameserver, user, team
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

    def fake_steamid():
        return randint(1e17, 1e18)

    users =  [user.User(fake_steamid(), "gla1ve"),
              user.User(fake_steamid(), "Magisk"),
              user.User(fake_steamid(), "dev1ce"),
              user.User(fake_steamid(), "dupreeh"),
              user.User(fake_steamid(), "Xyp9x"),
              user.User(fake_steamid(), "s1mple"),
              user.User(fake_steamid(), "Boombl4"),
              user.User(fake_steamid(), "electronic"),
              user.User(fake_steamid(), "Perfecto"),
              user.User(fake_steamid(), "flamie")]

    team1 = team.Team(name="Astralis",
                      steam_ids=[user.steam_id for user in users[:5]],
                      tag="AST")

    team2 = team.Team(name="Natus Vincere",
                      steam_ids=[user.steam_id for user in users[5:]],
                      tag="NAVI")

    await users_table.upsert(*users)
