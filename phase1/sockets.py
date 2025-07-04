import json
from asyncio import gather
from os import path
from typing import Any, Dict
from socketio import AsyncServer
from logging import getLogger

from mock_data import mockChallenges
from .db_interface import get_nation_via_id, capture_nation, get_all_nations, attempted_too_many_times, \
    mark_incorrect_attempt, mark_correct_attempt

from config import DIFFICULTY_TO_POINTS, get_is_mocks, get_is_dev
from app.db_interface import assign_team_points, get_socket_session

ANSWER_JSON_FILE = path.join(path.dirname(__file__), "assets", "answers.json")
logger = getLogger("phase1")


if not path.exists(ANSWER_JSON_FILE):
    raise FileNotFoundError("answers.json file not found")

# Load answers once at startup
with open(ANSWER_JSON_FILE) as f:
    ANSWERS: Dict[str, Dict[str, str]] = json.load(f)

# {
# "nation_001" : {
#       "answers" : "yes",
#       "difficulty": no
# },
# "nation_002" : "no"
# }


class WebSocketHandler:
    def __init__(
        self,
        sio: AsyncServer,
    ):
        self.sio = sio
        self.ANSWERS = ANSWERS

        self.sio.on("submit_answer", self.submit_answer)
        self.sio.on("get_nation_status", self.get_nation_status)

        # These functions are only to bypass checks for testing
        if get_is_dev():
            self.sio.on("broadcast_capture", self.broadcast_capture)

    async def submit_answer(self, sid: str, data: Dict[str, Any]) -> None:
        session = get_socket_session(sid)
        if not session or not session["team_name"]:
            await self.sio.emit("error", {"detail": "User not in a team to represent"})
            return

        if "nation_id" not in data or "answer" not in data:
            await self.sio.emit("error", {"detail": "nation_id & answer are the required fields"})
            return
        nation_id: str = data["nation_id"]
        submitted_answer: str = data["answer"]

        if attempted_too_many_times(session["team_name"], nation_id):
            await self.sio.emit("nation_locked", {"nation_id": nation_id}, to=sid)
            return


        nation = self.ANSWERS.get(nation_id)

        if nation is None:
            await self.sio.emit("answer_response", {"status": "invalid_nation"}, to=sid)
            logger.error(
                f"Missing or invalid nation was passed! Nation ID: {nation_id}"
            )
            return

        correct_answer = nation.get("answer")

        if not correct_answer:
            await self.sio.emit("answer_response", {"status": "invalid_nation"}, to=sid)
            return

        nation_doc = get_nation_via_id(nation_id)
        if not nation_doc:
            await self.sio.emit("answer_response", {"status": "invalid_nation"}, to=sid)
            return

        if nation_doc.get("captured"):
            await self.sio.emit(
                "answer_response", {"status": "already_captured"}, to=sid
            )
            return

        if submitted_answer.strip().lower() != correct_answer.lower():
            mark_incorrect_attempt(session["team_name"], nation_id)
            await self.sio.emit("answer_response", {"status": "incorrect"}, to=sid)
            return

        mark_correct_attempt(session["team_name"], nation_id)
        capture_nation(nation_id, session["team_name"])
        assign_team_points(
            session["team_name"], DIFFICULTY_TO_POINTS[nation.get("difficulty", "easy")]
        )

        await self.sio.emit(
            "activity-update", {"nation_id": nation_id, "captured_by": session["team_name"]}
        )

        await self.sio.emit("answer_response", {"status": "correct"}, to=sid)

    @staticmethod
    def _process_nation(nation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "nation_id": nation["_id"],
            "captured": nation.get("captured", False),
            "captured_by": nation.get("captured_by"),
        }

    # The reason I added a blank argument is if the socket did send some info (which we don't need)
    # python would crash complaining about too many arguments passed in, because fucking python
    # so the _ is the data that was sent but fuck that
    async def get_nation_status(self, sid: str, _) -> None:
        if get_is_mocks():
            return mockChallenges
        nations = get_all_nations()
        captured_list = [self._process_nation(nation) for nation in nations]

        await self.sio.emit("nation_status", captured_list, to=sid)
        return None

    async def broadcast_capture(self, sid: str, data):
        try:
            data = json.loads(data)
        except:
            await self.sio.emit("error", {"status": "wtf yuo doin? send me json"}, to=sid)
            return
        if "nation_id" not in data or "team_name" not in data:
            await self.sio.emit("reply", {"status": "nation_id & team_name needed"}, to=sid)
            return
        print("emitting")
        await self.sio.emit(
            "activity-update", {"nation_id": data["nation_id"], "captured_by": data["team_name"]}
        )