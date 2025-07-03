from threader import send_thread
from .db import users, socket_connections, token_sessions, teams
from datetime import datetime, timedelta
import uuid

NAMESPACE = uuid.UUID("5d8b4e77-52f7-4c84-a12f-1234567890ab")


# Users
def find_user_via_email(email: str):
    return users.find_one({"email": email})


def insert_user(email: str, name: str) -> str:
    return users.insert_one({"email": email, "name": name}).inserted_id


def get_user_id_create_user_if_doesnt_exist(email: str, name: str) -> str:
    existing_user = find_user_via_email(email)
    if not existing_user:
        return insert_user(email, name)
    return existing_user["_id"]


# Socket Connections
def save_socket(session_id: str, socket_id: str):
    send_thread(
        socket_connections.update_one,
        (
            {"_id": socket_id},
            {"$set": {"session_id": session_id}},
        ),
        {"upsert": True},
    )


def remove_socket(socket_id: str):
    send_thread(socket_connections.delete_one, ({"_id": socket_id},))


def remove_socket_unthreaded(socket_id: str):
    socket_connections.delete_one({"_id": socket_id})


async def remove_all_sockets_unthreaded(sio, session_id: str):
    sockets = socket_connections.find({"session_id": session_id})
    for s in sockets:
        socket_id = s["_id"]
        await sio.disconnect(socket_id)
        remove_socket_unthreaded(socket_id)


def remove_all_sockets(sio, session_id):
    send_thread(
        remove_socket_unthreaded,
        (
            sio,
            session_id,
        ),
    )


def get_all_sockets() -> list[str]:
    return [doc["_id"] for doc in socket_connections.find({})]


# Token sessions
def generate_session_token(user_id: str) -> str:
    session_id = str(uuid.uuid5(NAMESPACE, user_id + str(datetime.now())))

    send_thread(
        token_sessions.insert_one,
        (
            {
                "_id": session_id,
                "user_id": user_id,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=24),
            },
        ),
    )

    return session_id


def validate_session(session_id: str) -> str | None:
    session = token_sessions.find_one({"_id": session_id})
    if session and session["expires_at"] > datetime.now():
        return session["user_id"]
    return None


def delete_session(session_id: str):
    return token_sessions.delete_one({"_id": session_id})


# Teams
def assign_team_points(team_name: str, points: int):
    send_thread(
        teams.update_one,
        ({"name": team_name}, {"$inc": {"points": points}}),
        {"upsert": True},
    )
