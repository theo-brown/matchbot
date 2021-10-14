from fastapi import FastAPI
from matchbot.api import users as user_api
from matchbot.api import teams as team_api
from matchbot.api import matches as match_api
from matchbot.api import servers as server_api
from matchbot import database as db
from os import getenv
import uvicorn


app = FastAPI(title='MatchBot API')

engine = db.new_engine(host=getenv('POSTGRES_HOST'),
                       port=getenv('POSTGRES_PORT'),
                       user=getenv('POSTGRES_USER'),
                       password=getenv('POSTGRES_PASSWORD'),
                       db_name=getenv('POSTGRES_DB'))

user_api.engine = engine
app.include_router(user_api.router)

team_api.engine = engine
app.include_router(team_api.router)

match_api.engine = engine
app.include_router(match_api.router)

server_api.engine = engine
app.include_router(server_api.router)

if __name__ == '__main__':
    uvicorn.run("run:app", host="0.0.0.0", port=int(getenv('API_PORT')), reload=True)
