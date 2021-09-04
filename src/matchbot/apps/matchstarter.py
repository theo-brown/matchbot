import asyncio
import aiodocker
import matchbot.redis
import matchbot.gameserver
import matchbot.database
import json
from typing import Optional
import asyncpg


class MatchStarter:
    def __init__(self, db_host: str, db_port: int, db_user: str,
                 db_password: str, db_name: str, db_timeout=5,
                 redis_host: str = 'localhost', redis_port: int = 6379,
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        self.docker = aiodocker.Docker()
        self.eventhandler = matchbot.redis.EventHandler(channel="match_queue",
                                                        callback=self.start_match,
                                                        loop=loop,
                                                        host=redis_host,
                                                        port=redis_port)
        self.db_pool = matchbot.database.new_pool(host=db_host, port=db_port, user=db_user,
                                                  password=db_password, database_name=db_name,
                                                  timeout=db_timeout)
        self.servers = matchbot.gameserver.GameServersTable(self.db_pool)

    def run(self):
        try:
            self.eventhandler.start()
        finally:
            self.eventhandler.stop()

    async def start_match(self, match_json: str):
        match = json.loads(match_json)


        server =
        config = {"Image": "theobrown/csgo-docker:latest",
                  "Env": [f"SERVER_TOKEN={server['token']}",
                          f"PORT={server['port']}",
                          f"GOTV_PORT={server['gotv_port']}",
                          f"PASSWORD={server['password']}",
                          f"RCON_PASSWORD={server['rcon_password']}",
                          f"GOTV_PASSWORD={server['gotv_password']}",
                          f"MATCH_CONFIG={server['match_config']}"],
                  "HostConfig": {"NetworkMode": "host"}}
        self.container = await self.docker.containers.run(config=config, name=server['id'])
