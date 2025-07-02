import json
from asyncio import gather
from os import path
from typing import Any, Dict
from socketio import AsyncServer

from app.db_interface import assign_team_points
from .db_interface import get_nation_via_id, capture_nation, get_all_nations
from config import DIFFICULTY_TO_POINTS

ANSWER_JSON_FILE = path.join("phase1", "assets", "answers.json")
if not path.exists(ANSWER_JSON_FILE):
    raise FileNotFoundError("answers.json file not found")


# Load answers once at startup
with open(ANSWER_JSON_FILE) as f:
    ANSWERS: Dict[str, str] = {
        entry["nation_id"]: entry["answer"] for entry in json.load(f)
    }


class WebSocketHandler:
    def __init__(
        self,
        sio: AsyncServer,
    ):
        self.sio = sio
        self.ANSWERS = ANSWERS

        self.sio.on("submit_answer", self.submit_answer)
        self.sio.on("get_nation_status", self.get_nation_status)

    async def _validate_answer(self, nation_id, submitted_answer, team_name):
        result = True
        if not nation_id:
            await self.sio.emit("error", {"detail": "Nation ID is None!"})
            result = False

        if not submitted_answer:
            await self.sio.send({"detail": "Answer cannot be None!"})
            result = False

        if not team_name:
            await self.sio.send({"detail": "Haan haan, bina team name ke kaam karenge"})
            result = False

        return result

    async def submit_answer(self, sid: str, data: Dict[str, Any]) -> None:
        nation_id = data.get("nation_id")
        submitted_answer = data.get("answer")
        team_name = data.get("team_name")

        if not await self._validate_answer(nation_id, submitted_answer, team_name):
            return

        correct_answer = self.ANSWERS.get(nation_id)
        if not correct_answer:
            await self.sio.emit("answer_response", {"status": "invalid_nation"}, to=sid)
            return

        nation_doc = get_nation_via_id(nation_id)
        if not nation_doc:
            await self.sio.emit(
                "answer_response", {"status": "invalid_nation"}, to=sid
            )
            return

        if nation_doc.get("captured"):
            await self.sio.emit(
                "answer_response", {"status": "already_captured"}, to=sid
            )
            return

        if not submitted_answer.strip().lower() == correct_answer.lower():
            await self.sio.emit("answer_response", {"status": "incorrect"}, to=sid)
            return

        capture_nation(nation_id, team_name)
        assign_team_points(team_name, DIFFICULTY_TO_POINTS[correct_answer["difficulty"]])

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

    async def get_nation_status(self, sid: str) -> None:
        nations = get_all_nations()
        process_tasks = [self._process_nation(nation) for nation in nations]

        captured_list = await gather(*process_tasks)
        await self.sio.emit("nation_status", captured_list, to=sid)
