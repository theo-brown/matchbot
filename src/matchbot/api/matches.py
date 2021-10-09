import sqlalchemy
from fastapi import APIRouter, HTTPException
import matchbot.database as db
from matchbot import api
from uuid import UUID
from sqlalchemy import select

engine: sqlalchemy.ext.asyncio.AsyncEngine

router = APIRouter(prefix='/matches',
                   tags=['matches'])


##########
# CREATE #
##########
@router.post('/')
async def create_match(match: api.models.CreateMatch):
    """
    Add a match to the database
    """
    match = db.models.Match(id=match.id,
                            status=match.status,
                            created_timestamp=match.created_timestamp,
                            live_timestamp=match.live_timestamp,
                            finished_timestamp=match.finished_timestamp,
                            team1_id=match.team1_id,
                            team2_id=match.team2_id)
    async with db.new_session(engine) as session:
        try:
            session.begin()
            session.add(match)
            await session.commit()
        except:
            await session.rollback()
            raise
        result = await session.execute(select(db.models.Match).where(db.models.Match.id==match.id))
        created_match = result.scalar()
    return created_match.json


########
# READ #
########
@router.get('/id/{id}')
async def get_match_by_id(id: UUID):
    async with db.new_session(engine) as session:
        r = await session.execute(select(db.models.Match).where(db.models.Match.id==id))
        match = r.scalar()
        if match is None:
            raise HTTPException(status_code=404, detail="No matching match found")
        else:
            return match.json

