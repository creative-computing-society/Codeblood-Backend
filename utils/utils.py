from secrets import choice
from string import ascii_letters, digits
from uuid import uuid5, UUID
from typing import Dict, Tuple, Any


UUID_NAMESPACE = UUID("5d8b4e77-52f7-4c84-a12f-1234567890ab")


def create_team_code(length=8):
    chars = ascii_letters + digits
    return "".join(choice(chars) for _ in range(length))


def generate_player_uuid(player_name: str):
    return str(uuid5(UUID_NAMESPACE, player_name))


def generate_initial_team(
    team_name: str, player_name: str, email: str
) -> Dict[str, Any]:
    team_code = create_team_code()
    player_id = generate_player_uuid(player_name)
    return {
        "team_name": team_name,
        "team_code": team_code,
        "players": [
            {
                "name": player_name,
                "id": player_id,
                "email": email,
            }
        ],
        "team_leader_email": email,
    }


def add_player(
    team_code: str, player_name: str, email: str
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    player_id = generate_player_uuid(player_name)

    return (
        {
            "team_code": team_code,
            "$expr": {"$lt": [{"$size": "$players"}, 4]},
        },  # This part is filtering for 4 players
        {
            "$push": {
                "players": {
                    "name": player_name,
                    "id": player_id,
                    "email": email,
                }
            }
        },  # This part adds the player into the database
    )
