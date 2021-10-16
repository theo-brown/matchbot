import uuid
from typing import Union
from matchbot import api
from matchbot import database as db
from sqlalchemy import and_, select
import sqlalchemy
from fastapi import APIRouter, HTTPException
from uuid import UUID

engine: sqlalchemy.ext.asyncio.AsyncEngine

router = APIRouter(prefix='/teams',
                   tags=['teams'])


##########
# CREATE #
##########
@router.post('/')
async def create_team(team: api.models.CreateTeam):
    """
    Add a team to the database
    """
    async with db.new_session(engine) as session:
        team_id = team.id if team.id is not None else uuid.uuid4()
        db_team = db.models.Team(id=team_id,
                                 name=team.name,
                                 tag=team.tag)
        db_team_members = [db.models.TeamMembership(team_id=team_id, steam_id=steam_id) for steam_id in
                           team.user_ids]
        try:
            session.begin()
            session.add(db_team)
            session.add_all(db_team_members)
            await session.commit()
        except:
            await session.rollback()
            raise

        team_result = await session.execute(select(db.models.Team).where(db.models.Team.id==team.id))
        created_team = team_result.scalar()

    return created_team.json


@router.post('/id/{team_id}/members/')
async def add_member_to_team(team_id: UUID,
                             member: api.models.CreateMember):
    async with db.new_session(engine) as session:
        team_member = db.models.TeamMembership(team_id=team_id, steam_id=member.steam_id)
        try:
            session.begin()
            session.add(team_member)
            await session.commit()
        except:
            await session.rollback()
            raise
        team_result = await session.execute(select(db.models.Team).where(db.models.Team.id==team_id))
        team = team_result.scalars().first()
    return team.json


########
# READ #
########
async def get(column: str, value: Union[UUID, str]):
    if column == 'id':
        db_column = db.models.Team.id
    elif column == 'name':
        db_column = db.models.Team.name
    elif column == 'tag':
        db_column = db.models.Team.tag
    else:
        raise KeyError(f"Unrecognised column {column}, expected 'id', 'name' or 'tag'.")

    async with db.new_session(engine) as session:
        team_result = await session.execute(select(db.models.Team).where(db_column == value))
        teams = team_result.scalars().all()
        if not len(teams):
            raise HTTPException(status_code=404, detail="No matching team found")
        else:
            return [team.json for team in teams]


@router.get('/id/{id}')
async def get_team_by_id(id: UUID):
    return await get('id', id)


@router.get('/name/{name}')
async def get_team_by_name(name: str):
    return await get('name', name)


@router.get('/tag/{tag}')
async def get_team_by_tag(tag: str):
    return await get('tag', tag)


##########
# UPDATE #
##########
@router.put('/id/{id}')
async def update_team_metadata(id: UUID,
                               team: api.models.UpdateTeam):
    async with db.new_session(engine) as session:
        team_result = await session.execute(select(db.models.Team).where(db.models.Team.id==id))
        unmodified_team = team_result.scalars().first()
        modified_team = db.models.Team(id=id,
                                       name=team.name if team.name else unmodified_team.name,
                                       tag=team.tag if team.tag else unmodified_team.tag)
        try:
            session.begin()
            await session.merge(modified_team)
            await session.commit()
        except:
            await session.rollback()
            raise

        return True


@router.put('/id/{team_id}/members')
async def set_team_members(team_id: UUID,
                           members: api.models.UpdateMembers):
    async with db.new_session(engine) as session:
        team_membership_result = await session.execute(select(db.models.TeamMembership).where(db.models.TeamMembership.team_id==team_id))
        old_team_membership = team_membership_result.scalars().all()
        new_team_membership = [db.models.TeamMembership(team_id=team_id, steam_id=steam_id) for steam_id in members.steam_ids]
        try:
            session.begin()
            for member in old_team_membership:
                await session.delete(member)
            session.add_all(new_team_membership)
            await session.commit()
        except:
            await session.rollback()
            raise

        return True


##########
# DELETE #
##########
@router.delete('/id/{id}')
async def delete_team_by_id(id: UUID):
    async with db.new_session(engine) as session:
        team_result = await session.execute(select(db.models.Team).where(db.models.Team.id == id))
        team = team_result.scalars().first()
        if team is None:
            raise HTTPException(status_code=404, detail="No matching team found")
        else:
            try:
                session.begin()
                await session.delete(team)
                await session.commit()
            except:
                await session.rollback()
                raise
            return True


@router.delete('/id/{team_id}/members/{steam_id}')
async def delete_team_member_by_id(team_id: UUID,
                                   steam_id: int):
    async with db.new_session(engine) as session:
        team_membership_result = await session.execute(select(db.models.TeamMembership)
                                                       .where(and_(db.models.TeamMembership.team_id==team_id,
                                                                   db.models.TeamMembership.steam_id==steam_id)))
        team_member = team_membership_result.scalars().first()
        if team_member is None:
            raise HTTPException(status_code=404, detail="No matching team member found")
        else:
            try:
                session.begin()
                await session.delete(team_member)
                await session.commit()
            except:
                await session.rollback()
                raise
            return True
