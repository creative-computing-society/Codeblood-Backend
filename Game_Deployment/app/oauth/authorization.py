from fastapi import Header, HTTPException, Request
from logging import getLogger

from app.utils.jwt import verify_jwt

logger = getLogger(__name__)


# Extracts JWT token from header and validates it
# async def get_current_user(request: Request, authorization: str = Header(...)):
#     users = request.app.state.users

#     if not authorization.startswith("Bearer "):
#         raise HTTPException(401, "Invalid auth header")

#     token = authorization.split(" ")[1]
#     payload = verify_jwt(token)
#     if not payload:
#         raise HTTPException(401, "Invalid or expired token")

#     user = await users.find_one({"email": payload["sub"]})
#     if not user:
#         raise HTTPException(403, "User not registered")

#     return user

async def get_current_user(request: Request):
    users = request.app.state.users

    # Retrieve the session token from cookies
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Session token not found")

    payload = verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await users.find_one({"email": payload["email"]})
    if not user:
        raise HTTPException(status_code=403, detail="User not registered")

    return user