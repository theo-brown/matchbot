from __future__ import annotations
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, DateTime, Table
from sqlalchemy.dialects.postgresql import INET as POSTGRES_INET
from sqlalchemy.dialects.postgresql import ENUM as POSTGRES_ENUM
from sqlalchemy.dialects.postgresql import UUID as POSTGRES_UUID
from sqlalchemy.orm import declarative_base, relationship
from typing import Optional
from uuid import UUID
from datetime import datetime
from secrets import token_urlsafe
import json


Base = declarative_base()

MapSide = POSTGRES_ENUM('team1_ct', 'team2_ct', 'team1_t', 'team2_t', 'knife', name='map_side')
MatchStatus = POSTGRES_ENUM('CREATED', 'QUEUED', 'LIVE', 'FINISHED', name='match_status')


class Map(Base):
    __tablename__ = 'maps'

    id = Column(String(32), primary_key=True)
    name = Column(String(32))

    @property
    def json(self):
        return json.dumps({'id': str(self.id),
                           'name': self.name})


class MatchMap(Base):
    __tablename__ = 'match_maps'

    match_id = Column(POSTGRES_UUID(as_uuid=True), ForeignKey('matches.id'), primary_key=True)
    number = Column(Integer, primary_key=True)
    id = Column(String(32), ForeignKey('maps.id'))
    side = Column(MapSide)

    map = relationship('Map', lazy='selectin')

    @property
    def name(self):
        return self.map.name


class Match(Base):
    __tablename__ = 'matches'

    id = Column(POSTGRES_UUID(as_uuid=True), primary_key=True)
    status = Column(MatchStatus)
    created_timestamp = Column(DateTime, nullable=True)
    live_timestamp = Column(DateTime, nullable=True)
    finished_timestamp = Column(DateTime, nullable=True)
    team1_id = Column(POSTGRES_UUID(as_uuid=True), ForeignKey('teams.id'))
    team2_id = Column(POSTGRES_UUID(as_uuid=True), ForeignKey('teams.id'))

    team1 = relationship('Team', lazy='selectin', foreign_keys=[team1_id], uselist=False)
    team2 = relationship('Team', lazy='selectin', foreign_keys=[team2_id], uselist=False)
    maps = relationship('MatchMap', lazy='selectin')
    server = relationship('Server', back_populates='match', lazy='selectin', uselist=False)

    def __init__(self, id: UUID, status: MatchStatus, team1_id: UUID, team2_id: UUID,
                 created_timestamp: datetime,
                 live_timestamp: Optional[datetime] = None,
                 finished_timestamp: Optional[datetime] = None):
        self.id = id
        self.status = status
        self.created_timestamp = created_timestamp
        self.live_timestamp = live_timestamp
        self.finished_timestamp = finished_timestamp
        self.team1_id = team1_id
        self.team2_id = team2_id

    @property
    def json(self):
        return json.dumps({'id': str(self.id),
                           'status': self.status,
                           'created_timestamp': str(self.created_timestamp),
                           'live_timestamp': str(self.live_timestamp),
                           'finished_timestamp': str(self.finished_timestamp),
                           'maps': [m.id for m in self.ordered_maps],
                           'sides': [m.side for m in self.ordered_maps],
                           'team1': self.team1.json,
                           'team2': self.team2.json})

    @property
    def ordered_maps(self):
        # TODO: Check that this doesn't throw an error when it has no maps
        if self.maps:
            return sorted(self.maps, key=lambda m: m.number)
        else:
            return []

    @property
    def config(self):
        # TODO: Check that this doesn't throw an error when it has no maps
        players_per_team = max(len(self.team1.users), len(self.team2.users))
        return json.dumps({'matchid': str(self.id),
                           'num_maps': len(self.maps),
                           'maplist': [m.id for m in self.ordered_maps],
                           'skip_veto': True,
                           'map_sides': [m.side for m in self.ordered_maps],
                           'players_per_team': players_per_team,
                           'team1': {'name': self.team1.name,
                                     'tag': self.team1.tag,
                                     'players': {user.steam_id: user.display_name for user in self.team1.users}},
                           'team2': {'name': self.team2.name,
                                     'tag': self.team2.tag,
                                     'players': {user.steam_id: user.display_name for user in self.team2.users}},
                           'cvars': {"get5_warmup_cfg": "warmup_2v2.cfg" if players_per_team == 2 else "warmup_5v5.cfg",
                                     "get5_live_cfg": "live_2v2.cfg" if players_per_team == 2 else "live_5v5.cfg"}})

    def set_as_live(self):
        self.status = 'LIVE'
        self.live_timestamp = datetime.utcnow()

    def set_as_finished(self):
        self.status = 'FINISHED'
        self.finished_timestamp = datetime.utcnow()


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

    match = relationship('Match', back_populates='server', lazy='selectin')

    @property
    def json(self):
        return json.dumps({"id": str(self.id),
                           "token": self.token,
                           "ip": str(self.ip),
                           "port": self.port,
                           "gotv_port": self.gotv_port,
                           "password": self.password,
                           "rcon_password": self.rcon_password,
                           "match": self.match.json if self.match_id else None})

    def generate_passwords(self):
        self.password = token_urlsafe(16)
        self.gotv_password = token_urlsafe(16)
        self.rcon_password = token_urlsafe(16)

    @property
    def connect_str(self):
        return f"connect {self.ip}:{self.port}; password {self.password}"


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

    # matches = relationship('Match', lazy='selectin',
    #                        primaryjoin='or_(Team.id==Match.team1_id, Team.id==Match.team2_id)')

    def __init__(self, id: UUID, name: str, tag: str):
        self.id = id
        self.name = name
        self.tag = tag

    @property
    def json(self):
        return json.dumps({'id': str(self.id),
                           'name': self.name,
                           'tag': self.tag,
                           'members': [user.json for user in self.users]})


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
        return json.dumps({'steam_id': self.steam_id,
                           'display_name': self.display_name,
                           'discord_id': self.discord_id})


if __name__ == '__main__':
    from os import getenv
    from dotenv import load_dotenv
    import asyncio
    from matchbot.database import new_session, new_engine
    from sqlalchemy import select

    load_dotenv('../../.env')
    engine = new_engine('localhost', getenv('POSTGRES_PORT'), getenv('POSTGRES_USER'), getenv('POSTGRES_PASSWORD'),
                        getenv('POSTGRES_DB'))
    session = new_session(engine)
