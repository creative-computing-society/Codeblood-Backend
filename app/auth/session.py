import uuid
from datetime import datetime, timedelta
from ..db.mongo import sessions_col

NAMESPACE = uuid.UUID("5d8b4e77-52f7-4c84-a12f-1234567890ab")


def generate_session_token(user_id: str) -> str:
    session_id = str(uuid.uuid5(NAMESPACE, user_id + str(datetime.now())))
    
    sessions_col.insert_one({
        "_id": session_id,
        "user_id": user_id,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=24)
    })

    return session_id

def validate_session(session_id: str) -> str | None:
    session = sessions_col.find_one({"_id": session_id})
    if session and session["expires_at"] > datetime.now():
        return session["user_id"]
    return None