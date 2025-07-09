from typing import Any, Dict
from fastapi import APIRouter, Request, status
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import JSONResponse

from dotenv import load_dotenv
from os import getenv
from logging import getLogger

from utils.jwt import create_jwt

load_dotenv()

router = APIRouter(prefix="/auth")
logger = getLogger(__name__)

GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = getenv("GOOGLE_CLIENT_SECRET")

assert GOOGLE_CLIENT_ID is not None and GOOGLE_CLIENT_SECRET is not None, (
    "Client ID or Client Secret is None!"
)

config = Config(
    environ={
        "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
        "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
    }
)

oauth = OAuth(config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    resp = await oauth.google.get(
        "https://www.googleapis.com/oauth2/v3/userinfo", token=token
    )
    user: Dict[str, Any] = resp.json()

    email = user["email"]
    access_token = token["access_token"]

    jwt_token = create_jwt(email, access_token)
    users = request.app.state.users

    # Save to MongoDB
    await users.update_one(
        {"email": email},
        {
            "$set": {
                "name": user["name"],
                "jwt": jwt_token,
            }
        },
        upsert=True,
    )

    # Return JWT to frontend (store in localStorage or cookie)
    return JSONResponse(
        {"token": jwt_token, "email": email, "name": user["name"]},
        status_code=status.HTTP_200_OK,
    )
