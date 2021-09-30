from __future__ import annotations
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, INET, ENUM
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine


Base = declarative_base()

MapSide = ENUM('team1_ct', 'team2_ct', 'team1_t', 'team2_t', 'knife', name='map_side')
MatchStatus = ENUM('CREATED', 'QUEUED', 'LIVE', 'FINISHED', name='match_status')


def new_engine(host: str, port: int, user: str, password: str, db_name: str) -> AsyncEngine:
    return create_async_engine(f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}',
                               echo=True,  future=True)


def new_session(engine: AsyncEngine) -> AsyncSession:
    return AsyncSession(engine, expire_on_commit=False)


class Map(Base):
    __tablename__ = 'maps'

    id = Column(String(32), primary_key=True)
    name = Column(String(32))


class MatchMap(Base):
    __tablename__ = 'match_maps'

    match_id = Column(UUID(as_uuid=True), ForeignKey('matches.id'), primary_key=True)
    map_number = Column(Integer, primary_key=True)
    map_id = Column(String(32), ForeignKey('maps.id'))
    side = Column(MapSide)

    match = relationship('Match', back_populates='maps')


class Match(Base):
    __tablename__ = 'matches'

    id = Column(UUID(as_uuid=True), primary_key=True)
    status = Column(MatchStatus)
    created_timestamp = Column(DateTime, nullable=True)
    live_timestamp = Column(DateTime, nullable=True)
    finished_timestamp = Column(DateTime, nullable=True)
    team1_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'))
    team2_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'))

    server = relationship('Server', back_populates='match')
    maps = relationship('MatchMap', back_populates='match')


class ServerToken(Base):
    __tablename__ = 'server_tokens'

    token = Column(String(32), primary_key=True)


class Server(Base):
    __tablename__ = 'servers'

    id = Column(UUID(as_uuid=True), primary_key=True)
    token = Column(String(32), ForeignKey('server_tokens.token'))
    ip = Column(INET)
    port = Column(Integer)
    gotv_port = Column(Integer)
    password = Column(String(32), nullable=True)
    gotv_password = Column(String(32), nullable=True)
    rcon_password = Column(String(32), nullable=True)
    match_id = Column(UUID(as_uuid=True), ForeignKey('matches.id'))

    match = relationship('Match', back_populates='server')


class TeamMembership(Base):
    __tablename__ = 'team_members'

    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), primary_key=True)
    steam_id = Column(BigInteger, ForeignKey('users.steam_id'), primary_key=True)

    team = relationship('Team', back_populates='_membership')
    user = relationship('User', back_populates='_membership')

    def __init__(self, team: Team, user: User):
        self.team_id = team.id
        self.steam_id = user.steam_id
        self.team = team
        self.user = user


class Team(Base):
    __tablename__ = 'teams'

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(64))
    tag = Column(String(15), nullable=True)

    _membership = relationship('TeamMembership', back_populates='team')

    users = association_proxy('_membership', 'user')


class User(Base):
    __tablename__ = 'users'

    steam_id = Column(BigInteger, primary_key=True)
    discord_id = Column(BigInteger, nullable=True)
    display_name = Column(String(64))

    _membership = relationship('TeamMembership', back_populates='user')
    teams = association_proxy('_membership', 'team')
    