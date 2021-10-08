from __future__ import annotations
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, DateTime, select
from sqlalchemy.dialects.postgresql import INET as POSTGRES_INET
from sqlalchemy.dialects.postgresql import ENUM as POSTGRES_ENUM
from sqlalchemy.dialects.postgresql import UUID as POSTGRES_UUID
from sqlalchemy.orm import declarative_base, relationship
from typing import Optional
from uuid import UUID

Base = declarative_base()

MapSide = POSTGRES_ENUM('team1_ct', 'team2_ct', 'team1_t', 'team2_t', 'knife', name='map_side')
MatchStatus = POSTGRES_ENUM('CREATED', 'QUEUED', 'LIVE', 'FINISHED', name='match_status')


class Map(Base):
    __tablename__ = 'maps'

    id = Column(String(32), primary_key=True)
    name = Column(String(32))

    @property
    def json(self):
        return {'id': self.id,
                'name': self.name}


class MatchMap(Base):
    __tablename__ = 'match_maps'

    match_id = Column(POSTGRES_UUID(as_uuid=True), ForeignKey('matches.id'), primary_key=True)
    map_number = Column(Integer, primary_key=True)
    map_id = Column(String(32), ForeignKey('maps.id'))
    side = Column(MapSide)


class Match(Base):
    __tablename__ = 'matches'

    id = Column(POSTGRES_UUID(as_uuid=True), primary_key=True)
    status = Column(MatchStatus)
    created_timestamp = Column(DateTime, nullable=True)
    live_timestamp = Column(DateTime, nullable=True)
    finished_timestamp = Column(DateTime, nullable=True)
    team1_id = Column(POSTGRES_UUID(as_uuid=True), ForeignKey('teams.id'))
    team2_id = Column(POSTGRES_UUID(as_uuid=True), ForeignKey('teams.id'))


class ServerToken(Base):
    __tablename__ = 'server_tokens'

    token = Column(String(32), primary_key=True)


class Server(Base):
    __tablename__ = 'servers'

    id = Column(POSTGRES_UUID(as_uuid=True), primary_key=True)
    token = Column(String(32), ForeignKey('server_tokens.token'))
    ip = Column(POSTGRES_INET)
    port = Column(Integer)
    gotv_port = Column(Integer)
    password = Column(String(32), nullable=True)
    gotv_password = Column(String(32), nullable=True)
    rcon_password = Column(String(32), nullable=True)
    match_id = Column(POSTGRES_UUID(as_uuid=True), ForeignKey('matches.id'))


class TeamMembership(Base):
    __tablename__ = 'team_members'

    team_id = Column(POSTGRES_UUID(as_uuid=True), ForeignKey('teams.id'), primary_key=True)
    steam_id = Column(BigInteger, ForeignKey('users.steam_id'), primary_key=True)

    def __init__(self, team_id, steam_id):
        self.team_id = team_id
        self.steam_id = steam_id


class Team(Base):
    __tablename__ = 'teams'

    id = Column(POSTGRES_UUID(as_uuid=True), primary_key=True)
    name = Column(String(64))
    tag = Column(String(15), nullable=True)

    users = relationship('User', secondary='team_members', back_populates='teams', lazy='selectin')

    def __init__(self, id: UUID, name: str, tag: str):
        self.id = id
        self.name = name
        self.tag = tag

    @property
    def json(self):
        return {'id': self.id,
                'name': self.name,
                'tag': self.tag}


class User(Base):
    __tablename__ = 'users'

    steam_id = Column(BigInteger, primary_key=True)
    discord_id = Column(BigInteger, nullable=True)
    display_name = Column(String(64))

    teams = relationship('Team', secondary='team_members', back_populates='users', lazy='selectin')

    def __init__(self, steam_id: int, display_name: str, discord_id: Optional[int] = None):
        self.steam_id = steam_id
        self.display_name = display_name
        self.discord_id = discord_id

    @property
    def json(self):
        return {'steam_id': self.steam_id,
                'display_name': self.display_name,
                'discord_id': self.discord_id}


if __name__ == '__main__':
    from os import getenv
    from dotenv import load_dotenv
    import asyncio
    from matchbot.database import new_session, new_engine

    load_dotenv('../../.env')
    engine = new_engine('localhost', getenv('POSTGRES_PORT'), getenv('POSTGRES_USER'), getenv('POSTGRES_PASSWORD'),
                        getenv('POSTGRES_DB'))
    session = new_session(engine)
