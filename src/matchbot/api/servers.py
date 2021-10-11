import sqlalchemy
from fastapi import APIRouter, HTTPException
from matchbot import api
from matchbot import database as db
from uuid import UUID
from sqlalchemy import select
from typing import Union

engine: sqlalchemy.ext.asyncio.AsyncEngine

router = APIRouter(prefix='/servers',
                   tags=['servers'])


##########
# CREATE #
##########
@router.post('/')
async def create_server(server: api.models.CreateServer):
    server = db.models.Server(id=server.id,
                              token=server.token,
                              ip=server.ip,
                              port=server.port,
                              gotv_port=server.gotv_port,
                              password=server.password,
                              gotv_password=server.gotv_password,
                              rcon_password=server.rcon_password,
                              match_id=server.match_id)
    async with db.new_session(engine) as session:
        try:
            session.begin()
            session.add(server)
            await session.commit()
        except:
            await session.rollback()
            raise
    return server.json


@router.post('/tokens/')
async def add_server_token(token: str):
    async with db.new_session(engine) as session:
        token = db.models.ServerToken(token=token)
        try:
            session.begin()
            session.add(token)
            await session.commit()
        except:
            await session.rollback()
            raise
    return token


########
# READ #
########
@router.get('/id/{server_id}')
async def get_server_by_id(server_id: UUID):
    async with db.new_session(engine) as session:
        server = await session.get(db.models.Server, server_id)
        if server is None:
            raise HTTPException(status_code=404, detail="No matching server found")
        else:
            return server.json


async def get_server_by_column(column: str, value: Union[str, UUID, int]):
    if column == 'token':
        column = db.models.Server.token
    elif column == 'port':
        column = db.models.Server.port
    elif column == 'gotv_port':
        column = db.models.server.gotv_port
    elif column == 'match_id':
        column = db.models.server.match_id
    else:
        raise KeyError(f"Unrecognised column {column}, expected 'token', 'port', 'gotv_port' or 'match_id'.")

    async with db.new_session(engine) as session:
        r = await session.execute(select(db.models.Server).where(column==value))
        server = r.scalar()
        if server is None:
            raise HTTPException(status_code=404, detail="No matching server found")
        else:
            return server.json


@router.get('/token/{token}')
async def get_server_by_token(token: str):
    return await get_server_by_column('token', token)


@router.get('/port/{port}')
async def get_server_by_port(port: int):
    return await get_server_by_column('port', port)


@router.get('/gotv_port/{gotv_port}')
async def get_server_by_gotv_port(gotv_port: int):
    return await get_server_by_column('gotv_port', gotv_port)


@router.get('/match_id/{match_id}')
async def get_server_by_match_id(match_id: UUID):
    return await get_server_by_column('match_id', match_id)


##########
# UPDATE #
##########
@router.put('/id/{server_id}')
async def update_server(server_id: UUID,
                        server: api.models.UpdateServer):
    async with db.new_session(engine) as session:
        unmodified_server = await session.get(db.models.Server, server_id)
        modified_server = db.models.Server(id=server_id,
                                           token=server.token if server.token else unmodified_server.token,
                                           ip=server.ip if server.ip else unmodified_server.ip,
                                           port=server.port if server.port else unmodified_server.port,
                                           gotv_port=server.gotv_port if server.gotv_port else unmodified_server.gotv_port,
                                           password=server.password if server.password else unmodified_server.password,
                                           gotv_password=server.gotv_password if server.gotv_password else unmodified_server.gotv_password,
                                           rcon_password=server.rcon_password if server.rcon_password else unmodified_server.rcon_password,
                                           match_id=server.match_id if server.match_id else unmodified_server.match_id)
        try:
            session.begin()
            await session.merge(modified_server)
            await session.commit()
        except:
            await session.rollback()
            raise

        return True


##########
# DELETE #
##########
@router.delete('/id/{server_id}')
async def delete_server_by_id(server_id: UUID):
    async with db.new_session(engine) as session:
        server = await session.get(db.models.Server, server_id)
        if server is None:
            raise HTTPException(status_code=404, detail="No matching server found")
        else:
            try:
                session.begin()
                await session.delete(server)
                await session.commit()
            except:
                await session.rollback()
                raise
            return True


@router.delete('/token/{token}')
async def delete_server_token(token: str):
    async with db.new_session(engine) as session:
        token = await session.get(db.models.ServerToken, token)
        if token is None:
            raise HTTPException(status_code=404, detail="No matching server token found")
        else:
            try:
                session.begin()
                await session.delete(token)
                await session.commit()
            except:
                await session.rollback()
                raise
            return True
