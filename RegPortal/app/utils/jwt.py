from fastapi import HTTPException
from jose import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from os import getenv
from logging import getLogger
from typing import Dict, Any

load_dotenv()

logger = getLogger(__name__)

key = getenv("JWT_SECRET_KEY")

if key is None:
    logger.error("JWT is missing!")
    raise

SECRET_KEY = key
ALGORITHM = "HS256"
TOKEN_EXPIRY = (
    60 * 24 * 13
)  # 13 day expiry cause 19th ko event hain and we expect delays


def create_jwt(email: str, access_token: str):
    payload = {
        "email": email,
        "token": access_token,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        # print(f"Decoded JWT payload: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        print("JWT expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        print("Invalid JWT")
        raise HTTPException(status_code=401, detail="Invalid token")