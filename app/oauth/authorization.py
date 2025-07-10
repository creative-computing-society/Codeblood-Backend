from fastapi import Header, HTTPException, Request
from logging import getLogger

from app.utils.jwt import verify_jwt

logger = getLogger(__name__)


# Extracts JWT token from header and validates it
async def get_current_user(request: Request, authorization: str = Header(...)):
    users = request.app.state.users

    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid auth header")

    token = authorization.split(" ")[1]
    payload = verify_jwt(token)
    if not payload:
        raise HTTPException(401, "Invalid or expired token")

    user = await users.find_one({"email": payload["sub"]})
    if not user:
        raise HTTPException(403, "User not registered")

    return user
