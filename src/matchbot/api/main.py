from fastapi import FastAPI
from matchbot.api import users as user_api
from matchbot.api import teams as team_api
from matchbot import database as db
from os import getenv


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=7000, reload=True)
