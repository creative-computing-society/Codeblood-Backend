import uvicorn
import loggers

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from socketio import AsyncServer, ASGIApp
from contextlib import asynccontextmanager
from logging import getLogger
from dotenv import load_dotenv
from os import getenv
from config import IS_DEV

from app.oauth import oauth_router
from app.registeration import registeration_routes
# from admin import admin_routes
from app.database import init_db, init_users, init_teams, init_lobbies

load_dotenv()

logger = getLogger(__name__)

SECRET_KEY = getenv("SESSION_SECRET_KEY")
assert SECRET_KEY is not None, "Session secret key not found!"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_users()
    await init_teams()
    await init_lobbies()

    from app.database import users, teams, lobbies

    app.state.users = users
    app.state.teams = teams
    app.state.lobbies = lobbies

    yield


app = FastAPI(debug=True, lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(oauth_router)
app.include_router(registeration_routes)
# app.include_router(admin_routes)

sio = AsyncServer()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=IS_DEV)
