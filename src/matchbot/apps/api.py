from typing import Optional
from fastapi import FastAPI
from matchbot import database as db
from sqlalchemy import select, and_
from os import getenv

app = FastAPI()
engine = db.new_engine(getenv('POSTGRES_HOST'),
                       getenv('POSTGRES_PORT'),
                       getenv('POSTGRES_USER'),
                       getenv('POSTGRES_PASSWORD'),
                       getenv('POSTGRES_DB'))



@app.get("/user")
async def get_user(steam_id: Optional[int] = None,
                   display_name: Optional[str] = None,
                   discord_id: Optional[int] = None):
    """
    Get the user that matches all of the supplied columns
    """
    async with db.new_session(engine) as session:
        condition = and_((db.models.User.steam_id == steam_id) if steam_id else True,
                         (db.models.User.display_name == display_name) if display_name else True,
                         (db.models.User.discord_id == discord_id) if discord_id else True)
        r = await session.execute(select(db.models.User).where(condition))
        user = r.scalars().first()
        if user is None:
            return None
        else:
            return user.json


@app.post("/user")
async def update_user(steam_id: int,
                      display_name: Optional[str] = None,
                      discord_id: Optional[int] = None):
    """
    Update the display_name and discord_id of the user with the matching steam_id
    """
    async with db.new_session(engine) as session:
        r = await session.execute(select(db.models.User).where(db.models.User.steam_id==steam_id))
        user = r.scalars().first()
        modified_user = db.models.User(steam_id=steam_id,
                                       display_name=display_name if display_name else user.display_name,
                                       discord_id=discord_id if discord_id else user.discord_id)
        try:
            session.begin()
            await session.merge(modified_user)
            await session.commit()
        except:
            await session.rollback()
            raise

        return True


@app.delete("/user")
async def delete_user(steam_id: Optional[int] = None,
                      display_name: Optional[str] = None,
                      discord_id: Optional[int] = None):
    """
    Delete a user that matches all of the supplied columns
    """
    async with db.new_session(engine) as session:
        condition = and_((db.models.User.steam_id == steam_id) if steam_id else True,
                         (db.models.User.display_name == display_name) if display_name else True,
                         (db.models.User.discord_id == discord_id) if discord_id else True)
        r = await session.execute(select(db.models.User).where(condition))
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


if __name__=='__main__':
    import uvicorn
    uvicorn.run("api:app", port=9000, reload=True)