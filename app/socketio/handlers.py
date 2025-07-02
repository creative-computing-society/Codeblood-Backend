import json
from asyncio import gather
from os import path
from typing import Any, Dict, Optional
from datetime import datetime

from pymongo.collection import Collection
from socketio import AsyncServer

from .socket_map import save_socket, remove_socket
from ..db.mongo import nations_col, teams_col

ANSWER_JSON_FILE = path.join("app", "game", "answers.json")
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
        nations_col: Collection[Dict[str, Any]],
        teams_col: Collection[Dict[str, Any]],
    ):
        self.sio = sio
        self.nations_col = nations_col
        self.teams_col = teams_col
        self.ANSWERS = ANSWERS

        self.sio.on("connect", self.connect)
        self.sio.on("disconnect", self.disconnect)
        self.sio.on("submit_answer", self.submit_answer)
        self.sio.on("get_nation_status", self.get_nation_status)

    async def _process_nation(self, nation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "nation_id": nation["_id"],
            "captured": nation.get("captured", False),
            "captured_by": nation.get("captured_by"),
        }

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

    async def connect(
        self, sid: str, environ: Dict[str, Any], auth: Optional[Dict[str, Any]]
    ) -> Optional[bool]:
        session_id = auth.get("session_id") if auth else None
        if not session_id:
            return False

        save_socket(session_id, sid)
        print(f"[+] WebSocket connected: {sid} <- session: {session_id}")
        return None

    async def disconnect(self, sid: str) -> None:
        remove_socket(sid)
        print(f"[-] WebSocket disconnected: {sid}")

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

        nation_doc = self.nations_col.find_one({"_id": nation_id})
        if nation_doc and nation_doc.get("captured"):
            await self.sio.emit(
                "answer_response", {"status": "already_captured"}, to=sid
            )
            return

        if not submitted_answer.strip().lower() == correct_answer.lower():
            await self.sio.emit("answer_response", {"status": "incorrect"}, to=sid)
            return
        # Update nations collection
        nations_col.update_one(
            {"_id": nation_id},
            {
                "$set": {
                    "captured": True,
                    "captured_by": team_name,
                    "timestamp": datetime.now(),
                }
            },
            upsert=True,
        )

        # Update team points
        teams_col.update_one({"_id": team_name}, {"$inc": {"points": 100}}, upsert=True)

        # Broadcast capture to all sockets
        await self.sio.emit(
            "nation_captured", {"nation_id": nation_id, "captured_by": team_name}
        )

        await self.sio.emit("answer_response", {"status": "correct"}, to=sid)

    async def get_nation_status(self, sid: str) -> None:
        nations = self.nations_col.find({})
        process_tasks = [self._process_nation(nation) for nation in nations]

        captured_list = await gather(*process_tasks)
        await self.sio.emit("nation_status", captured_list, to=sid)
