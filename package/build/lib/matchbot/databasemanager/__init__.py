from dotenv import load_dotenv
from os import getenv
import asyncio
import aiopg
from typing import Iterable
from matchbot import Team, User

load_dotenv()
DB_HOST = getenv("DB_HOST")
DB_PORT = int(getenv("DB_PORT"))
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_DATABASE_NAME = getenv("DB_DATABASE_NAME")


class DatabaseManager:
    def __init__(self, host, port, user, password, database_name):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.database_name = database_name
        self.db = None
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.async_init())

    async def async_init(self):
        self.db = await aiomysql.connect(host=self.host,
                                         port=self.port,
                                         user=self.user,
                                         password=self.password,
                                         db=self.database_name,
                                         loop=self.loop)

        async with self.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS matchbot_users ("
                                 "steam_id     BIGINT      UNSIGNED NOT NULL,"
                                 "discord_id   BIGINT      UNSIGNED NOT NULL,"
                                 "display_name VARCHAR(64)          NOT NULL,"
                                 "PRIMARY KEY (steam_id),"
                                 "CONSTRAINT unique_user UNIQUE (steam_id, discord_id, display_name));")

            await cursor.execute("CREATE TABLE IF NOT EXISTS matchbot_teams ("
                                 "team_id           VARCHAR(32)          NOT NULL,"
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
                                 "matchid     VARCHAR(32)          NOT NULL,"
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
                                 "matchid     VARCHAR(32)          NOT NULL,"
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
                                 "matchid            VARCHAR(32)          NOT NULL,"
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
        del self.db
        self.db = None

    async def add_users(self, users: Iterable[User]):
        async with self.db.cursor() as cursor:
            await cursor.executemany("INSERT INTO matchbot_users(steam_id, discord_id, display_name)"
                                     " VALUES (%s, %s, %s) AS new_entry"
                                     " ON DUPLICATE KEY UPDATE steam_id = new_entry.steam_id,"
                                                              "discord_id = new_entry.discord_id,"
                                                              "display_name = new_entry.display_name;",
                                                               [(user.steam_id, user.discord_id, user.display_name)
                                                                for user in users])
            await self.db.commit()

    async def get_users(self, column: str, values: Iterable) -> Iterable[User]:
        if column not in ["steam_id", "discord_id", "display_name"]:
            raise ValueError(f"Unrecognised column {column} (expected 'steam_id', 'discord_id', or 'display_name')")
        async with self.db.cursor() as cursor:
            parameters = ", ".join(['%s'] * len(values))
            await cursor.execute("SELECT steam_id, discord_id, display_name"
                                 f" FROM matchbot_users WHERE {column} IN ({parameters});", values)
            users_raw = await cursor.fetchall()
        return [User(steam_id=user[0], discord_id=user[1], display_name=user[2]) for user in users_raw]

    async def add_team(self, team: Team):
        number_of_players = len(team.players)
        steam_ids_padded = team.steam_ids() + [None]*(5 - number_of_players)
        async with self.db.cursor() as cursor:
            await cursor.execute(f"INSERT INTO matchbot_teams(team_id, team_name, team_tag, number_of_players, "
                                                             "steamid_p1, steamid_p2, steamid_p3, steamid_p4, steamid_p5)"
                                      " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) AS new_entry"
                                      " ON DUPLICATE KEY UPDATE team_id = new_entry.team_id,"
                                                               "team_name = new_entry.team_name,"
                                                               "team_tag = new_entry.team_tag,"
                                                               "number_of_players = new_entry.number_of_players,"
                                                               "steamid_p1 = new_entry.steamid_p1,"
                                                               "steamid_p2 = new_entry.steamid_p2,"
                                                               "steamid_p3 = new_entry.steamid_p3,"
                                                               "steamid_p4 = new_entry.steamid_p4,"
                                                               "steamid_p5 = new_entry.steamid_p5;",
                                                                (team.id, team.name, team.tag, len(team.players),
                                                                 *steam_ids_padded))
            await self.db.commit()

    async def get_teams(self, column: str, values: Iterable) -> Iterable[Team]:
        if column not in ["team_id", "team_name", "team_tag", "steam_id"]:
            raise ValueError(f"Unrecognised column {column} (expected 'team_id', 'team_name', 'team_tag', 'steam_id')")

        parameters = ", ".join(['%s'] * len(values))
        if column == "steam_id":
            query = ("SELECT team_id, team_name, team_tag, number_of_players, "
                     "steamid_p1, steamid_p2, steamid_p3, steamid_p4, steamid_p5"
                    f" FROM matchbot_teams WHERE steamid_p1 IN ({parameters})"
                                            f"OR steamid_p2 IN ({parameters})"
                                            f"OR steamid_p3 IN ({parameters})"
                                            f"OR steamid_p4 IN ({parameters})"
                                            f"OR steamid_p5 IN ({parameters});")
            values = values*5
        else:
            query = ("SELECT team_id, team_name, team_tag, number_of_players, "
                     "steamid_p1, steamid_p2, steamid_p3, steamid_p4, steamid_p5"
                    f" FROM matchbot_teams WHERE {column} IN ({parameters});")
        async with self.db.cursor() as cursor:
            await cursor.execute(query, values)
            teams_raw = await cursor.fetchall()
        output = []
        for team in teams_raw:
            team_id = team[0]
            team_name = team[1]
            team_tag = team[2]
            num_players = team[3]
            steam_ids = team[4:4+num_players]
            players = await self.get_users('steam_id', steam_ids)
            output.append(Team(name=team_name, players=players, tag=team_tag, id=team_id))
        return output
