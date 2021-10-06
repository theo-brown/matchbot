from pydantic import BaseModel
from typing import Optional, List


class User(BaseModel):
    steam_id: int
    discord_id: Optional[int] = None
    display_name: str
