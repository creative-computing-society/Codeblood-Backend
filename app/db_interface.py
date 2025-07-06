from random import choice
from typing import List

from threader import send_thread
from .db import users, socket_connections, token_sessions, teams
from datetime import datetime, timedelta
import uuid
from bson import ObjectId

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


def get_socket_session(socket_id):
    return socket_connections.find_one({"socket_id": socket_id})


# Socket Connections
def save_socket(session_id: str, session_data: dict, socket_id: str):
    send_thread(
        socket_connections.insert_one,
        {
            "socket_id": socket_id,
            "session_id": session_id,
            "user_id": session_data["user_id"],
            "team_name": session_data.get("team_name", None),
            "team_id": session_data.get("team_id", None),
            "team_set": session_data.get("team_set", None),
        },
    )


def get_socket_connections_from_user_ids(user_ids: List[str]) -> List[str]:
    return list(map(
        lambda connection: connection["socket_id"],
        socket_connections.find({
            "user_id": {"$in": user_ids}
        })
    ))


def remove_socket(socket_id: str):
    send_thread(socket_connections.delete_one, {"socket_id": socket_id})


def remove_socket_unthreaded(socket_id: str):
    socket_connections.delete_one({"socket_id": socket_id})


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


# Token sessions
def generate_session_token(user_id: str) -> str:
    session_id = str(uuid.uuid5(NAMESPACE, user_id + str(datetime.now())))

    send_thread(
        token_sessions.insert_one,
        {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=24),
        },
    )

    return session_id


def get_session(session_id: str) -> dict | None:
    session = token_sessions.find_one({"session_id": session_id})
    if not session:
        return None
    if session["expires_at"] > datetime.now():
        delete_session(session_id)
        return None
    return session


def delete_session(session_id: str):
    return token_sessions.delete_one({"session_id": session_id})


# Teams
def get_random_team():
    return choice(teams.find({}))

def assign_team_points(team_name: str, points: int):
    send_thread(
        teams.update_one,
        ({"name": team_name}, {"$inc": {"points": points}}),
        {"upsert": True},
    )

def get_teams_of_sets(sets: List[str]):
    return teams.find({
        "set": { "$in": sets }
    })

def get_member_ids(team_name: str) -> List[str]:
    doc = teams.find_one({"name": team_name})
    if doc is None:
        return []
    return doc["members"]

def get_team_points(team_id: str) -> int:
    doc = teams.find_one({"_id": team_id})
    if doc is None:
        return 0
    try:
        return int(doc["points"])
    except:
        return 0
