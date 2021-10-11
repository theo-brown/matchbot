from __future__ import annotations
import aiodocker
from matchbot import database as db
from matchbot.apps import MatchbotBaseApp
from sqlalchemy import select
from uuid import UUID
from secrets import token_urlsafe


class MatchStarter(MatchbotBaseApp):
    def __init__(self, *args, **kwargs):
        self.docker = aiodocker.Docker()
        self.new_event_handler('match_queue', self.start_match)
        super().__init__(*args, **kwargs)

    async def start_match(self, match_id: UUID):
        async with self.new_session() as session:
            match = await session.get(db.models.Match, match_id)
            r = await session.execute(select(db.models.Server).where(db.models.Server.match_id is None))
            server = r.scalars().one()
            if not server:
                raise LookupError('No available servers.')
            server.match_id = match.id
            server.password = token_urlsafe()
            server.gotv_password = token_urlsafe()
            server.rcon_password = token_urlsafe()
            container_config = {"Image": "theobrown/csgo-docker:latest",
                                "Env": [f"SERVER_TOKEN={server.token}",
                                        f"PORT={server.port}",
                                        f"GOTV_PORT={server.gotv_port}",
                                        f"PASSWORD={server.password}",
                                        f"RCON_PASSWORD={server.rcon_password}",
                                        f"GOTV_PASSWORD={server.gotv_password}",
                                        f"MATCH_CONFIG={match.config}"],
                                "HostConfig": {"NetworkMode": "host"}}
            await self.docker.containers.run(config=container_config, name=server.id)
            match.status = 'LIVE'
            session.begin()
            session.add(match)
            session.add(server)
            await session.commit()
