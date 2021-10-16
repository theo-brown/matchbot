from __future__ import annotations
import aiodocker
from matchbot import database as db
from matchbot.apps import MatchbotBaseApp
from sqlalchemy import select
from uuid import UUID


class MatchStarter(MatchbotBaseApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, db_echo=False, **kwargs)
        self.docker = aiodocker.Docker()
        self.new_event_handler('match_queue', self.start_match)

    async def start_match(self, match_id: UUID):
        self.logger.debug(f"start_match('{str(match_id)}') triggered by EventHandler on 'match_queue'")
        async with self.new_session() as session:
            match = await session.get(db.models.Match, match_id)
            if not match:
                raise LookupError(f'No match found with id {match_id}')
            self.logger.debug(f"Match: {match.json}")
            r = await session.execute(select(db.models.Server).where(db.models.Server.match_id.is_(None)))
            server = r.scalars().first()
            if not server:
                raise LookupError('No available servers.')
            server.generate_passwords()
            match.set_as_live()
            server.match = match
            self.logger.debug(f"Server: {server.json}")
            container_config = {"Image": "theobrown/csgo-get5-docker:latest",
                                "Env": [f"SERVER_TOKEN={server.token}",
                                        f"PORT={server.port}",
                                        f"GOTV_PORT={server.gotv_port}",
                                        f"PASSWORD={server.password}",
                                        f"RCON_PASSWORD={server.rcon_password}",
                                        f"GOTV_PASSWORD={server.gotv_password}",
                                        f"MATCH_CONFIG={match.config}"],
                                "ExposedPorts": {f"{server.port}/tcp": {},
                                                 f"{server.port}/udp": {},
                                                 f"{server.gotv_port}/udp": {}},
                                "HostConfig": {"NetworkMode": "host"}}
            await self.docker.containers.run(config=container_config, name=str(server.id))
            self.logger.info(f"Started server {server.id} running match {match.id}")
            session.begin()
            self.logger.debug(f"Committing changes to the database")
            session.add(match)
            session.add(server)
            await session.commit()
            self.logger.info(f"Connect to server using '{server.connect_str}'")
