from os import getenv
import asyncio
from matchbot.gameserver import GameServer, GameServerManager
from matchbot.database import DatabaseInterface
from matchbot import Match, Team


async def main():
    try:
        dbi = DatabaseInterface(host="database",
                                user=getenv("POSTGRES_USER"),
                                password=getenv("POSTGRES_PASSWORD"),
                                database_name=getenv("POSTGRES_DB"))
        await dbi.connect()

        ports = [i for i in range(int(getenv("PORT_MIN")),
                                  int(getenv("PORT_MAX")) + 1)]
        gotv_ports = [i for i in range(int(getenv("GOTV_PORT_MIN")),
                                       int(getenv("GOTV_PORT_MAX")) + 1)]

        gsm = GameServerManager([GameServer(token=token,
                                            ip=getenv("PUBLIC_IP"),
                                            port=ports.pop(),
                                            gotv_port=gotv_ports.pop())
                                            for token in await dbi.get_server_tokens()])

        team1 = Team("TEAM EVOLU",
                     await dbi.get_users('steam_id', 76561198922288040),
                     tag="EVL")
        team2 = Team("Bots",
                     [],
                     tag="BOT")

        match = Match(team1, team2, maps=["de_dust2", "de_inferno", "de_overpass"],
                      sides=["team1_ct", "team2_ct", "knife"])

        await gsm.start_match(match)

    finally:
        dbi.close()
        await gsm.stop_all()


if __name__ == "__main__":
    asyncio.run(main())
