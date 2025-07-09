import uvicorn
import loggers

from fastapi import FastAPI
from socketio import AsyncServer, ASGIApp
from contextlib import asynccontextmanager
from logging import getLogger

from oauth import oauth_router
from registeration import registeration_routes
from database import init_db, init_users, init_teams, init_lobbies

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_users()
    await init_teams()
    await init_lobbies()

    from database import users, teams, lobbies

    app.state.users = users
    app.state.teams = teams
    app.state.lobbies = lobbies
    app.state.teams = teams

    yield


app = FastAPI(debug=True, lifespan=lifespan)
app.include_router(oauth_router)
app.include_router(registeration_routes)

sio = AsyncServer()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
