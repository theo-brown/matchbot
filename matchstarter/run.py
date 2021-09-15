import asyncio
from matchbot.apps.matchstarter import MatchStarter
from os import getenv


async def main():
    matchstarter = MatchStarter(db_host=getenv("POSTGRES_HOST"),
                                db_port=int(getenv("POSTGRES_PORT")),
                                db_user=getenv("POSTGRES_USER"),
                                db_password=getenv("POSTGRES_PASSWORD"),
                                db_name=getenv("POSTGRES_DB"),
                                redis_host=getenv("REDIS_HOST"),
                                redis_port=int(getenv("REDIS_PORT")))
    await matchstarter.connect()
    await matchstarter.start()


asyncio.run(main())
