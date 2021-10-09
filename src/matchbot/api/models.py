from pydantic import BaseModel, IPvAnyAddress
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class CreateUser(BaseModel):
    steam_id: int
    display_name: str
    discord_id: Optional[int] = None


class UpdateUser(BaseModel):
    display_name: Optional[str] = None
    discord_id: Optional[int] = None


# Team classes
class CreateTeam(BaseModel):
    id: UUID
    name: str
    tag: str
    user_ids: Optional[List[int]] = None


class UpdateTeam(BaseModel):
    name: Optional[str] = None
    tag: Optional[str] = None


# Team member classes
class CreateMember(BaseModel):
    steam_id: int


class UpdateMembers(BaseModel):
    steam_ids: List[int]


# Match classes
class MatchStatus(str, Enum):
    created = 'CREATED'
    queued = 'QUEUED'
    live = 'LIVE'
    finished = 'FINISHED'


class CreateMatch(BaseModel):
    id: UUID
    status: Optional[MatchStatus] = 'CREATED'
    created_timestamp: Optional[datetime] = datetime.now()
    live_timestamp: Optional[datetime] = None
    finished_timestamp: Optional[datetime] = None
    team1_id: UUID
    team2_id: UUID


# Server classes
class CreateServer(BaseModel):
    id: UUID
    token: str
    ip: IPvAnyAddress
    port: int
    gotv_port: int
    password: Optional[str] = None
    gotv_password: Optional[str] = None
    rcon_password: Optional[str] = None
    match_id: Optional[UUID] = None
