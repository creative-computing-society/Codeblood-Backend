import json
from asyncio import gather
from os import path
from typing import Any, Dict
from socketio import AsyncServer
from logging import getLogger

from .db_interface import get_nation_via_id, capture_nation, get_all_nations

from config import DIFFICULTY_TO_POINTS
from app.db_interface import assign_team_points


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

    async def _validate_answer(
        self, nation_id: str, submitted_answer: str, team_name: str
    ):
        result = True
        if nation_id == "":
            await self.sio.emit("error", {"detail": "Nation ID is None!"})
            result = False

        if submitted_answer == "":
            await self.sio.send({"detail": "Answer cannot be None!"})
            result = False

        if team_name == "":
            await self.sio.send({"detail": "Haan haan, bina team name ke kaam karenge"})
            result = False

        return result

    async def submit_answer(self, sid: str, data: Dict[str, Any]) -> None:
        nation_id: str = data.get("nation_id", "")
        submitted_answer: str = data.get("answer", "")
        team_name: str = data.get("team_name", "")

        if not await self._validate_answer(nation_id, submitted_answer, team_name):
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
            await self.sio.emit("answer_response", {"status": "incorrect"}, to=sid)
            return

        capture_nation(nation_id, team_name)
        assign_team_points(
            team_name, DIFFICULTY_TO_POINTS[nation.get("difficulty", "easy")]
        )

        await self.sio.emit(
            "nation_captured", {"nation_id": nation_id, "captured_by": team_name}
        )

        await self.sio.emit("answer_response", {"status": "correct"}, to=sid)

    @staticmethod
    async def _process_nation(nation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "nation_id": nation["_id"],
            "captured": nation.get("captured", False),
            "captured_by": nation.get("captured_by"),
        }

    # The reason I added a blank argument is if the socket did send some info (which we don't need)
    # python would crash complaining about too many arguments passed in, because fucking python
    # so the _ is the data that was sent but fuck that
    async def get_nation_status(self, sid: str, _) -> None:
        nations = get_all_nations()
        process_tasks = [self._process_nation(nation) for nation in nations]

        captured_list = await gather(*process_tasks)
        await self.sio.emit("nation_status", captured_list, to=sid)
