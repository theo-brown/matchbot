from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class CreateUser(BaseModel):
    steam_id: int
    display_name: str
    discord_id: Optional[int] = None


class UpdateUser(BaseModel):
    display_name: Optional[str] = None
    discord_id: Optional[int] = None


class CreateTeam(BaseModel):
    id: UUID
    name: str
    tag: str
    user_ids: List[int]


class UpdateTeam(BaseModel):
    name: Optional[str] = None
    tag: Optional[str] = None