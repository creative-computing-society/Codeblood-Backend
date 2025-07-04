from random import choices
from app.db import users, token_sessions, teams
from threader import send_thread
from string import ascii_lowercase
from .db import team_codes

#TODO: there is no limit to the people that can be in a team

def assign_team_to_user_unthreaded(user_id: str, team_code: str):
    # NOTE: even if the code is invalid, the endpoint would still return "status": "ok", without joining the person to the team
    team_info = team_codes.find_one({"code": team_code})
    if team_info is None:
        return
    users.update_one(
        {"_id": user_id},
        {"$set": {
            "team_id": team_info["id"],
            "team_name": team_info["name"]
        }}
    )
    token_sessions.update_one(
        {"user_id": user_id},
        {"$set": {
            "team_id": team_info["id"],
            "team_name": team_info["name"]
        }}
        # No upserting, it just means the user didn't login
    )
    teams.update_one(
        {"_id": team_info["id"]},
        {"$inc": {
            "member_count": 1,
            "members": [user_id],
        }}
    )

def assign_team_to_user(user_id: str, team_code: str):
    send_thread(
        assign_team_to_user_unthreaded,
        (user_id, team_code.lower()),
    )


def create_team_registration(team_name: str, creator_id: str):
    join_code = "".join(choices(ascii_lowercase, k=8))
    send_thread(
        create_team_registration_unthreaded,
        (team_name, creator_id, join_code)
    )
    return join_code


def create_team_registration_unthreaded(team_name: str, creator_id: str, join_code: str):
    team_id = teams.insert_one({
        "team_name": team_name,
        "member_count": 1,
        "members": [creator_id],
    }).inserted_id
    team_codes.insert_one({"code": join_code, "id": team_id, "name": team_name})
    users.update_one(
        {"_id": creator_id},
        {"$set": {
            "team_id": team_id,
            "team_name": team_name
        }}
    )
    token_sessions.update_one(
        {"user_id": creator_id},
        {"$set": {
            "team_id": team_id,
            "team_name": team_name
        }}
        # No upserting, it just means the user didn't login
    )

    return join_code
