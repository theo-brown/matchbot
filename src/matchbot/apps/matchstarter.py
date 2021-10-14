from __future__ import annotations
import aiodocker
from matchbot import timestamp
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
        print(f"{timestamp()} MatchStarter.start_match({match_id})")
        async with self.new_session() as session:
            match = await session.get(db.models.Match, match_id)
            print(f"{timestamp()} Retrieved Match object: {match.json}")
            r = await session.execute(select(db.models.Server).where(db.models.Server.match_id.is_(None)))
            server = r.scalars().first()
            if not server:
                raise LookupError('No available servers.')
            server.generate_passwords()
            match.set_as_live()
            server.match = match
            print(f"{timestamp()} Assigned Server object: {server.json}")
            container_config = {"Image": "theobrown/csgo-docker:latest",
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
            await self.docker.containers.run(config=container_config, name=server.id)
            print(f"{timestamp()} Server started with config: {match.config}")
            session.begin()
            print(f"{timestamp()} Committing changes to the database")
            session.add(match)
            session.add(server)
            await session.commit()
            print(f"{timestamp()} Done.")
            print(f"{timestamp()} Connect to server: {server.connect_str}")
