from __future__ import annotations
from typing import Iterable, Union
from matchbot import User


class UsersTable:
    def __init__(self, dbi: DatabaseInterface):
        self.dbi = dbi

    async def add(self, *users: User):
        await self.dbi.db.executemany("INSERT INTO users(steam_id, discord_id, display_name)"
                                      " VALUES ($1, $2, $3)"
                                      " ON CONFLICT (steam_id) DO UPDATE"
                                      " SET discord_id = excluded.discord_id,"
                                          " display_name = excluded.display_name;",
                                      [(user.steam_id, user.discord_id, user.display_name)
                                       for user in users])

    async def get(self, column: str, *values: Union[int, str]) -> Union[User, Iterable[User]]:
        if column not in ['steam_id', 'discord_id', 'display_name']:
            raise ValueError(f"Column {column} not found in table"
                             " (expected 'steam_id', 'discord_id' or 'display_name').")
        users = [User(steam_id=record.get('steam_id'),
                      discord_id=record.get('discord_id'),
                      display_name=record.get('display_name'))
                 for record in await self.dbi.db.fetch("SELECT steam_id, discord_id, display_name FROM users"
                                                       f" WHERE {column} = ANY ($1);", values)]
        if len(values) == 1:
            if len(users) == 1:
                return users[0]
            elif len(users) > 1:
                raise(LookupError(f"Multiple matching users found with {column}={values[0]}."))
            else:
                raise(LookupError(f"No matching user found with {column}={values[0]}."))
        else:
            return users

    async def get_by_steam_id(self, *steam_ids: int) -> Union[User, Iterable[User]]:
        return await self.get('steam_id', *steam_ids)

    async def get_by_discord_id(self, *discord_ids: int) -> Union[User, Iterable[User]]:
        return await self.get('discord_id', *discord_ids)

    async def get_by_display_name(self, *display_names: str) -> Union[User, Iterable[User]]:
        return await self.get('display_name', *display_names)
