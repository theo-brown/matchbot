from dotenv import load_dotenv
from os import getenv
import aiomysql
import asyncio

load_dotenv()
DB_HOST = getenv("DB_HOST")
DB_PORT = int(getenv("DB_PORT"))
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_DATABASE_NAME = getenv("DB_DATABASE_NAME")


class DatabaseManager():
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.async_init())

    async def async_init(self):
        self.db = await aiomysql.connect(host=DB_HOST,
                                         port=DB_PORT,
                                         user=DB_USER,
                                         password=DB_PASSWORD,
                                         db=DB_DATABASE_NAME,
                                         loop=self.loop)

        async with self.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS matchbot_users ("
                                 "steam_id     BIGINT      UNSIGNED NOT NULL,"
                                 "discord_id   BIGINT      UNSIGNED NOT NULL,"
                                 "display_name VARCHAR(64)          NOT NULL,"
                                 "PRIMARY KEY (steam_id),"
                                 "CONSTRAINT unique_user UNIQUE (steam_id, discord_id, display_name));")

            await cursor.execute("CREATE TABLE IF NOT EXISTS matchbot_teams ("
                                 "team_id           BIGINT      UNSIGNED NOT NULL,"
                                 "team_name         VARCHAR(64)          NOT NULL,"
                                 "team_tag          VARCHAR(15)          NOT NULL DEFAULT '',"
                                 "number_of_players TINYINT     UNSIGNED NOT NULL,"
                                 "steamid_p1        BIGINT      UNSIGNED          DEFAULT NULL,"
                                 "steamid_p2        BIGINT      UNSIGNED          DEFAULT NULL,"
                                 "steamid_p3        BIGINT      UNSIGNED          DEFAULT NULL,"
                                 "steamid_p4        BIGINT      UNSIGNED          DEFAULT NULL,"
                                 "steamid_p5        BIGINT      UNSIGNED          DEFAULT NULL,"
                                 "PRIMARY KEY (team_id));")

            await cursor.execute("CREATE TABLE IF NOT EXISTS matchbot_stats_matches ("
                                 "matchid     BIGINT      UNSIGNED NOT NULL,"
                                 "start_time  DATETIME             NOT NULL,"
                                 "end_time    DATETIME             NULL     DEFAULT NULL,"
                                 "winner      VARCHAR(64)          NOT NULL DEFAULT '',"
                                 "series_type VARCHAR(64)          NOT NULL DEFAULT '',"
                                 "team1_name  VARCHAR(64)          NOT NULL DEFAULT '',"
                                 "team1_score SMALLINT    UNSIGNED NOT NULL DEFAULT '0',"
                                 "team2_name  VARCHAR(64)          NOT NULL DEFAULT '',"
                                 "team2_score SMALLINT    UNSIGNED NOT NULL DEFAULT '0',"
                                 "PRIMARY KEY (matchid));")

            await cursor.execute("CREATE TABLE IF NOT EXISTS matchbot_stats_maps ("
                                 "matchid     BIGINT      UNSIGNED NOT NULL,"
                                 "mapnumber   TINYINT     UNSIGNED NOT NULL,"
                                 "start_time  DATETIME             NOT NULL,"
                                 "end_time    DATETIME             NULL     DEFAULT NULL,"
                                 "winner      VARCHAR(64)              NOT NULL DEFAULT '',"
                                 "mapname     VARCHAR(64)              NOT NULL DEFAULT '',"
                                 "team1_score SMALLINT    UNSIGNED NOT NULL DEFAULT '0',"
                                 "team2_score SMALLINT    UNSIGNED NOT NULL DEFAULT '0',"
                                 "PRIMARY KEY (matchid, mapnumber),"
                                 "CONSTRAINT matchbot_stats_maps_matchid FOREIGN KEY (matchid)"
                                 " REFERENCES matchbot_stats_matches (matchid));")

            await cursor.execute("CREATE TABLE IF NOT EXISTS matchbot_stats_players ("
                                 "matchid            BIGINT      UNSIGNED NOT NULL,"
                                 "mapnumber          TINYINT     UNSIGNED NOT NULL,"
                                 "steamid64          BIGINT      UNSIGNED NOT NULL,"
                                 "team               VARCHAR(64)          NOT NULL DEFAULT '',"
                                 "rounds_played      SMALLINT    UNSIGNED NOT NULL,"
                                 "name               VARCHAR(64)          NOT NULL,"
                                 "kills              SMALLINT    UNSIGNED NOT NULL,"
                                 "deaths             SMALLINT    UNSIGNED NOT NULL,"
                                 "assists            SMALLINT    UNSIGNED NOT NULL,"
                                 "flashbang_assists  SMALLINT    UNSIGNED NOT NULL,"
                                 "teamkills          SMALLINT    UNSIGNED NOT NULL,"
                                 "headshot_kills     SMALLINT    UNSIGNED NOT NULL,"
                                 "damage             INT         UNSIGNED NOT NULL,"
                                 "bomb_plants        SMALLINT    UNSIGNED NOT NULL,"
                                 "bomb_defuses       SMALLINT    UNSIGNED NOT NULL,"
                                 "v1                 SMALLINT    UNSIGNED NOT NULL,"
                                 "v2                 SMALLINT    UNSIGNED NOT NULL,"
                                 "v3                 SMALLINT    UNSIGNED NOT NULL,"
                                 "v4                 SMALLINT    UNSIGNED NOT NULL,"
                                 "v5                 SMALLINT    UNSIGNED NOT NULL,"
                                 "2k                 SMALLINT    UNSIGNED NOT NULL,"
                                 "3k                 SMALLINT    UNSIGNED NOT NULL,"
                                 "4k                 SMALLINT    UNSIGNED NOT NULL,"
                                 "5k                 SMALLINT    UNSIGNED NOT NULL,"
                                 "firstkill_t        SMALLINT    UNSIGNED NOT NULL,"
                                 "firstkill_ct       SMALLINT    UNSIGNED NOT NULL,"
                                 "firstdeath_t       SMALLINT    UNSIGNED NOT NULL,"
                                 "firstdeath_ct      SMALLINT    UNSIGNED NOT NULL,"
                                 "tradekill          SMALLINT    UNSIGNED NOT NULL,"
                                 "kast               SMALLINT    UNSIGNED NOT NULL,"
                                 "contribution_score SMALLINT    UNSIGNED NOT NULL,"
                                 "mvp                SMALLINT    UNSIGNED NOT NULL,"
                                 "PRIMARY KEY (matchid, mapnumber, steamid64),"
                                 " CONSTRAINT matchbot_stats_players_matchid FOREIGN KEY (matchid)"
                                 " REFERENCES matchbot_stats_matches (matchid));")

            await self.db.commit()

    def close(self):
        self.db.close()

    async def add_users(self, users):
        async with self.db.cursor() as cursor:
            await cursor.executemany(("INSERT INTO matchbot_users(steam_id, discord_id, display_name)"
                                      " VALUES (%s, %s, %s) AS new_entry"
                                      " ON DUPLICATE KEY UPDATE steam_id = new_entry.steam_id,"
                                                               "discord_id = new_entry.discord_id,"
                                                               "display_name = new_entry.display_name;"),
                                                                users)
            await self.db.commit()

    async def get_users_from_steam_ids(self, steam_ids):
        async with self.db.cursor() as cursor:
            parameters = ", ".join(['%s'] * len(steam_ids))
            await cursor.execute("SELECT steam_id, discord_id, display_name"
                                 f" FROM matchbot_users WHERE steam_id IN ({parameters});", steam_ids)
            users = await cursor.fetchall()
        return users

    async def get_users_from_discord_ids(self, discord_ids):
        async with self.db.cursor() as cursor:
            parameters = ", ".join(['%s'] * len(discord_ids))
            await cursor.executemany("SELECT steam_id, discord_id, display_name"
                                      f" FROM matchbot_users WHERE discord_id IN ({parameters});", discord_ids)
            users = await cursor.fetchall()
        return users

    async def get_users_from_display_names(self, display_names):
        async with self.db.cursor() as cursor:
            parameters = ", ".join(['%s'] * len(display_names))
            await cursor.executemany("SELECT steam_id, discord_id, display_name"
                                      f" FROM matchbot_users WHERE display_name IN {parameters};", display_names)
            users = await cursor.fetchall()
        return users