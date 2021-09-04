from __future__ import annotations


class User:
    def __init__(self, steam_id, display_name, discord_id=None):
        self.steam_id = steam_id
        self.display_name = display_name
        self.discord_id = discord_id

    def __str__(self):
        return ("User:\n"
                f"\tSteam ID: {self.steam_id}\n"
                f"\tDiscord ID: {self.discord_id}\n"
                f"\tDisplay name: {self.display_name}")


def from_dict(user_dict: dict) -> User:
    return User(user_dict.get('steam_id'),
                user_dict.get('display_name'),
                user_dict.get('discord_id'))


class UsersTable:
    def __init__(self, pool: asyncpg.pool.Pool):
        self.pool = pool

    async def upsert(self, *users: User):
        async with self.pool.acquire() as connection:
            await connection.executemany("INSERT INTO users(steam_id, discord_id, display_name)"
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
        async with self.pool.acquire() as connection:
            users = [from_dict(record)
                     for record in await connection.fetch("SELECT steam_id, discord_id, display_name FROM users"
                                                          f" WHERE {column} = ANY ($1);", values)]
        if len(values) == 1:
            if len(users) == 1:
                return users[0]
            elif len(users) > 1:
                raise (LookupError(f"Multiple matching users found with {column}={values[0]}."))
            else:
                raise (LookupError(f"No matching user found with {column}={values[0]}."))
        else:
            return users
