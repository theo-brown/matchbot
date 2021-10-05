from fastapi import FastAPI
from matchbot.api import user as user_api
from matchbot import database as db
from os import getenv


app = FastAPI()

engine = db.new_engine(host=getenv('POSTGRES_HOST'),
                       port=getenv('POSTGRES_PORT'),
                       user=getenv('POSTGRES_USER'),
                       password=getenv('POSTGRES_PASSWORD'),
                       db_name=getenv('POSTGRES_DB'))


user_api.engine = engine
app.include_router(user_api.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=7000, reload=True)
