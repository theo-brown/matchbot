from os import getenv
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from motor.motor_asyncio import AsyncIOMotorCollection as MongoCollection
from database import users


async def copy_steam_ids():
    mongo_client = MongoClient(getenv('MONGO_URI'))
    mongo_users: MongoCollection = mongo_client.popskill.user_links
    user_list = await mongo_users.find().to_list(length=None)
    users_with_steam_ids = []
    for user in user_list:
        if 'steam_id' in user.keys():
            users_with_steam_ids.append(user)
    await users.add_steam64_ids(users_with_steam_ids)


if __name__ == '__main__':
    import asyncio
    import aiosqlite
    from dotenv import load_dotenv
    load_dotenv("../.env")

    async def run():
        users.db = await aiosqlite.connect("database.db", isolation_level=None)
        await copy_steam_ids()

    asyncio.run(run())
