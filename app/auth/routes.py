from fastapi import APIRouter
from starlette.responses import JSONResponse
from authlib.integrations.starlette_client import OAuth
import os

from config import IS_DEV
from ..db.mongo import users_col
from ..auth.session import generate_session_token
from fastapi import Header, Request
from ..db.mongo import sessions_col, sockets_col
from ..socketio.socket_map import remove_socket


router = APIRouter()

oauth = OAuth()

oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth')  # this will be the callback
    return await oauth.google.authorize_redirect(request, redirect_uri)

def validate_email(email: str):
    if IS_DEV:
        return email.endswith("@thapar.edu") or email.endswith("@gmail.com")
    return email.endswith("@thapar.edu")

@router.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        return {"error": "Failed to fetch user info"}

    email = user_info["email"]
    if not validate_email(email):
        return {"error": "Only thapar.edu or gmail.com domains are allowed"}

    # Save user if new
    existing_user = users_col.find_one({"email": email})
    if not existing_user:
        user_id = users_col.insert_one({
            "email": email,
            "name": user_info["name"]
        }).inserted_id
    else:
        user_id = existing_user["_id"]

    # Generate session token
    session_token = generate_session_token(str(user_id))

    return JSONResponse({ "redirect_link": f"oauth?session_id={session_token}" })

@router.post("/logout")
async def logout(request: Request, session_id: str = Header(..., alias="X-Session-ID")):
    deleted = sessions_col.delete_one({"_id": session_id})
    
    if deleted.deleted_count != 1:
        return {"status": "session_not_found"}

    # Get the socket.io server instance
    sio = request.app.state.sio

    # Find all sockets linked to this session
    sockets = sockets_col.find({"session_id": session_id})
    for s in sockets:
        socket_id = s["_id"]
        await sio.disconnect(socket_id)
        remove_socket(socket_id)

    return {"status": "logged_out"}