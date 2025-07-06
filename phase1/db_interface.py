from datetime import datetime

from threader import send_thread
from .db import questions, activity_logs, attempts, bonuses


# Questions
def get_question_via_id(question_id: str):
    return questions.find_one({"question_id": question_id})

def capture_question(question_id: str, capturer_team_name: str):
    send_thread(
        questions.update_one,
        (
            {"question_id": question_id},
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


def get_all_questions():
    return questions.find({})


def get_logs():
    return activity_logs.find({}).limit(10)


def insert_log(question_id: str, team_name: str):
    activity_logs.insert_one({
        "question_id": question_id,
        "captured_by": team_name,
        "timestamp": datetime.now(),
    })


def attempted_too_many_times(team_name: str, question_id: str):
    attempts_info = attempts.find_one({"team_name": team_name, "question_id": question_id})

    # First time attempting
    if attempts_info is None:
        return False

    return attempts_info["attempts"] >= 3

def mark_incorrect_attempt(team_name: str, question_id: str):
    # TODO CHECK: IF UPSERT ADDS team_name
    send_thread(
        attempts.update_one,
        (
            {"team_name": team_name, "question_id": question_id},
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


def mark_correct_attempt(team_name: str, question_id: str):
    send_thread(
        attempts.update_one,
        (
            {"team_name": team_name, "question_id": question_id},
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

def create_bonus(team_name: str, question_id: str, extra_points: str):
    assert extra_points != 0, "Extra points shouldn't be zero mate"
    send_thread(
        bonuses.insert_one,
        {
            "team_name": team_name,
            "question_id": question_id,
            "extra_points": extra_points,
        }
    )

def get_bonus(team_name: str):
    team_bonuses = bonuses.find_one({"team_name": team_name})
    return list(map(
        lambda bonus: { "question_id": bonus["question_id"], "extra_points": bonus["extra_points"] },
        team_bonuses
    ))