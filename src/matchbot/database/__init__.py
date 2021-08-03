import asyncio
import aiopg
from typing import Iterable
from matchbot import Team, User
from matchbot.gameservermanager.gameserver import GameServer


class DatabaseInterface:

    def __init__(self, host, port, user, password, database_name):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.database_name = database_name
        self.db = None
        asyncio.get_event_loop().run_until_complete(self.init_db())

    async def init_db(self):
        self.db = await aiopg.connect(host=self.host,
                                      port=self.port,
                                      user=self.user,
                                      password=self.password,
                                      database=self.database_name)

    def close(self):
        self.db.close()
        del self.db
        self.db = None

    async def add_gameserver(self, server_token, ip, port, gotv_port):
        async with self.db.cursor() as cursor:
            await cursor.execute("INSERT INTO game_servers(server_token, ip, port, gotv_port)"
                                 " VALUES (%s, %s, %s, %s);", (server_token, ip, port, gotv_port))

    async def generate_gameservers(self):
        gameservers = []
        async with self.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM game_servers")
            for server in cursor.fetchall():
                gameservers.append(GameServer(server[0], server[1], server[2], server[3]))
        return gameservers

    #async def add_users(self, users: Iterable[User]):
    #    async with self.db.cursor() as cursor:
    #        await cursor.executemany("INSERT INTO matchbot_users(steam_id, discord_id, display_name)"
    #                                 " VALUES (%s, %s, %s) AS new_entry"
    #                                 " ON DUPLICATE KEY UPDATE steam_id = new_entry.steam_id,"
    #                                                          "discord_id = new_entry.discord_id,"
    #                                                          "display_name = new_entry.display_name;",
    #                                                           [(user.steam_id, user.discord_id, user.display_name)
    #                                                            for user in users])
    #        await self.db.commit()

    #async def get_users(self, column: str, values: Iterable) -> Iterable[User]:
    #    if column not in ["steam_id", "discord_id", "display_name"]:
    #        raise ValueError(f"Unrecognised column {column} (expected 'steam_id', 'discord_id', or 'display_name')")
    #    async with self.db.cursor() as cursor:
    #        parameters = ", ".join(['%s'] * len(values))
    #        await cursor.execute("SELECT steam_id, discord_id, display_name"
    #                             f" FROM matchbot_users WHERE {column} IN ({parameters});", values)
    #        users_raw = await cursor.fetchall()
    #    return [User(steam_id=user[0], discord_id=user[1], display_name=user[2]) for user in users_raw]
