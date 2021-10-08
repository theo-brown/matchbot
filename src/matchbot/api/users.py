from typing import Optional, Union
from matchbot import api
from matchbot import database as db
from sqlalchemy import select
import sqlalchemy
from fastapi import APIRouter, HTTPException


engine: sqlalchemy.ext.asyncio.AsyncEngine

router = APIRouter(prefix='/users',
                   tags=['users'],)

##########
# CREATE #
##########
@router.post('/')
async def create_user(user: api.models.CreateUser):
    """
    Add a user to the database
    """
    user = db.models.User(steam_id=user.steam_id,
                          discord_id=user.discord_id,
                          display_name=user.display_name)
    async with db.new_session(engine) as session:
        try:
            session.begin()
            session.add(user)
            await session.commit()
        except:
            await session.rollback()
            raise
    return user.json


########
# READ #
########
async def get(column: str, value: Union[str, int]):
    if column == 'steam_id':
        db_column = db.models.User.steam_id
    elif column == 'discord_id':
        db_column = db.models.User.discord_id
    elif column == 'display_name':
        db_column = db.models.User.display_name
    else:
        raise KeyError(f"Unrecognised column {column}, expected 'steam_id', 'discord_id' or 'display_name'.")

    async with db.new_session(engine) as session:
        r = await session.execute(select(db.models.User).where(db_column == value))
        user = r.scalars().first()
        if user is None:
            raise HTTPException(status_code=404, detail="No matching user found")
        else:
            return user.json

@router.get('/steam_id/{steam_id}')
async def get_user_by_steam_id(steam_id: int):
    return await get('steam_id', steam_id)

@router.get('/discord_id/{discord_id}')
async def get_user_by_discord_id(discord_id: int):
    return await get('discord_id', discord_id)

@router.get('/display_name/{display_name}')
async def get_user_by_display_name(display_name: str):
    return await get('display_name', display_name)


##########
# UPDATE #
##########
@router.put('/steam_id/{steam_id}')
async def update_user(steam_id: int,
                      user: api.models.UpdateUser):
    """
    Update the display_name and discord_id of the user with the matching steam_id
    """
    async with db.new_session(engine) as session:
        r = await session.execute(select(db.models.User).where(db.models.User.steam_id==steam_id))
        unmodified_user = r.scalars().first()
        modified_user = db.models.User(steam_id=steam_id,
                                       display_name=user.display_name if user.display_name else unmodified_user.display_name,
                                       discord_id=user.discord_id if user.discord_id else unmodified_user.discord_id)
        try:
            session.begin()
            await session.merge(modified_user)
            await session.commit()
        except:
            await session.rollback()
            raise

        return True


##########
# DELETE #
##########
async def delete(column: str, value: Union[str, int]):
    if column == 'steam_id':
        db_column = db.models.User.steam_id
    elif column == 'discord_id':
        db_column = db.models.User.discord_id
    elif column == 'display_name':
        db_column = db.models.User.display_name
    else:
        raise KeyError(f"Unrecognised column {column}, expected 'steam_id', 'discord_id' or 'display_name'.")

    async with db.new_session(engine) as session:
        r = await session.execute(select(db.models.User).where(db_column==value))
        user = r.scalars().first()
        if user is not None:
            try:
                session.begin()
                await session.delete(user)
                await session.commit()
            except:
                await session.rollback()
                raise
        return True

@router.delete('/steam_id/{steam_id}')
async def delete_user_by_steam_id(steam_id: int):
    return await delete('steam_id', steam_id)

@router.delete('/discord_id/{discord_id}')
async def delete_user_by_discord_id(discord_id: int):
    return await delete('discord_id', discord_id)

@router.delete('/display_name/{display_name}')
async def delete_user_by_display_name(display_name: int):
    return await delete('display_name', display_name)
