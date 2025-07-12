from typing import Any, Dict
from fastapi import APIRouter, Request, status, Header, HTTPException
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import JSONResponse
from starlette.responses import RedirectResponse
from dotenv import load_dotenv
from os import getenv
from logging import getLogger


FRONTEND_URL = getenv("FRONTEND_URL", "http://127.0.0.1:3000")

from app.utils.jwt import create_jwt, verify_jwt

load_dotenv()

router = APIRouter()
logger = getLogger(__name__)

GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = getenv("GOOGLE_CLIENT_SECRET")
SECURE_LOGIN = getenv("SECURE_LOGIN")
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
    redirect_uri = "https://api-obscura.ccstiet.com/auth"
    return await oauth.google.authorize_redirect(request, redirect_uri)



@router.get("/auth")
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

    # Set HTTP-only cookie and redirect
    #Biscuit nhi Cookie set krna hai
    # Cookie will be HTTP-only, secure, and have a max age of 7 days
    response = RedirectResponse(url=f"{FRONTEND_URL}/oauth")
    
    response.set_cookie(
        key="session_token",
        value=jwt_token,
        httponly=True,
        secure=SECURE_LOGIN, 
        domain=".ccstiet.com" ,# Use SECURE_LOGIN from config 
        samesite="lax",  
        max_age=7 * 24 * 60 * 60,  
        path="/"
    )
    print(response)
    return response

@router.post("/logout")
async def logout(request: Request):
    """
    Logs the user out by clearing the session cookie and removing the stored JWT from the DB.
    """
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=400, detail="Session token not found")

    payload = verify_jwt(session_token)

    email = payload.get("sub")
    print("Decoded JWT payload:", payload)

    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    users = request.app.state.users

    # Remove the stored JWT from the database
    await users.update_one({"email": email}, {"$unset": {"jwt": ""}})

    # Clear the session cookie
    response = JSONResponse({"message": "Logged out successfully"}, status_code=200)
    response.delete_cookie(key="session_token", path="/")

    return response

@router.get("/me")
async def get_user_info(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not logged in")

    try:
        payload = verify_jwt(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in token")

    users = request.app.state.users
    user = await users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"name": user["name"], "email": user["email"]}