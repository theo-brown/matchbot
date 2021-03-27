from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from motor.motor_asyncio import AsyncIOMotorCollection as MongoCollection
from database import users

import aiosqlite
import aiofiles
import asyncio
from bson.json_util import loads,dumps

from sys import argv
from os import getenv
from dotenv import load_dotenv
load_dotenv("../.env")

mongo_users: MongoCollection

async def copy_steam_ids():
    print('batch updating')
    user_list = await mongo_users.find().to_list(length=None)
    users_with_steam_ids = []
    for user in user_list:
        if 'steam_id' in user.keys():
            users_with_steam_ids.append(user)
    await users.add_steam64_ids(users_with_steam_ids)
    print('done')

async def watch_mongo():
    try:
        async with aiofiles.open('resume', 'r') as tokenfile:
            resume_token = loads(await tokenfile.read())
    except FileNotFoundError:
        resume_token = None

    try:
        print('watching')
        async with mongo_users.watch({'$match': {'operationType': {'$in': ['insert', 'update', 'replace']}}},
                                     full_document='updateLookup',
                                     resume_after=resume_token) as stream:
            async for change in stream:
                print(change)
                entry = change['fullDocument']
                if 'steam_id' in entry:
                    await users.add_steam64_id(entry['discord_id'], entry['steam_id'])
                resume_token = stream.resume_token
    finally:
        print('exiting')
        assert resume_token  # only save if not None
        async with aiofiles.open('resume', 'w') as tokenfile:
            await tokenfile.write(dumps(resume_token))

async def run():
    global mongo_users
    mongo_users = MongoClient(getenv('MONGO_URI')).popskill.user_links
    users.db = await aiosqlite.connect("database.db", isolation_level=None)

    action = copy_steam_ids if 'update' in argv else watch_mongo
    await action()

if __name__ == '__main__':
    asyncio.run(run())
