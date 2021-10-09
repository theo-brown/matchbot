import sqlalchemy
from fastapi import APIRouter, HTTPException
from matchbot import api
from matchbot import database as db


engine: sqlalchemy.ext.asyncio.AsyncEngine

router = APIRouter(prefix='/servers',
                   tags=['servers'])
