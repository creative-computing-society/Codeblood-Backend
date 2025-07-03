import uuid
from datetime import datetime, timedelta
from app.db.mongo import sessions_col

def generate_session_token(user_id: str) -> str:
    namespace = uuid.UUID("5d8b4e77-52f7-4c84-a12f-1234567890ab")
    session_id = str(uuid.uuid5(namespace, user_id + str(datetime.utcnow())))
    
    sessions_col.insert_one({
        "_id": session_id,
        "user_id": "hehe",
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=24)
    })

    return session_id

def validate_session(session_id: str) -> str | None:
    session = sessions_col.find_one({"_id": session_id})
    if session and session["expires_at"] > datetime.utcnow():
        return session["user_id"]
    return None