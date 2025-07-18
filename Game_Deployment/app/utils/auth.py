from fastapi import Request, HTTPException, Depends
from app.utils.jwt import verify_jwt

async def verify_cookie(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized: Missing session token")

    payload = verify_jwt(token)
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid session token")

    return email  # Return the email for use in the route