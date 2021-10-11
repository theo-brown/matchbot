import sqlalchemy
from fastapi import APIRouter, HTTPException
import matchbot.database as db
from matchbot import api
from uuid import UUID
from sqlalchemy import select, or_

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
        created_match = await session.get(db.models.Match, match.id)
    return created_match.json


@router.post('/id/{match_id}/map/')
async def add_map_to_match(match_id: UUID,
                           map: api.models.CreateMatchMap):
    async with db.new_session(engine) as session:
        map = db.models.MatchMap(match_id=match_id,
                                 number=map.number,
                                 id=map.id,
                                 side=map.side)
        try:
            session.begin()
            session.add(map)
            await session.commit()
        except:
            await session.rollback()
            raise
        created_match = await session.get(db.models.Match, match.id)
    return created_match.json


########
# READ #
########
@router.get('/id/{match_id}')
async def get_match_by_id(match_id: UUID):
    async with db.new_session(engine) as session:
        match = await session.get(db.models.Match, match_id)
        if match is None:
            raise HTTPException(status_code=404, detail="No matching match found")
        else:
            return match.json


@router.get('/team-id/{team_id}')
async def get_matches_by_team_id(team_id: UUID):
    async with db.new_session(engine) as session:
        r = await session.execute(select(db.models.Match).where(or_(db.models.Match.team1_id==team_id,
                                                                    db.models.Match.team2_id==team_id)))
        matches = r.scalars().all()
        if not len(matches):
            raise HTTPException(status_code=404, detail="No matching match found")
        else:
            return [match.json for match in matches]


@router.get('/status/{status}')
async def get_matches_by_status(status: api.models.MatchStatus):
    async with db.new_session(engine) as session:
        r = await session.execute(select(db.models.Match).where(db.models.Match.status==status))
        matches = r.scalars().all()
        if not len(matches):
            raise HTTPException(status_code=404, detail="No matching match found")
        else:
            return [match.json for match in matches]


@router.get('/map/{map_id}')
async def get_matches_by_map_id(map_id: str):
    async with db.new_session(engine) as session:
        r = await session.execute(select(db.models.Match)
                                  .where(db.models.Match.id.in_(select(db.models.MatchMap.match_id)
                                                                .where(db.models.MatchMap.id==map_id))))
        matches = r.scalars().all()
        if not len(matches):
            raise HTTPException(status_code=404, detail="No matching match found")
        else:
            return [match.json for match in matches]


##########
# UPDATE #
##########
@router.put('/id/{match_id}')
async def update_match_metadata(match_id: UUID,
                                match: api.models.UpdateMatch):
    async with db.new_session(engine) as session:
        unmodified_match = await session.get(db.models.Match, match_id)
        modified_match = db.models.Match(id=match_id,
                                         status=match.status if match.status else unmodified_match.status,
                                         team1_id=match.team1_id if match.team1_id else unmodified_match.team1_id,
                                         team2_id=match.team2_id if match.team2_id else unmodified_match.team2_id,
                                         created_timestamp=match.created_timestamp
                                                           if match.created_timestamp
                                                           else unmodified_match.created_timestamp,
                                         live_timestamp=match.live_timestamp
                                                        if match.live_timestamp
                                                        else unmodified_match.live_timestamp,
                                         finished_timestamp=match.finished_timestamp
                                                            if match.finished_timestamp
                                                            else unmodified_match.finished_timestamp)
        try:
            session.begin()
            await session.merge(modified_match)
            await session.commit()
        except:
            await session.rollback()
            raise

        return True


@router.put('/id/{match_id}/map_number/{map_number}')
async def update_match_map(match_id: UUID,
                           map_number: int,
                           map: api.models.UpdateMatchMap):
    async with db.new_session(engine) as session:
        unmodified_matchmap = await session.get(db.models.MatchMap, (match_id, map_number))
        modified_matchmap = db.models.MatchMap(match_id=match_id,
                                               number=map_number,
                                               id=map.id if map.id else unmodified_matchmap.id,
                                               side=map.side if map.side else unmodified_matchmap.side)
        try:
            session.begin()
            await session.merge(modified_matchmap)
            await session.commit()
        except:
            await session.rollback()
            raise

        return True


##########
# DELETE #
##########
@router.delete('/id/{match_id}')
async def delete_match_by_id(match_id: UUID):
    async with db.new_session(engine) as session:
        match = await session.get(db.models.Match, match_id)
        if match is None:
            raise HTTPException(status_code=404, detail="No matching match found")
        else:
            try:
                session.begin()
                await session.delete(match)
                for map in match.maps:
                    await session.delete(map)
                await session.commit()
            except:
                await session.rollback()
                raise
            return True


@router.delete('/id/{match_id}/map/{map_id}')
async def delete_match_map_by_id(match_id: UUID,
                                 map_id: str):
    async with db.new_session(engine) as session:
        match = await session.get(db.models.Match, match_id)
        map_result = await session.execute(select(db.models.MatchMap).where(and_(db.models.MatchMap.id==map_id,
                                                                                 db.models.MatchMap.match_id==match_id)))
        maps = map_result.scalars().all()
        if not len(maps):
            raise HTTPException(status_code=404, detail="No matching map found")
        else:
            try:
                session.begin()
                for map in maps:
                    await session.delete(map)
                await session.commit()
            except:
                await session.rollback()
                raise
            return True


@router.delete('/id/{match_id}/map_number/{map_number}')
async def delete_match_map_by_map_number(match_id: UUID,
                                         map_number: int):
    async with db.new_session(engine) as session:
        map = await session.get(db.models.MatchMap, (match_id, map_number))
        if map is None:
            raise HTTPException(status_code=404, detail="No matching map found")
        else:
            try:
                session.begin()
                await session.delete(map)
                await session.commit()
            except:
                await session.rollback()
                raise
            return True
