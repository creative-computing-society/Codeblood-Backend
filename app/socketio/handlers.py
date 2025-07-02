
import json
from socketio import AsyncServer
from .socket_map import save_socket, remove_socket, get_all_sockets
from ..db.mongo import nations_col, teams_col
from datetime import datetime

# Load answers once at startup
with open("app/game/answers.json") as f:
    ANSWERS = {entry["nation_id"]: entry["answer"] for entry in json.load(f)}

def register_handlers(sio: AsyncServer):

    @sio.event
    async def connect(sid, environ, auth):
        session_id = auth.get("session_id")
        if not session_id:
            return False  
        save_socket(session_id, sid)
        print(f"[+] WebSocket connected: {sid} <- session: {session_id}")

    @sio.event
    async def disconnect(sid):
        remove_socket(sid)
        print(f"[-] WebSocket disconnected: {sid}")

    @sio.event
    async def submit_answer(sid, data):
        nation_id = data.get("nation_id")
        submitted_answer = data.get("answer")
        team_name = data.get("team_name")

        correct_answer = ANSWERS.get(nation_id)
        if not correct_answer:
            await sio.emit("answer_response", {"status": "invalid_nation"}, to=sid)
            return

        nation_doc = nations_col.find_one({"_id": nation_id})
        if nation_doc and nation_doc.get("captured"):
            await sio.emit("answer_response", {"status": "already_captured"}, to=sid)
            return

        if not submitted_answer.strip().lower() == correct_answer.lower():
            await sio.emit("answer_response", {"status": "incorrect"}, to=sid)
            return
        # Update nations collection
        nations_col.update_one(
            {"_id": nation_id},
            {"$set": {
                "captured": True,
                "captured_by": team_name,
                "timestamp": datetime.utcnow()
            }},
            upsert=True
        )

        # Update team points
        teams_col.update_one(
            {"_id": team_name},
            {"$inc": {"points": 100}},
            upsert=True
        )

        # Broadcast capture to all sockets
        await sio.emit("nation_captured", {
            "nation_id": nation_id,
            "captured_by": team_name
        })

        await sio.emit("answer_response", {"status": "correct"}, to=sid)

    @sio.event
    async def get_nation_status(sid):
        nations = await nations_col.find({})
        captured_list = [{
            "nation_id": n["_id"],
            "captured": n.get("captured", False),
            "captured_by": n.get("captured_by")
        } for n in nations]
        await sio.emit("nation_status", captured_list, to=sid)
