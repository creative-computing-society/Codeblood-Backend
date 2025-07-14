from secrets import choice
from string import ascii_letters, digits
from uuid import uuid5, UUID
from typing import Dict, Tuple, Any
from bson import ObjectId
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorCollection
from logging import getLogger
from random import choice

logger = getLogger(__name__)

UUID_NAMESPACE = UUID("5d8b4e77-52f7-4c84-a12f-1234567890ab")


def create_team_code(length=8):
    chars = ascii_letters + digits
    return "".join(choice(chars) for _ in range(length))


def generate_player_uuid(email: str):
    return str(uuid5(UUID_NAMESPACE, email))

def generate_initial_team(
    team_name: str, player_name: str, email: str, discord_id: str, rollno: str
) -> Dict[str, Any]:
    team_code = create_team_code()
    player_id = generate_player_uuid(email)
    is_hacker = choice([True, False])  # Randomly assign hacker or wizard role
    is_wizard = not is_hacker  # Ensure complementary roles

    return {
        "team_name": team_name,
        "team_code": team_code,
        "players": [
            {
                "name": player_name,
                "id": player_id,
                "email": email,
                "discord_id": discord_id,
                "rollno": rollno,
                "is_hacker": is_hacker,
                "is_wizard": is_wizard,
            }
        ],
        "team_leader_email": email,
    }

def add_player(
    team_code: str, player_name: str, email: str, discord_id: str, rollno: str, existing_players: List[Dict[str, Any]]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    player_id = generate_player_uuid(player_name)

    # Count existing hackers and wizards
    hacker_count = sum(player["is_hacker"] for player in existing_players)
    wizard_count = sum(player["is_wizard"] for player in existing_players)

    # Randomly assign roles while adhering to constraints
    if hacker_count < 2 and wizard_count < 2:
        is_hacker = choice([True, False])
        is_wizard = not is_hacker
    elif hacker_count < 2:
        is_hacker = True
        is_wizard = False
    elif wizard_count < 2:
        is_hacker = False
        is_wizard = True
    else:
        raise ValueError("Cannot add more hackers or wizards")

    return (
        {
            "team_code": team_code,
            "$expr": {"$lt": [{"$size": "$players"}, 4]},
        },
        {
            "$push": {
                "players": {
                    "name": player_name,
                    "id": player_id,
                    "email": email,
                    "discord_id": discord_id,
                    "rollno": rollno,
                    "is_hacker": is_hacker,
                    "is_wizard": is_wizard,
                }
            }
        },
    )


async def add_teamid_to_user(request: Request, team_code: str, email: str):
    teams: AsyncIOMotorCollection = request.app.state.teams
    users: AsyncIOMotorCollection = request.app.state.users

    # Step 1: Find the team
    team = await teams.find_one({"team_code": team_code})

    assert team is not None, (
        "We have a problem, i just inserted the team and it did not insert"
    )

    team_id = team["_id"]  # this is an ObjectId

    # Step 2: Add this team_id to the user
    result = await users.update_one(
        {"email": email},  # Find user by email
        {"$set": {"team_id": team_id}},  # Add or update team_id field
    )

    if result.modified_count == 0:
        logger.warning(
            f"User was unable to be added to team. Team Code: {team_code}, Email: {email}"
        )
