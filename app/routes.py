import os
from logging import getLogger

from fastapi import APIRouter, Header, Request
from starlette.responses import JSONResponse
from authlib.integrations.starlette_client import OAuth

from config import IS_DEV
from .db_interface import (
    generate_session_token,
    delete_session,
    remove_all_sockets,
    get_user_id_create_user_if_doesnt_exist,
)

router = APIRouter()
oauth = OAuth()
logger = getLogger(__name__)


oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def validate_email(email: str):
    if IS_DEV:
        return email.endswith("@thapar.edu") or email.endswith("@gmail.com")
    return email.endswith("@thapar.edu")


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")  # this will be the callback
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        return {"error": "Failed to fetch user info"}

    email = user_info["email"]
    if not validate_email(email):
        return {"error": "Only thapar.edu or gmail.com domains are allowed"}

    user_id = get_user_id_create_user_if_doesnt_exist(email, user_info["name"])
    session_token = generate_session_token(str(user_id))

    return JSONResponse({"redirect_link": f"oauth?session_id={session_token}"})


@router.post("/logout")
async def logout(request: Request, session_id: str = Header(..., alias="X-Session-ID")):
    deleted = delete_session(session_id)

    if deleted.deleted_count != 1:
        return {"status": "session_not_found"}

    sio = request.app.state.sio
    await remove_all_sockets(sio, session_id)
    return {"status": "logged_out"}
