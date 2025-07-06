import json
from os import path
from typing import Any, Dict
from socketio import AsyncServer
from logging import getLogger

from mock_data import mockActivity
from .questions import questions, sets
from .db_interface import get_question_via_id, capture_question, get_all_questions, attempted_too_many_times, \
    mark_incorrect_attempt, mark_correct_attempt, insert_log, get_bonus, create_challenge, accept_challenge, \
    get_challenge, mark_incorrect_attempt_with_returned_attempts

from config import DIFFICULTY_TO_POINTS, get_is_mocks, get_is_dev
from app.db_interface import assign_team_points, get_socket_session, get_teams_of_sets, get_member_ids, \
    get_socket_connections_from_user_ids, get_team_points
from .questions import sets_without_question

ANSWER_JSON_FILE = path.join(path.dirname(__file__), "assets", "answers.json")
logger = getLogger("phase1")

CHALLENGE_POINTS = 100


if not path.exists(ANSWER_JSON_FILE):
    raise FileNotFoundError("answers.json file not found")


class WebSocketHandler:
    def __init__(
        self,
        sio: AsyncServer,
    ):
        self.sio = sio
        self.sio.on("get-team-points", self.get_self_team_points)
        self.sio.on("submit_answer", self.submit_answer)
        self.sio.on("submit_challenge_answer", self.submit_challenge_answer)
        self.sio.on("get_question_status", self.get_question_status)
        self.sio.on("accept-challenge", self.accept_challenge)
        self.sio.on("send-challenge", self.send_challenge)
        self.sio.on("get-challengeable-teams", self.get_challengeable_teams)
        self.sio.on("get-question", self.get_question)

        # These functions are only to bypass checks for testing
        if get_is_dev():
            self.sio.on("broadcast_capture", self.broadcast_capture)

    async def get_self_team_points(self, sid, _):
        session = get_socket_session(sid)
        if not session or not session["team_name"]:
            await self.sio.emit("error", {"detail": "User not in a team to represent"}, to=sid)
            return None
        return get_team_points(session["team_id"])

    async def submit_answer(self, sid: str, data: Dict[str, Any]) -> None:
        session = get_socket_session(sid)
        if not session or not session["team_name"]:
            await self.sio.emit("error", {"detail": "User not in a team to represent"}, to=sid)
            return

        if "question_id" not in data or "answer" not in data:
            await self.sio.emit("error", {"detail": "question_id & answer are the required fields"}, to=sid)
            return

        question_id: str = data["question_id"]
        submitted_answer: str = data["answer"]
        extra_points = 0

        if question_id not in sets[session["team_set"]]:
            team_bonuses = get_bonus(session["team_name"])
            for bonus_question in team_bonuses:
                if bonus_question["question_id"] != question_id:
                    continue
                extra_points = bonus_question["extra_points"]
                break

            if extra_points == 0:
                await self.sio.emit("error", {"detail": "invalid question"}, to=sid)
                return

        if attempted_too_many_times(session["team_name"], question_id):
            await self.sio.emit("question_locked", {"question_id": question_id}, to=sid)
            return

        question = list(filter(lambda x: x["id"] == question_id, questions))
        if len(question) == 0:
            await self.sio.emit("error", {"detail": "invalid_question"}, to=sid)
            logger.error(
                f"Missing or invalid question was passed! Question ID: {question_id}"
            )
            return

        question = question[0]
        correct_answer = question["answer"]

        #TODO: Talk about bonuses if another team solved the question (which wasn't bonus to them)
        # Then should the team that got the bonus get screwed over?
        question_doc = get_question_via_id(question_id)
        if not question_doc:
            await self.sio.emit("answer_response", {"status": "invalid_question"}, to=sid)
            return

        if question_doc.get("captured"):
            await self.sio.emit(
                "answer_response", {"status": "already_captured"}, to=sid
            )
            return

        if submitted_answer.strip().lower() != correct_answer.lower():
            mark_incorrect_attempt(session["team_name"], question_id)
            await self.sio.emit("answer_response", {"status": "incorrect"}, to=sid)
            return

        mark_correct_attempt(session["team_name"], question_id)
        capture_question(question_id, session["team_name"])
        assign_team_points(
            session["team_name"],
            DIFFICULTY_TO_POINTS[question.get("difficulty", "easy")] + extra_points
        )
        insert_log(question_id, session["team_name"])
        await self.sio.emit(
            "activity-update", {"question_id": question_id, "captured_by": session["team_name"]}
        )
        await self.sio.emit("answer_response", {"status": "correct"}, to=sid)

    async def submit_challenge_answer(self, sid, data: Dict[str, Any]) -> None:
        session = get_socket_session(sid)
        if not session or not session["team_name"]:
            await self.sio.emit("error", {"detail": "User not in a team to represent"}, to=sid)
            return

        if "accept_code" not in data or "answer" not in data:
            await self.sio.emit("error", {"detail": "accept_code & answer are the required fields"}, to=sid)
            return

        challenge_doc = get_challenge(data["accept_code"])

        if challenge_doc["accepter_team"] != session["team_name"]:
            await self.sio.emit("error", {"detail": "mate you can't answer someone else's challenge"}, to=sid)
            return

        question_id = challenge_doc["question_id"]

        if attempted_too_many_times(session["team_name"], question_id):
            await self.sio.emit("question_locked", {"question_id": question_id}, to=sid)
            return

        question = list(filter(lambda x: x["id"] == question_id, questions))
        if len(question) == 0:
            await self.sio.emit("error", {"detail": "invalid_question"}, to=sid)
            logger.error(
                f"Missing or invalid question was passed! Question ID: {question_id}"
            )
            return

        question = question[0]
        correct_answer = question["answer"]

        if data["answer"].strip().lower() == correct_answer.lower():
            mark_correct_attempt(session["team_name"], question_id)
            capture_question(question_id, session["team_name"])
            assign_team_points(
                session["team_name"],
                DIFFICULTY_TO_POINTS[question.get("difficulty", "easy")] + CHALLENGE_POINTS # technically the NET is not zero, but i think this is fine
            )
            assign_team_points(challenge_doc["challenger_team"], -CHALLENGE_POINTS)
            insert_log(question_id, session["team_name"])
            await self.sio.emit(
                "activity-update", {"question_id": question_id, "captured_by": session["team_name"]}
            )
            await self.sio.emit("answer_response", {"status": "correct"}, to=sid)
            return

        attempt_num = mark_incorrect_attempt_with_returned_attempts(session["team_name"], question_id)
        if attempt_num == 3:
            assign_team_points(session["team_name"], -CHALLENGE_POINTS)
            assign_team_points(challenge_doc["challenger_team"], CHALLENGE_POINTS)

        await self.sio.emit("answer_response", {"status": "incorrect"}, to=sid)

    @staticmethod
    def _process_question(question: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "question_id": question["_id"],
            "captured": question.get("captured", False),
            "captured_by": question.get("captured_by"),
        }

    # The reason I added a blank argument is if the socket did send some info (which we don't need)
    # python would crash complaining about too many arguments passed in, because fucking python
    # so the _ is the data that was sent but fuck that
    async def get_question_status(self, sid: str, _) -> None:
        if get_is_mocks():
            return mockActivity
        question_list = get_all_questions()
        captured_list = [self._process_question(question) for question in question_list]

        await self.sio.emit("question_status", captured_list, to=sid)
        return None

    async def broadcast_capture(self, sid: str, data):
        try:
            data = json.loads(data)
        except:
            await self.sio.emit("error", {"status": "wtf yuo doin? send me json"}, to=sid)
            return
        if "question_id" not in data or "team_name" not in data:
            await self.sio.emit("reply", {"status": "question_id & team_name needed"}, to=sid)
            return
        await self.sio.emit(
            "activity-update", {"question_id": data["question_id"], "captured_by": data["team_name"]}
        )

    async def accept_challenge(self, sid: str, data):
        session = get_socket_session(sid)
        if not session or not session["team_name"]:
            await self.sio.emit("error", {"detail": "User not in a team to represent"}, to=sid)
            return None
        if "accept_code" not in data:
            await self.sio.emit("error", {"detail": "Missing accept_code"}, to=sid)
            return None

        accept_challenge(session["team_name"], data["accept_code"])
        return None

    async def send_challenge(self, sid: str, data):
        session = get_socket_session(sid)
        if not session or not session["team_name"]:
            await self.sio.emit("error", {"detail": "User not in a team to represent"}, to=sid)
            return None
        if "target_team" not in data or "target_question_id" not in data:
            await self.sio.emit("error", {"detail": "Missing target_team or target_question_id"}, to=sid)
            return None

        target_team = data["target_team"]
        target_question_id = data["target_question_id"]

        question = list(filter(lambda x: x["id"] == target_question_id, questions))
        if len(question) == 0:
            await self.sio.emit("error", {"detail": "invalid_question"}, to=sid)
            logger.error("Missing or invalid question was passed!")
            return

        accept_code = create_challenge(target_team, target_question_id)
        members = get_member_ids(target_team)
        socket_connections = get_socket_connections_from_user_ids(members)

        await self.sio.emit("incoming-challenge", {
            "question_id": target_question_id,
            "challenger_name": target_team,
            "accept_code": accept_code,
        }, to=socket_connections)
        return {"info": "sent"}

    async def get_challengeable_teams(self, sid: str, question_id: str):
        #TODO: if we get a different bonus question set, then only include teams that are actively connected
        session = get_socket_session(sid)
        if not session or not session["team_name"]:
            await self.sio.emit("error", {"detail": "User not in a team to represent"}, to=sid)
            return None
        return list(map(
            lambda team: team["name"],
            get_teams_of_sets(sets_without_question(question_id))
        ))

    async def get_question(self, sid: str, data):
        session = get_socket_session(sid)
        if not session or not session["team_name"]:
            await self.sio.emit("error", {"detail": "User not in a team to represent"}, to=sid)
            return
        if "question_id" not in data:
            await self.sio.emit("error", {"detail": "Missing question_id in data"}, to=sid)
            return

        question_id = data["question_id"]
        question_info = list(filter(lambda x: x["id"] == question_id, questions))
        if len(question_info) == 0:
            await self.sio.emit("error", {"detail": "No question info"}, to=sid)
            return