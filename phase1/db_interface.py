from datetime import datetime

from threader import send_thread
from .db import nations, acitivity_logs, attempts


# Nations
def get_nation_via_id(nation_id: str):
    return nations.find_one({"_id": nation_id})

def capture_nation(nation_id: str, capturer_team_name: str):
    send_thread(
        nations.update_one,
        (
            {"_id": nation_id},
            {
                "$set": {
                    "captured": True,
                    "captured_by": capturer_team_name,
                    "timestamp": datetime.now(),
                }
            },
        ),
        {"upsert": True}
    )

def get_all_nations():
    return nations.find({})

def get_logs():
    return acitivity_logs.find({}).limit(10)


def attempted_too_many_times(team_name: str, nation_id: str):
    return attempts.find_one({"team_name": team_name, "nation_id": nation_id})["attempts"] >= 3

def mark_incorrect_attempt(team_name: str, nation_id: str):
    # TODO CHECK: IF UPSERT ADDS team_name
    send_thread(
        attempts.update_one,
        (
            {"team_name": team_name, "nation_id": nation_id},
            {
                "$inc": {
                    "attempts": 1,
                },
                "$set": {
                    "solved": False,
                }
            },
        ),
        {"upsert": True}
    )


def mark_correct_attempt(team_name: str, nation_id: str):
    send_thread(
        attempts.update_one,
        (
            {"team_name": team_name, "nation_id": nation_id},
            {
                "$inc": {
                    "attempts": 1,
                },
                "$set": {
                    "solved": True
                }
            },
        ),
        {"upsert": True}
    )
