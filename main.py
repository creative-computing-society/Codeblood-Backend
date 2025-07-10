import uvicorn
import loggers
import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from socketio import AsyncServer, ASGIApp
from contextlib import asynccontextmanager
from logging import getLogger
from dotenv import load_dotenv
from os import getenv

from starlette.middleware.base import BaseHTTPMiddleware
from app.oauth import oauth_router
from app.registeration import registeration_routes
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, init_users, init_teams, init_lobbies

load_dotenv()

logger = getLogger(__name__)

SECRET_KEY = getenv("SESSION_SECRET_KEY")
IS_DEV = getenv("IS_DEV")
SECURE_LOGIN = getenv("SECURE_LOGIN")
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
# Add SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# print(f"SECRET_KEY: {SECRET_KEY}")

@app.middleware("http")
async def debug_middleware(request, call_next):
    # print(f"Request scope: {request.scope}")
    response = await call_next(request)
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Include routers
app.include_router(oauth_router)
app.include_router(registeration_routes)
# app.include_router(admin_routes

@app.get("/test")
async def test():
    return {"message": "backend is up and running!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3021, reload=IS_DEV)

